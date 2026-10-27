# Journal des versions

Ce qui change dans le dépôt, mise à jour par mise à jour. Les comptes sont ceux de `data/kb.jsonl`.

## 2026-10-27

**3586 passages, 26 thèmes.**

Ajouté : **1** passage(s).

- 1 · X @davidlisnard

## 2026-10-25

**3585 passages, 26 thèmes.**

Ajouté : **29** passage(s).

- 29 · YouTube

## 2026-10-25

**3556 passages, 26 thèmes.**

Aucun changement de contenu : seuls les fichiers dérivés (statistiques, vision) ont été régénérés.

## 2026-10-24

**3556 passages, 26 thèmes.**

Ajouté : **39** passage(s).

- 39 · site Nouvelle Énergie

## 2026-10-23

**3517 passages, 25 thèmes.**

Ajouté : **7** passage(s).

- 5 · site Nouvelle Énergie
- 2 · X @davidlisnard

## 2026-10-22

**3510 passages, 25 thèmes.**

Aucun changement de contenu : seuls les fichiers dérivés (statistiques, vision) ont été régénérés.

## 2026-10-21

**3510 passages, 25 thèmes.**

Aucun changement de contenu : seuls les fichiers dérivés (statistiques, vision) ont été régénérés.

## 2026-10-21

**3510 passages, 25 thèmes.**

Ajouté : **5** passage(s).

- 5 · site Nouvelle Énergie

## 2026-10-20

**3 505 passages, 25 thèmes, 579 973 mots.**

Ajouté
- `data/vision.md` — la synthèse du projet en 20 sections, 34 000 caractères. C'est le document qui sert de contexte à un modèle de langage.
- `data/schema.json` — description formelle des 11 champs, avec types et signification.
- `CHANGELOG.md` — ce fichier.
- Statistiques par année et par thème dans `data/stats.json`.

Corrigé
- **Thèmes normalisés.** La base avait été construite par vagues, chacune avec sa convention : `securite` et `sécurité`, `education` et `éducation`, `sante` et `santé`, `numerique-ia` et `numérique/IA/science`. Un filtre sur une seule graphie ratait des passages. 216 valeurs corrigées, 37 thèmes ramenés à 25.
- **42 passages sans source** (articles du site) reçoivent `Site Nouvelle Énergie`.
- **98 passages dont l'URL pointait sur un PDF** sont rattachés au site qui publie le document : `Site Nouvelle Énergie : Le Livre noir`, `Carnets : Santé`, `Carnets : Agriculture`. L'URL du fichier est conservée dans `url_pdf`, mais ce n'est plus elle qui est citée : un PDF d'images n'est pas vérifiable.

## 2026-10-19

**3 504 passages, 33 thèmes.**

Ajouté
- Instagram : 272 passages issus des comptes officiels, parole directe ou citation attribuée.
- Champ `verification` sur chaque entrée, qui dit comment le texte a été attribué.

Retiré
- Facebook, TikTok et LinkedIn : aucune API ne permet d'y vérifier qu'un texte provient bien de David Lisnard.
- `raw/tiktok/` et `raw/youtube/` : 18 et 57 fichiers de transcriptions automatiques non vérifiées, avec des doublons. Ils contredisaient la promesse du dépôt.

Corrigé
- Le README annonçait « transcriptions automatiques et non vérifiées ». Ce n'est plus vrai : les vidéos et podcasts sont diarisés, donc la voix est identifiée. Le README explique maintenant les quatre méthodes de vérification.

## 2026-10-15

**Version initiale. 4 610 passages, 15 thèmes.**

Première publication : programme officiel, articles du site, tribunes de presse, posts X, transcriptions YouTube et TikTok. Le corpus contenait alors des transcriptions automatiques non vérifiées et des passages de récit à la troisième personne, retirés depuis.

---

## Comment lire ces chiffres

Le nombre de passages **baisse** parfois d'une version à l'autre. Ce n'est pas une perte de contenu : c'est le retrait de passages qui ne portaient pas sa parole (récit de journaliste, transcriptions non vérifiées, plateformes invérifiables). Un corpus plus petit et entièrement attribuable vaut mieux qu'un corpus plus gros où l'on ne sait pas qui parle.
