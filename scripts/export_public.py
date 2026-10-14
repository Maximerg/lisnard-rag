#!/usr/bin/env python3
"""Reconstruit le dépôt open data public depuis la base privée (/workspace/lisnard-kb).
N'exporte que des contenus publics : aucune donnée du bot (x/), aucun secret, aucune mention ni donnée personnelle."""
import unicodedata, csv, glob, hashlib, html, json, os, re, shutil, sys
SRC = os.environ.get("LISNARD_KB", "/workspace/lisnard-kb")
OUT = os.environ.get("LISNARD_PUBLIC", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
X_ACCOUNTS = {"103918784": "davidlisnard"}  # complété par les noms de fichiers ne_* -> nouv_energie
def wipe(p):
    if os.path.exists(p): shutil.rmtree(p)
    os.makedirs(p)
def precision(d):
    if not d or not re.match(r"\d{4}", d): return None, None
    if re.match(r"\d{4}-\d\d-\d\d", d): return d[:10], "day"
    return d[:4], "year"
def speaker(st):
    s = st.lower()
    if "x @davidlisnard" in s or s.startswith("citation") or "tribune" in s or "youtube @david_lisnard" in s and "transcription" not in s: return "David Lisnard"
    if "transcription" in s: return "David Lisnard (intervenants non distingués)"
    if "programme" in s: return "Nouvelle Énergie (programme)"
    return "Nouvelle Énergie"
def title(r):
    m = re.search(r"«\s*(.+?)\s*»", r.get("claim") or "")
    if m: return m.group(1)[:200]
    m = re.match(r"Programme \((.*?)\)", r.get("claim") or "")
    return ("Programme — " + m.group(1)) if m else (r.get("claim") or "")[:120]
def kb():
    rows = []
    for l in open(f"{SRC}/kb.jsonl"):
        r = json.loads(l); d, p = precision(r.get("date"))
        if r.get("auto_transcription") or "transcription" in (r.get("source_type") or ""): auto = True
        else: auto = False
        rows.append({"id": hashlib.sha1((r.get("source_url", "") + (r.get("claim") or "") + (r.get("quote") or "")).encode()).hexdigest()[:16],
                     "claim": r.get("claim"), "quote": r.get("quote"), "speaker": speaker(r.get("source_type") or ""),
                     "source_type": r.get("source_type"), "source_title": title(r), "source_url": r.get("source_url"),
                     "date": d if p == "day" else (d if p == "year" else None), "date_precision": p, "theme": r.get("theme") or [],
                     "is_auto_transcript": auto, **({"note": "transcription automatique non vérifiée"} if auto else {})})
    return rows
def vtt_text(path):
    out, last = [], None
    for blk in open(path, encoding="utf-8", errors="ignore").read().split("\n\n"):
        ls = blk.strip().split("\n")
        if not ls or "-->" not in ls[0]: continue
        t = ls[0][:8]; txt = " ".join(re.sub(r"<[^>]+>", "", x).strip() for x in ls[1:]).strip()
        if txt and txt != last and not (last and txt in last): out.append((t, txt)); last = txt
    paras, cur, mark = [], [], None
    for t, x in out:
        if mark is None: mark = t
        cur.append(x)
        if len(" ".join(cur)) > 700: paras.append(f"[{mark}] " + " ".join(cur)); cur, mark = [], None
    if cur: paras.append(f"[{mark}] " + " ".join(cur))
    return "\n\n".join(paras)
def media(src, dst, kind):
    os.makedirs(dst, exist_ok=True); n = 0
    for info in glob.glob(f"{src}/**/*.info.json", recursive=True):
        j = json.load(open(info)); vid = j.get("id")
        if j.get("_type") == "playlist" or not vid: continue
        vtts = sorted(glob.glob(info.replace(".info.json", "*.vtt")), key=lambda p: ("orig" in p, p))
        if not vtts: continue
        body = vtt_text(vtts[0])
        if len(body) < 80: continue
        d = j.get("upload_date"); d = f"{d[:4]}-{d[4:6]}-{d[6:]}" if d else "date inconnue"
        ch = j.get("channel") or j.get("uploader") or ""
        hdr = (f"# {j.get('title') or j.get('description', '')[:100]}\n\n- Source : {j.get('webpage_url')}\n- Chaîne/compte : {ch}\n- Date de publication : {d}\n"
               f"- Transcription : automatique, **non vérifiée**. Les questions des journalistes et les autres intervenants ne sont pas séparés des propos de David Lisnard.\n\n")
        open(f"{dst}/{d}_{vid}.md", "w").write(hdr + body + "\n"); n += 1
    return n
def programme(dst):
    from bs4 import BeautifulSoup
    os.makedirs(dst, exist_ok=True); n = 0
    for l in open(f"{SRC}/raw/urlmap.tsv"):
        fn, u = l.rstrip("\n").split("\t")
        if "/notre-programme" not in u or not os.path.exists(f"{SRC}/{fn}"): continue
        s = BeautifulSoup(open(f"{SRC}/{fn}", encoding="utf-8", errors="ignore").read(), "html.parser")
        m = s.find("main") or s.body
        for x in m(["script", "style", "nav", "footer", "form", "header"]): x.decompose()
        txt = re.sub(r"\n{3,}", "\n\n", m.get_text("\n", strip=True))
        slug = u.rstrip("/").split("/")[-1]
        open(f"{dst}/{slug}.md", "w").write(f"# Programme Nouvelle Énergie — {slug}\n\n- Source : {u}\n- Date : non datée (page de programme mise à jour en continu)\n\n{txt}\n"); n += 1
    return n
def xposts(dst):
    os.makedirs(dst, exist_ok=True); seen = {}
    for f in glob.glob(f"{SRC}/raw/x/*.json") + glob.glob(f"{SRC}/raw/x_page*.json"):
        acct = "nouv_energie" if os.path.basename(f).startswith("ne_") else "davidlisnard"
        for t in json.load(open(f)).get("data", []):
            if t.get("author_id") not in ("103918784",) and acct == "davidlisnard" and t.get("author_id"): pass
            txt = (t.get("note_tweet") or {}).get("text") or t.get("text")
            seen[t["id"]] = {"id": t["id"], "account": acct, "date": (t.get("created_at") or "")[:10] or None, "text": txt, "url": f"https://x.com/{acct}/status/{t['id']}"}
    for acct in ("davidlisnard", "nouv_energie"):
        rows = sorted((r for r in seen.values() if r["account"] == acct), key=lambda r: r["date"] or "", reverse=True)
        with open(f"{dst}/{acct}.jsonl", "w") as fh: fh.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    return len(seen)
def main():
    for d in ("data", "raw"): wipe(f"{OUT}/{d}")
    rows = kb()
    with open(f"{OUT}/data/kb.jsonl", "w") as f: f.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    cols = ["id", "claim", "quote", "speaker", "source_type", "source_title", "source_url", "date", "date_precision", "theme", "is_auto_transcript"]
    with open(f"{OUT}/data/kb.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(cols)
        for r in rows: w.writerow([";".join(r[c]) if c == "theme" else r[c] for c in cols])
    os.makedirs(f"{OUT}/data/themes"); th = {}
    for r in rows:
        for t in r["theme"] or ["divers"]: th.setdefault(re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()).strip("-"), []).append(r)
    for t, rs in th.items(): open(f"{OUT}/data/themes/{t}.jsonl", "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rs))
    stats = {"entries": len(rows), "themes": len(th), "programme_pages": programme(f"{OUT}/raw/programme"), "x_posts": xposts(f"{OUT}/raw/x"),
             "youtube_transcripts": media(f"{SRC}/raw/youtube", f"{OUT}/raw/youtube", "youtube"), "tiktok_transcripts": media(f"{SRC}/raw/tiktok", f"{OUT}/raw/tiktok", "tiktok")}
    json.dump(stats, open(f"{OUT}/data/stats.json", "w"), indent=1); print(stats); return stats
if __name__ == "__main__": main()
