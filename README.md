# Base de connaissances David Lisnard (open data, non officielle)

Ce dépôt rassemble les positions publiques de David Lisnard et de Nouvelle Énergie, avec leur source et leur date. Il est prévu pour la recherche, le fact-checking et les systèmes RAG (recherche + génération).

**Non officiel.** Ce projet n'est affilié ni à David Lisnard ni à Nouvelle Énergie. Les textes appartiennent à leurs auteurs. Ici, ils sont seulement référencés et cités, avec un lien vers chaque source.

## Sources
- Programme officiel sur unenouvelleenergie.fr (`raw/programme/`), ainsi que les articles, tribunes et pages « Questions » du site.
- Posts X de @davidlisnard et @nouv_energie (`raw/x/`).
- Vidéos YouTube : la chaîne officielle et des interviews dans les médias (`raw/youtube/`), plus les vidéos TikTok (`raw/tiktok/`).

Les transcriptions sont **automatiques et non vérifiées**. Les questions des journalistes et les autres intervenants ne sont pas séparés des propos de David Lisnard : vérifiez toujours sur la vidéo d'origine, à partir du minutage `[hh:mm:ss]`.

## Méthode de datation
- `date` : date de **publication** de la source (post, vidéo, article), au format ISO `AAAA-MM-JJ`.
- `date_precision` : `day`, `year` (année seule connue) ou `null`.
- Les pages du programme sont mises à jour en continu et n'ont **pas de date** (`null`). La date de collecte n'est jamais utilisée comme date de publication. Toute date située dans le futur est rejetée.
- Pour un RAG, privilégiez les positions les plus récentes : elles peuvent évoluer.

## Schéma (`data/kb.jsonl`, `data/kb.csv`, `data/themes/*.jsonl`)
| Champ | Description |
|---|---|
| `id` | identifiant stable (hash) |
| `claim` | résumé ou intitulé de la position |
| `quote` | texte verbatim de la source, s'il existe |
| `speaker` | David Lisnard, Nouvelle Énergie, ou « intervenants non distingués » |
| `source_type` | type de source (programme, X, YouTube, citation dans un média…) |
| `source_title` | titre de la source |
| `source_url` | lien vers l'original |
| `date` / `date_precision` | voir ci-dessus |
| `theme` | liste de thèmes |
| `is_auto_transcript` | `true` pour une transcription automatique non vérifiée |

## Utilisation dans un RAG
```python
import json, datetime as dt
kb = [json.loads(l) for l in open("data/kb.jsonl", encoding="utf-8")]
def search(q, k=5):
    words = set(q.lower().split())
    def score(e):
        text = f"{e['claim']} {e.get('quote') or ''}".lower()
        hits = sum(w in text for w in words)
        age = (dt.date.today() - dt.date.fromisoformat(e["date"])).days / 365 if e["date_precision"] == "day" else 2
        return hits * 0.5 ** age          # pertinence × fraîcheur
    return sorted(kb, key=score, reverse=True)[:k]
for e in search("carte scolaire école"):
    print(e["date"], e["source_url"], e["claim"][:100])
```
Avec un modèle de langage, citez toujours `source_url` et `date`, et signalez `is_auto_transcript`.

## Mise à jour
Le dépôt est régénéré chaque jour par `scripts/export_public.py`, à partir d'une collecte des sources publiques.

## Retrait sur demande
Vous êtes ayant droit ou concerné par un contenu ? Ouvrez une *issue* sur ce dépôt ou contactez le mainteneur via github.com/Maximerg : le contenu sera retiré rapidement.

## Licences
- Données (`data/`, `raw/`) : **CC BY 4.0** (`LICENSE-DATA`). Les droits sur les textes cités restent à leurs auteurs.
- Scripts (`scripts/`) : **MIT** (`LICENSE`).

---
## English
Unofficial open dataset of David Lisnard's and Nouvelle Énergie's public positions (French politics, 2027 presidential election). Each entry has its source URL and its publication date. Programme pages are undated, and crawl dates are never used as publication dates. Transcripts are automatic and unverified. See the schema above. Data is under CC BY 4.0 and code under MIT. Takedown requests: open an issue.
