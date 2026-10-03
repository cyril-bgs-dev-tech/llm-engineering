# Wiki Log

Append-only fallback log (this wiki is not a git repo yet). Format:
`## [YYYY-MM-DD] <operation> | <title>` — recent: `grep "^## \[" log.md | tail -10`

---

## [2026-10-01] init | Fine-tuning de LLM sur textes cliniques français

## [2026-10-01] ingest | Environnement Blackwell (spikes P0-04 et P0-05)
Pages créées : env-blackwell. Sources : raw/spike-p0-04-torch-blackwell.json, raw/spike-p0-05-lora-nf4.json (sorties des scripts `scripts/spikes/`, runs enregistrés dans `results/runs/`).

## [2026-10-01] update | env-blackwell
Reason: ajout de la section RM-06 (RAM visible 68,7 Gio contre 96 annoncés, débits ext4 et /mnt/d, disque libre) ; CLAUDE.md et AGENTS.md corrigés en conséquence.
Source: raw/rm06-machine-wsl.json

## [2026-10-01] ingest | Règles de formulation (P0-20)
Pages créées : regles-de-formulation. Source : raw/parhaf-readme-60426cc.md (copie de la fiche du jeu à la révision 60426cc).

## [2026-10-02] update | overview
Reason: première synthèse mesurée (pile Blackwell, contraintes disque et RAM, règles de formulation) ; les deux pages existantes ne sont plus orphelines.
Source: raw/spike-p0-04-torch-blackwell.json, raw/rm06-machine-wsl.json, raw/parhaf-readme-60426cc.md

## [2026-10-02] ingest | Lot A, papiers A4 à A6 (P0-47)
Pages créées : parhaf-corpus-paper, learning-rate-matters, causal-llm-classification-heads, reglage-taux-apprentissage-lora. Pages mises à jour : regles-de-formulation (lien vers l'article PARHAF). Sources : raw/arxiv-2603.20494.txt, raw/arxiv-2602.04998.txt, raw/arxiv-2512.12677.txt (texte extrait des PDF arXiv par pypdf, citations vérifiées mot pour mot par script).

## [2026-10-02] update | overview
Reason: les trois papiers du Lot A (A4, A5, A6) sont ingérés ; la vue d'ensemble ne dit plus « aucune source ingérée » et les relie.
Source: wiki/pages/parhaf-corpus-paper.md, wiki/pages/learning-rate-matters.md, wiki/pages/causal-llm-classification-heads.md

## [2026-10-02] create | compatibilite-modeles-p0-06
Reason: tableau de compatibilité de classification des cinq modèles testés (P0-06) et banc du plus gros professeur en QLoRA 4 bits (P0-08) ; limites dites (padding non exercé, qualité non mesurée, MedGemma exclu).
Source: raw/spike-p0-06-qwen3-5-4b.json, raw/spike-p0-06-qwen3-5-9b.json, raw/spike-p0-06-gemma-4-e4b.json, raw/spike-p0-06-qwen3-8-27b.json, raw/spike-p0-06-gemma-4-31b.json

## [2026-10-02] ingest | Lot A, A7 (arXiv 2411.08870) et A1 (README du dépôt du 1er LMSYS), RM-18 partiel
Pages créées : limited-impact-medical-adaptation, lmsys-first-place-distillation-readme. Pages mises à jour : overview. Sources : raw/arxiv-2411.08870.txt (texte extrait du PDF par pypdf), raw/lmsys-blackpearl-readme.md (README du dépôt GitHub). A2 et A3 non ingérés : pages Kaggle illisibles hors navigateur ; texte à fournir par Cyril (Q10).

## [2026-10-02] ingest | Lot A, A8 TRIPOD-LLM (RM-23)
Pages créées : tripod-llm-reporting-guideline. Pages mises à jour : overview, compatibilite-modeles-p0-06, reglage-taux-apprentissage-lora (liens). Source : raw/pmc-12104976-tripod-llm.txt (texte extrait de la page PMC du manuscrit d'auteur). Licence de réutilisation non vérifiée, liste des items résumée et non recopiée.

## [2026-10-03] create | protocole-gele-2026-10-03
Reason: témoin daté du gel de PROTOCOLE.md (P0-46) : neuf instantanés et leurs empreintes SHA-256.
Source: experiments/INDEX.md, experiments/frozen/

## [2026-10-03] ingest | Sliding-window beats linear attention
Pages créées : sliding-window-beats-linear-attention. Pages mises à jour : index.
Source : raw/arxiv-2608.28444.txt (PDF arXiv 2608.28444 extrait par pypdf). Relevance faible pour le projet (hybrides natifs écartés par les auteurs).

## [2026-10-03] ingest | Automated Medical Coding on MIMIC-III and MIMIC-IV (Edin et al.)
Pages créées : automated-medical-coding-mimic-replicability. Pages mises à jour : overview, index.
Source : raw/arxiv-2304.10909.txt (PDF arXiv 2304.10909 extrait par pypdf).

## [2026-10-03] ingest | Statistical Inference of the MCC for Multiclass Classification (Tamura et al.)
Pages créées : mcc-multiclass-statistical-inference. Pages mises à jour : overview, protocole-gele-2026-10-03, index.
Source : raw/arxiv-2503.06450.txt (PDF arXiv 2503.06450 extrait par pypdf).

## [2026-10-03] ingest | Hierarchical Scoring for ML Classifier Error Impact Evaluation (Lanus et al.)
Pages créées : hierarchical-scoring-classifier-error-impact. Pages mises à jour : overview, protocole-gele-2026-10-03, index.
Source : raw/arxiv-2508.04489.txt (PDF arXiv 2508.04489 extrait par pypdf).

## [2026-10-03] ingest | Incidents et audits externes
Pages créées : incidents-et-audits-externes. Source : journal de nuit, audit GLM v3.

## [2026-10-03] ingest | État par composante
Pages créées : etat-par-composante. Source : RESULTATS.md, triage GLM v3.

## [2026-10-03] ingest | Contrats des modules
Pages créées : contrats-des-modules-du-chemin-court.
