# Base de connaissances David Lisnard (open data, non officielle)

Ce dépôt rassemble les positions publiques de David Lisnard et de Nouvelle Énergie, avec leur source et leur date. Il est prévu pour la recherche, le fact-checking et les systèmes RAG (recherche + génération).

**Non officiel.** Ce projet n'est affilié ni à David Lisnard ni à Nouvelle Énergie. Les textes appartiennent à leurs auteurs. Ici, ils sont seulement référencés et cités, avec un lien vers chaque source.

## Ce que contient le corpus

**3 505 passages, 580 000 mots, tous attribués et sourcés.** Chaque entrée renvoie à son origine vérifiable.

| Famille | Passages | Vérification |
|---|---|---|
| Vidéos et podcasts diarisés | 1 114 | diarisation : la voix de David Lisnard est identifiée par locuteur |
| Articles du site | 451 | texte recoupé sur la page citée |
| Programme officiel | 396 | texte officiel de Nouvelle Énergie |
| Posts X | 630 | API X, authentique par construction |
| Tribunes de presse | 344 | tribune signée, média et date de parution |
| Instagram | 272 | compte officiel, parole directe ou citation attribuée |
| Fiches « Questions » | 163 | réponses officielles du site |
| Livre *Ainsi va la France* | 64 | ouvrage signé |

## Sources

- **Site unenouvelleenergie.fr** : programme officiel, articles, tribunes, pages « Questions ». C'est la seule source de textes du corpus — le site agrège déjà les interviews de presse.
- **Posts X** de @davidlisnard.
- **Instagram** de David Lisnard, via le dépôt officiel du parti.
- **Vidéos et podcasts** : chaîne YouTube officielle et émissions (Thinkerview, Grand Angle, Sud Radio, Bourdin, franceInfo, CNEWS, BFMTV, Europe 1, RTL…).

**Écartés volontairement** : Facebook, TikTok et LinkedIn. Ces plateformes n'offrent aucun moyen de vérifier qu'un texte provient bien de lui ; rien n'y est publié ici.

## Comment le contenu est vérifié

Le corpus ne contient que de la parole attribuée à David Lisnard, jamais de récit à la troisième personne ni de commentaire de journaliste.

- **Articles et fiches** : le texte est retrouvé mot pour mot sur la page citée, puis filtré — première personne ou passage entre guillemets. Le récit est écarté.
- **Vidéos et podcasts** : les voix sont séparées (diarisation ElevenLabs), puis l'orateur est identifié. Les propos des journalistes et des autres invités ne sont pas conservés. Une transcription automatique peut comporter des erreurs de mots, mais **l'attribution, elle, est vérifiée**.
- **Posts X et Instagram** : le texte vient directement de la plateforme, sans intermédiaire.

Le champ `verification` de chaque entrée indique laquelle de ces méthodes s'applique.

## Méthode de datation

- `date` : date de **publication** de la source (post, vidéo, article), au format ISO `AAAA-MM-JJ`.
- `date_precision` : `day`, `year` (année seule connue) ou `null`.
- Les pages du programme sont mises à jour en continu et n'ont **pas de date** (`null`). La date de collecte n'est jamais utilisée comme date de publication.
- Pour un RAG, privilégiez les positions les plus récentes : elles peuvent évoluer.

## Schéma (`data/kb.jsonl`, `data/kb.csv`, `data/themes/*.jsonl`)

| Champ | Description |
|---|---|
| `id` | identifiant stable (hash de l'URL et du texte) |
| `claim` | le passage, dans son texte |
| `quote` | citation verbatim, quand la source en distingue une |
| `speaker` | David Lisnard, ou Nouvelle Énergie pour le programme |
| `source_type` | type de source (programme, X, Instagram, diarisation, tribune…) |
| `source_title` | titre de la source |
| `source_url` | lien vers l'original |
| `date` / `date_precision` | voir ci-dessus |
| `theme` | liste de thèmes (33 thèmes) |
| `verification` | méthode d'attribution et de vérification |

## Utilisation dans un RAG

```python
import json, datetime as dt

kb = [json.loads(l) for l in open("data/kb.jsonl", encoding="utf-8")]

def search(q, k=5):
    words = set(q.lower().split())
    def score(e):
        text = f"{e['claim']} {e.get('quote') or ''}".lower()
        hits = sum(w in text for w in words)
        age = (dt.date.today() - dt.date.fromisoformat(e["date"])).days / 365 \
              if e["date_precision"] == "day" else 2
        return hits * 0.5 ** age          # pertinence × fraîcheur
    return sorted(kb, key=score, reverse=True)[:k]

for e in search("carte scolaire école"):
    print(e["date"], e["source_url"], e["claim"][:100])
```

Avec un modèle de langage, citez toujours `source_url` et `date`. Pour une citation exacte à partir d'une vidéo, vérifiez sur l'original : la transcription est automatique.

## Mise à jour

Le dépôt est régénéré par `scripts/exporter_public.py`, à partir d'une veille quotidienne des sources publiques : nouveaux articles, fiches, tribunes, posts X, Instagram, vidéos et podcasts.

## Retrait sur demande

Vous êtes ayant droit ou concerné par un contenu ? Ouvrez une *issue* sur ce dépôt ou contactez le mainteneur via github.com/Maximerg : le contenu sera retiré rapidement.

## Licences

- Données (`data/`, `raw/`) : **CC BY 4.0** (`LICENSE-DATA`). Les droits sur les textes cités restent à leurs auteurs.
- Scripts (`scripts/`) : **MIT** (`LICENSE`).

---

## English

Unofficial open dataset of David Lisnard's and Nouvelle Énergie's public positions (French politics, 2027 presidential election). **3,505 passages, 580,000 words**, each with its source URL, publication date and verification method.

Only attributed speech is included — never third-person reporting or journalists' commentary. Articles are matched word-for-word against the cited page; videos and podcasts are speaker-diarised so that only David Lisnard's own words are kept. Facebook, TikTok and LinkedIn are deliberately excluded: no way to verify authorship.

Programme pages are undated, and crawl dates are never used as publication dates. Data is under CC BY 4.0 and code under MIT. Takedown requests: open an issue.
