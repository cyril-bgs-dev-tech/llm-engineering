# Carte de modèle v4 (06/10/2026, mise à jour après l'ouverture du test scellé) : système final G (gelé), classifieur du chapitre CIM-10, comptes rendus cliniques fictifs français

Remplace `docs/CARTE_DE_MODELE_V3.md` pour le système retenu par la règle de sélection (G). Statut : développement **et lecture confirmatoire sur le test scellé, ouvert une seule fois le 06/10/2026** (section « Test scellé » ci-dessous) ; avant cette ouverture le test n'était ni ouvert ni lu (aucune étiquette) ; **aucun verdict confirmatoire**. Le système est **gelé depuis le 06/10/2026** (ADR-016, `results/frozen_final.json`, prédiction chiffrée hachée) ; le test scellé reste fermé. Chaque chiffre renvoie à un `run_id` ; la checklist TRIPOD-LLM reste celle de `docs/CARTE_DE_MODELE_PROVISOIRE.md` et sera rejouée au gel (P4-10 n'est pas close).

## Usage prévu et hors usage
**Prévu** : démonstration méthodologique de l'évaluation de techniques d'adaptation sur un corpus **fictif**. **Hors usage** : tout usage clinique, toute décision sur des patients réels, toute généralisation à un autre corpus ou à des textes réels. Supervision humaine requise ; le renvoi à l'humain est prévu par la politique d'abstention ci-dessous.

## Système G
Moyenne à parts égales (un tiers chacune) de trois composantes : LoRA Qwen3.5-4B (une graine, 1000), CamemBERT-bio 10 époques moyenné sur cinq graines (1000 à 1004), TF-IDF caractères 3 à 5 à poids équilibrés. Entraînement final sur les 3 586 patients de développement. Modèles et temps A au registre : `20261006-022716-final-lora-s1000`, `final-encoder-s1000` à `s1004`, `final-tfidf`, `temps-a-*` ; empreintes dans la section 8 de `docs/BROUILLON_GEL_SYSTEME_FINAL.md`. Choix par la règle écrite d'avance : run `selection-systeme-final-apres-rm56` (G seul admissible : la borne basse de la différence de E avec G est −2,79 et celle de F −2,47, sous le seuil −2,0 ; E et F ne sont donc pas admissibles).

## Performance (prédictions hors pli, cinq plis, 3 586 patients)
| Système | macro-F1 | Source |
|---|---|---|
| G (LoRA + encodeur + TF-IDF) | 0,7799 | `selection-systeme-final-apres-rm56` |
| Ensemble encodeur + TF-IDF (E) | 0,7721 | idem |
| LoRA 4B seul (F), une graine par pli | 0,7673 | idem |
| Encodeur moyenné (D) | 0,7528 | idem |
| TF-IDF caractères (A) | 0,7202 | idem |
**Écart de G à E : +0,78 seulement, non résolu** ; LoRA contre encodeur +1,45 non résolu. Un seul LoRA final : la variance entre graines du LoRA n'est pas mesurée. **Prédiction chiffrée du gel (ADR-016, hachée avant ouverture)** : macro-F1 du test scellé centrée sur 0,78, probabilité d'un « gain confirmé » à δ = 2,0 d'environ 0,47 (largeur attendue 8,23 points au format du test, `puissance-au-format-du-test-scelle-g`) : « non résolu » reste le résultat le plus probable.

## Incertitude (développement, étalonnage croisé hors pli ; run `cinq-plis-ensemble-g`, `conformal-by-family`)
- **Calibration** : ECE 0,016 avant température, 0,020 après ; la température n'améliore pas G (perte logarithmique 0,465, Brier 0,207).
- **Conforme (LAC, cible 90 %)** : marginal, couverture 0,900 avec 1,12 classe par ensemble **mais couverture minimale par classe 0,143** : garantie marginale seulement. Par famille de chapitres (Mondrian) : couverture 0,901, 1,82 classe par ensemble, minimum par famille 0,891.
- **Abstention** (« un seul candidat dans l'ensemble : décision automatique, sinon renvoi à l'humain ») : exactitude 0,866 à couverture complète, 0,906 à 90 %, 0,931 à 80 %, 0,951 à 70 %.
- Hypothèse d'échangeabilité : des patients tirés du même corpus avec les mêmes auteurs ; sous décalage d'auteur, la garantie n'est pas démontrée pour G (un étalonnage par plis d'auteurs a été mesuré pour d'autres systèmes : `docs/CARTE_DE_MODELE_V3.md`). La couverture sur le test scellé est rapportée dans la section suivante (RM-51 en partie).

