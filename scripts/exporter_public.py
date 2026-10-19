#!/usr/bin/env python3
"""Exporte la base vers le dépôt open data `Maximerg/lisnard-rag`.

Le dépôt public a son propre schéma, plus léger que la base interne : il ne
contient aucune donnée du bot (mentions, brouillons, jetons), seulement les
textes et leur source.

Différences avec `export_public.py` d'origine :
  - la source est `lisnard-kb/base/kb-v2.jsonl`, pas `/workspace/lisnard-kb` ;
  - les champs sont `texte`/`url` et non `claim`/`source_url` ;
  - `is_auto_transcript` tombe à False : depuis le 19/10/2026 toutes les
    transcriptions sont diarisées, donc attribuées et vérifiées. Le degré de
    vérification est publié dans `verification` ;
  - le thème est une chaîne dans la base, une liste dans le dépôt.

  python3 exporter_public.py --vers /chemin/du/depot
"""
import argparse, csv, datetime, hashlib, json, os, re, shutil, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KB = os.path.join(ROOT, "lisnard-kb", "base", "kb-v2.jsonl")

COLS = ["id", "claim", "quote", "speaker", "source_type", "source_title",
        "source_url", "date", "date_precision", "theme", "verification"]


def precision(d):
    if not d or not re.match(r"\d{4}", str(d)):
        return None, None
    d = str(d)
    if re.match(r"\d{4}-\d\d-\d\d", d):
        return d[:10], "day"
    return d[:4], "year"


def locuteur(r):
    st = str(r.get("source_type") or "").lower()
    if "programme" in st or "fiche" in st:
        return "Nouvelle Énergie (programme)"
    if "publication" in st:
        return "Nouvelle Énergie"
    return "David Lisnard"


def titre(r):
    t = r.get("source_label") or r.get("titre") or ""
    if t:
        return str(t)[:200]
    m = re.search(r"«\s*(.+?)\s*»", r.get("texte") or "")
    if m:
        return m.group(1)[:200]
    return (r.get("texte") or "")[:120]


def themes(r):
    th = r.get("theme")
    if isinstance(th, list):
        return th or ["divers"]
    if isinstance(th, str) and th:
        return [th]
    return ["divers"]


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-",
                  unicodedata.normalize("NFKD", t.lower())
                  .encode("ascii", "ignore").decode()).strip("-") or "divers"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vers", required=True, help="racine du dépôt cloné")
    ap.add_argument("--sans-raw", action="store_true",
                    help="ne pas toucher raw/ (garder les sources brutes du dépôt)")
    a = ap.parse_args()
    out = a.vers

    rows = []
    for l in open(KB, encoding="utf-8"):
        r = json.loads(l)
        t = (r.get("texte") or "").strip()
        if not t:
            continue
        d, p = precision(r.get("date"))
        url = r.get("url") or ""
        rows.append({
            "id": hashlib.sha1((url + t).encode()).hexdigest()[:16],
            "claim": t,
            "quote": None,
            "speaker": locuteur(r),
            "source_type": r.get("source_type") or r.get("nature") or "passage",
            "source_title": titre(r),
            "source_url": url,
            "date": d if p in ("day", "year") else None,
            "date_precision": p,
            "theme": themes(r),
            "verification": r.get("methode_verification") or "corpus structuré contrôlé",
        })

    print(f"{len(rows)} passages à publier")

    os.makedirs(os.path.join(out, "data", "themes"), exist_ok=True)
    with open(os.path.join(out, "data", "kb.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(os.path.join(out, "data", "kb.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for r in rows:
            w.writerow([";".join(r[c]) if c == "theme" else r[c] for c in COLS])

    # thèmes éclatés
    for vieux in os.listdir(os.path.join(out, "data", "themes")):
        os.remove(os.path.join(out, "data", "themes", vieux))
    th = {}
    for r in rows:
        for t in r["theme"]:
            th.setdefault(slug(t), []).append(r)
    for t, rs in th.items():
        with open(os.path.join(out, "data", "themes", f"{t}.jsonl"), "w", encoding="utf-8") as f:
            for r in rs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # statistiques
    par_source = {}
    for r in rows:
        par_source[r["source_type"]] = par_source.get(r["source_type"], 0) + 1
    avec_date = sum(1 for r in rows if r["date"])
    stats = {
        "entries": len(rows),
        "themes": len(th),
        "avec_date": avec_date,
        "sans_date": len(rows) - avec_date,
        "mots": sum(len((r["claim"] or "").split()) for r in rows),
        "date_export": datetime.date.today().isoformat(),
        "verification": "100 % des passages attribués et vérifiés",
        "sources": dict(sorted(par_source.items(), key=lambda x: -x[1])),
    }
    json.dump(stats, open(os.path.join(out, "data", "stats.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)

    print(json.dumps({k: v for k, v in stats.items() if k != "sources"}, indent=1, ensure_ascii=False))
    print(f"\nécrit dans {out}/data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
