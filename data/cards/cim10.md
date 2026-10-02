# Fiche de ressource : nomenclature CIM-10 FR (ATIH)

Statut au 02/10/2026 : P0-27 fait. Sert à dériver les niveaux chapitre, bloc et catégorie à 3 caractères des étiquettes PARHAF.

## Sources consultées (par un sous-agent de recherche, recoupé par mes mesures)

| Ressource | Accès | Remarque |
|---|---|---|
| ClaML 2019 de l'ATIH (`cim10fr2019_claml.zip`) | libre, https://www.atih.sante.fr/recueillir-les-donnees/guides-et-documentations/cim-10-fr-usage-pmsi-au-format-claml | **version utilisée** : 22 chapitres, 275 blocs, 11 623 catégories (recomptés par moi dans le fichier) |
| CIM-10 FR 2026 à usage PMSI (PDF, 1 011 pages) | libre, page ATIH du millésime 2026 | sert de recoupement ; extraction texte non vérifiée catégorie par catégorie |
| Terminologie CIM-10 FR 2025 du SMT (OWL, XML) | **bloquée** : compte affilié requis | non téléchargée |

L'annonce du SMT d'avril 2026 dit que des correctifs de hiérarchie « n'ont pas été reportés dans le fichier source CLAML de l'ATIH » : le ClaML 2019 est donc **imparfait**. Mesuré : une anomalie sur les catégories à 3 caractères (C85 rattaché à la catégorie C84 au lieu d'un bloc), traversée par `llmft.cim10` et signalée par `Claml.anomalies()`. Écarts rapportés par le sous-agent entre ClaML 2019 et PDF 2026 (6 codes : C83.1, C85, G41.0, T76, T78, U90 ; 5 codes U08.9 à U12.9 seulement dans le PDF) : non revérifiés par moi.

## Conditions de réutilisation (lues par le sous-agent aux mentions légales de l'ATIH)

« Les documents, fichiers et programmes, à l'exception de ceux indiqués comme payants, peuvent être téléchargés gratuitement sous réserve de : mentionner leur origine en cas d'utilisation ; ne pas les modifier ; ne pas en faire un usage commercial [...] » (https://www.atih.sante.fr/mentions-legales). La fiche SMT annonce la licence CC BY-NC-ND 3.0 IGO. Le fichier ClaML porte « Copyright WHO, ATIH 1994 - 2014 ». Les conditions de l'OMS ne sont pas lues.

**Conséquence adoptée** : on ne versionne ni ne redistribue **aucun fichier dérivé** de la nomenclature (pas de CSV de hiérarchie). Sont versionnés : cette fiche, les empreintes ci-dessous, le chargeur `src/llmft/cim10.py` et ses tests. Les fichiers sources restent dans `data/raw/cim10/` (ignoré par Git). Mention d'origine à reprendre dans toute sortie : « ATIH, CIM-10 FR à usage PMSI, ClaML 2019 ». Une publication publique du dépôt exigerait d'écrire à l'ATIH (nomenclatures-de-sante@atih.sante.fr) : **décision à Cyril**.

La preuve prévue en P0-27 (« fichier versionné ») est remplacée par : empreintes, chargeur et tests, pour la raison ci-dessus.

## Empreintes SHA-256 des fichiers sources

| Fichier | SHA-256 |
|---|---|
| `cim10fr2019.xml` | `b835685f4d1359b2f9de41773de254560508ae7351fecfb32836d50eba4e2775` |
| `cim10fr2019_claml.zip` | `a6078fff07e76abf5d319a9643dd2a411d65c47ce2a37b22af492b011d0d9c81` |
| `cim10fr2026.pdf` | `819a1b8480f073f81c9cb15e147dd977a5ebe6b60f19cae6ade78510eb73ea40` |

## Pièges de la nomenclature

- La lettre **D** couvre les chapitres II (D00-D48) et III (D50-D89), et **H** les chapitres VII et VIII : un chapitre ne se déduit pas de la première lettre, mais de la catégorie à 3 caractères. Le test `test_letter_d_is_split_across_chapters_by_range_not_by_letter` le verrouille.
- Les codes PARHAF contiennent des extensions françaises (5 caractères) et des suffixes `+n` : seuls les trois premiers caractères sont utilisés.
- Un code PARHAF (`N571`, patient GYNECOLOGIE-00116, libellé « Abcès de la glande de Bartholin », qui correspond à N75.1) n'existe ni dans le ClaML 2019 ni dans le PDF 2026 : **erreur de saisie probable**, patient mis en quarantaine, non corrigé.