## Test scellé (ouvert une seule fois le 06/10/2026, 633 patients ; run `20261006-210015-ouverture-test-scelle-g`)
| Système | macro-F1 test | exactitude |
|---|---|---|
| **G** | **0,8131** | 0,8910 |
| LoRA seul (F) | 0,8033 | 0,8847 |
| Ensemble encodeur + TF-IDF (E) | 0,8031 | 0,8799 |
| Encodeur moyenné (D) | 0,7737 | 0,8657 |
| TF-IDF (A) | 0,7402 | 0,8483 |
**Question primaire (G moins TF-IDF)** : +7,28 points, IC 95 % par blocs d'auteurs [+1,55 ; +12,62] : **« non résolu »** à δ = 2,0 (la borne basse est sous 2,0). G moins E : +0,99 [−3,71 ; +5,00] ; G moins F : +0,98 [−1,39 ; +3,76] (sans verdict). **Incertitude** : conforme LAC à 90 %, couverture marginale 0,924 (1,10 classe par ensemble), par famille 0,916 (1,58 classe), **minimum 0,821** (une famille de 56 patients) ; abstention : exactitude 0,962 à 70 % de couverture (443 patients), 0,932 à 90 %. **Prédiction préenregistrée** (ADR-016) : quatre réussites sur six (macro-F1 de G au-dessus de l'intervalle prévu ; couverture minimale par famille sous le seuil prévu). Le test compte 633 patients et quatre chapitres de moins de 10 patients : les intervalles sont larges ; la robustesse aux nouveaux auteurs n'est pas mesurée sur le test.

## Coûts mesurés (composantes ; pas de mesure de bout en bout de G)
LoRA fusionné bf16 : p50 61,3 ms, 8,6 Wh pour 1 000 patients (`bench-lora-serving-llm-mur2-qwen3-5-4b-ep10-lr1e-4`) ; encodeur sur GPU bf16 : p50 4,3 ms (`bench-encoder-gpu-camembert-deploy-ep10-lr1e-4`) ; TF-IDF : p50 1,9 ms sur processeur (`bench-serving-tfidf-charbal-v1`). Cascade routée par l'ensemble conforme : non-infériorité (+0,23 [−0,09 ; +0,59]), 45,5 % des patients sans LoRA (`cascade-conforme-cinq-plis`) ; cascade à seuil : 93,4 % sans LoRA, couverture par région 0,899 et 0,923 avec 3,48 classes par ensemble (`cascade-seuil-couverture-cinq-plis`).

## Résultats négatifs qui bornent la carte
- **Distillation vers l'encodeur** : gain apparent de +3,47 non préservé par le professeur imbriqué (−0,77 [−2,46 ; +0,96] ; fuite de second ordre −4,24 [−6,00 ; −2,90]) ; les élèves ne font pas partie de G (RM-56).
- **Compression** : élagage à six couches dégradé (−13,08 [−15,88 ; −10,14], `20261006-121213-encodeur-elague-analyse-cinq-plis`) ; INT8 statique ONNX effondré (0,0227) et plus lent (`20261006-091535-onnx-int8-statique-partiel-camembert-deploy-ep10-lr1e-4`, partiel).
- **Recette d'encodeur** : lissage, moyenne de poids et curriculum sans gain ; bf16 équivalent (−0,07 [−1,67 ; +1,69]) et 2,25 fois plus rapide (`encodeur-v2-analyse-cinq-plis`).
- **Empilement appris** non supérieur au 50/50 (+0,41 [−0,25 ; +1,13], `glm-v6-empilement`).

## Limites connues
Corpus fictif dont l'étiquette vient d'un scénario ; cinq chapitres de 27 à 63 patients portent 85 % de la variance de la macro-F1 ; signature d'auteur d'environ 2 points (leave-one-author-out) ; erreurs surtout entre diagnostics rivaux (le bon chapitre figure parmi les deux premiers dans 95 % des cas) ; 65 erreurs confiantes dont l'audit montre de l'ambiguïté de codage, sans établir un bruit d'étiquette ; non-déterminisme GPU ; robustesse de l'encodeur et du LoRA aux nouveaux auteurs non mesurée (RM-39) ; **le LoRA classe sur la fin de la séquence** : retirer 10 % de la fin du compte rendu fait tomber sa macro-F1 de 0,78 à 0,14 et le seul retrait du saut de ligne final de 7,7 points (`20261006-173250-robustesse-modeles-appris-lora`, runs de diagnostic ci-dessous) ; l'encodeur perd 7,5 points quand le début est retiré (`20261006-171647-robustesse-modeles-appris-encoder`) ; règle de puissance v2 valable pour une question primaire unique à 95 % par blocs d'auteurs, pas à 98,33 %.

## Éthique et conformité
Corpus fictif, aucun comité d'éthique requis (à formuler ainsi) ; licences : `docs/LICENCES.md` ; aucune sortie du dépôt sans `claim-gate`.
