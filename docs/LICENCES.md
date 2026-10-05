# Licences des dépendances et dépôts consultés (P0-12)

Audit du 01/10/2026. **Dépendances installées** : licence lue dans les métadonnées du paquet installé (`.venv`). **Dépôts non installés** : licence lue par l'API publique de GitHub (`/repos/<dépôt>/license`) ou, quand elle répond « NOASSERTION », dans le fichier `LICENSE`. Les licences de **modèles** et de **jeux de données** se trouvent dans leurs fiches (`data/cards/`, `BOITE_A_OUTILS.md`) et se relisent à la source en P0-06 et RM-13.

Règle du projet : un dépôt sans licence (tous droits réservés) se lit et se réimplémente, il ne se copie pas.

## Installées (verrouillées dans `uv.lock`)

| Paquet | Version | Licence | Usage | Compatibilité |
|---|---|---|---|---|
| torch | 2.11.0+cu128 | BSD-3-Clause | calcul | libre |
| transformers | 5.18.0 | Apache-2.0 | modèles | libre |
| peft | 0.21.2 | Apache-2.0 | LoRA | libre |
| trl | 1.14.1 | Apache-2.0 | entraînement, distillation | libre |
| accelerate | 1.15.0 | Apache-2.0 | entraînement | libre |
| bitsandbytes | 0.50.2 | MIT | quantification | libre |
| datasets | 5.0.1 | Apache-2.0 | données | libre |
| huggingface_hub | 1.33.0 | Apache-2.0 | téléchargement | libre |
| numpy, pandas, pyarrow, scipy, scikit-learn, statsmodels | 2.5.3, 3.0.6, 25.0.1, 1.18.1, 1.9.1, 0.15.0 | BSD ou Apache-2.0 | analyse | libre |
| pydantic, pyyaml | 2.13.5, 6.0.3 | MIT | contrats, profils | libre |
| pytest, ruff, mypy | 9.1.1, 0.16.10, 2.4.0 | MIT | outillage de développement | libre |

## Dépôts non installés

| Dépôt | Licence trouvée | Usage prévu | Décision |
|---|---|---|---|
| scikit-learn-contrib/MAPIE | BSD-3-Clause | prédiction conforme (RM-22) | utilisable |
| cleanlab/cleanlab | Apache-2.0 | audit d'étiquettes (P0-31) | utilisable ; **corrige `BOITE_A_OUTILS.md`, qui annonçait MIT** |
| aphp/edsnlp | BSD-3-Clause | extraction, réutilisation de l'écosystème AP-HP | utilisable |
| ml-stat-Sustech/TorchCP | **LGPL-3.0** | vérification croisée seulement (RM-22) | pas de copie de code dans le dépôt ; usage en dépendance libre, redistribution à examiner |
| linkedin/Liger-Kernel | BSD-2-Clause | noyaux d'entraînement (option) | utilisable |
| unslothai/unsloth | Apache-2.0 | option d'entraînement | utilisable |
| gradio-app/trackio | MIT | suivi d'expériences | utilisable |
| vllm-project/llm-compressor | Apache-2.0 | quantification (hors chemin critique) | utilisable |
| vllm-project/vllm | Apache-2.0 | service (hors chemin critique) | utilisable |
| ModelCloud/GPTQModel | Apache-2.0 d'après l'en-tête SPDX de `LICENSE` (l'API répond NOASSERTION) | quantification (hors chemin critique) | utilisable ; relire le fichier complet avant tout usage |
| EleutherAI/lm-evaluation-harness | MIT | évaluation de référence | utilisable |
| jongwooko/distillm-2 | **aucune licence** | lecture de la recette de distillation | **lecture seule, réimplémentation** |
| shyoulala/LMSYS_BlackPearl | **aucune licence** | lecture de la recette 1re place LMSYS | **lecture seule, réimplémentation** |
| Lizhecheng02/Kaggle-Multilingual_Chatbot_Arena | **aucune licence** | lecture de la recette 5e place | **lecture seule, réimplémentation** |

Non vérifiés à ce jour : Hydra, Optuna, DVC, distilabel, xgrammar, llguidance, outlines, client Elasticsearch (aucun n'est installé ni requis avant leur étape).

## Modèles utilisés (audit GLM v3, C8-A9 ; lus dans l'API publique de Hugging Face le 03/10/2026)

| Modèle | Licence | Usage | Compatibilité |
|---|---|---|---|
| Qwen/Qwen3.5-4B, Qwen/Qwen3.5-9B | Apache-2.0 | élèves LoRA | libre |
| google/gemma-4-E4B-it, google/gemma-4-31B-it | Apache-2.0 | élève et professeur | libre |
| almanach/camembert-bio-base | MIT | encodeur de référence | libre |
| google/medgemma-4b-it | non lue (accès conditionné ; Q6 : conditions non acceptées) | non utilisé | exclu du chemin court |

Les licences se relisent à chaque nouveau modèle ajouté au chemin court.

## MorFITT (05/10/2026)
Données : CC BY-SA 4.0 ; code du dépôt d'origine : Apache-2.0 ; source lue : dépôt GitHub `qanastek/MORFITT` ; usage : ancrage externe (RM-49), copie locale non redistribuée. Fiche : `docs/FICHE_DE_DONNEES_MORFITT.md`.
