# Tableaux générés depuis le registre (ne pas éditer à la main)

58 runs d'entraînement terminés avec une macro-F1 au registre. Regénérer : `.venv/bin/python scripts/make_tables.py`.

## Tous les runs d'entraînement (pli, modèle, taux, époques, graine)

| slug | pli | modèle | taux | époques | graine | macro-F1 | exactitude | log loss | ECE | secondes |
|---|---|---|---|---|---|---|---|---|---|---|
| `tfidf-hier-balanced` |  |  |  |  |  | 0,6740 | 0,8054 | 0,8621 |  |  |
| `tfidf-hier-plain` |  |  |  |  |  | 0,6448 | 0,7984 | 0,7963 |  |  |
| `tfidf-loao` |  |  |  |  |  | 0,6185 | 0,8036 | 0,6746 |  |  |
| `tfidf-variant-balanced` |  |  |  |  |  | 0,6805 | 0,8104 | 0,6675 |  |  |
| `tfidf-variant-char` |  |  |  |  |  | 0,6874 | 0,8095 | 0,6663 |  |  |
| `tfidf-variant-char-balanced` |  |  |  |  |  | 0,7202 | 0,8221 | 0,6152 |  |  |
| `tfidf-variant-char-balanced-author` |  |  |  |  |  | 0,6742 | 0,7989 | 0,7111 |  |  |
| `p1-11-qwen3-5-4b-lr1e-4` | 0 | Qwen3.5-4B | 0.0001 | 2 | 1000 | 0,5867 | 0,7894 | 0,7093 | 0,0338 | 3023.6 |
| `p1-26-rejeu-qwen3-5-4b-lr1e-4` | 0 | Qwen3.5-4B | 0.0001 | 2 | 1000 | 0,5807 | 0,7810 | 0,7109 | 0,0319 | 2490.3 |
| `q19-qwen3-5-4b-lr1e-4-perte-ponderee` | 0 | Qwen3.5-4B | 0.0001 | 2 | 1000 | 0,5637 | 0,7559 | 0,7729 | 0,0251 | 2507.9 |
| `p1-11-qwen3-5-4b-lr1e-5` | 0 | Qwen3.5-4B | 1e-05 | 2 | 1000 | 0,1930 | 0,4393 | 1,9003 | 0,0513 | 2514.9 |
| `p1-13-qwen3-5-4b-lr2e-5` | 0 | Qwen3.5-4B | 2e-05 | 2 | 1000 | 0,3060 | 0,5607 | 1,5422 | 0,0883 | 2515.3 |
| `p1-13-qwen3-5-4b-lr5e-5` | 0 | Qwen3.5-4B | 5e-05 | 2 | 1000 | 0,4733 | 0,7238 | 0,9817 | 0,0549 | 2509.2 |
| `llm-mur-s1001-qwen3-5-4b-ep10-lr1e-4` | 0 | Qwen3.5-4B | 0.0001 | 10 | 1001 | 0,7893 | 0,8633 | 0,7697 | 0,1072 | 12665.2 |
| `llm-mur2-qwen3-5-4b-ep10-lr1e-4` | 0 | Qwen3.5-4B | 0.0001 | 10 | 1000 | 0,7795 | 0,8577 | 0,8166 | 0,1078 | 12466.6 |
| `llm-mur-pli1-qwen3-5-4b-ep10-lr1e-4` | 1 | Qwen3.5-4B | 0.0001 | 10 | 1000 | 0,7415 | 0,8552 | 0,8135 | 0,1099 | 12420.9 |
| `p1-11-qwen3-5-9b-lr1e-4` | 0 | Qwen3.5-9B | 0.0001 | 2 | 1000 | 0,5650 | 0,7880 | 0,7234 | 0,0544 | 3622.7 |
| `p1-11-qwen3-5-9b-lr1e-5` | 0 | Qwen3.5-9B | 1e-05 | 2 | 1000 | 0,2128 | 0,4477 | 1,8558 | 0,0795 | 3690.1 |
| `p1-07-camembert-bio-lr1e-4` | 0 | camembert-bio-base | 0.0001 | 2 | 1000 | 0,4484 | 0,7699 | 1,0145 | 0,1755 | 42.9 |
| `p1-07-camembert-bio-lr1e-5` | 0 | camembert-bio-base | 1e-05 | 2 | 1000 | 0,0665 | 0,3766 | 2,3608 | 0,2863 | 43.1 |
| `p1-07-camembert-bio-lr2e-5` | 0 | camembert-bio-base | 2e-05 | 2 | 1000 | 0,2793 | 0,5816 | 2,0041 | 0,3808 | 42.6 |
| `p1-07-camembert-bio-lr5e-5` | 0 | camembert-bio-base | 5e-05 | 2 | 1000 | 0,4267 | 0,7559 | 1,4019 | 0,3630 | 42.8 |
| `camembert-epoques-lr1e-4-ep4` | 0 | camembert-bio-base | 0.0001 | 4 | 1000 | 0,5255 | 0,8033 | 0,7683 | 0,0477 | 85.7 |
| `camembert-epoques-lr1e-4-ep6` | 0 | camembert-bio-base | 0.0001 | 6 | 1000 | 0,5527 | 0,8089 | 0,7126 | 0,0385 | 127.5 |
| `camembert-fenetres-lr1e-4-ep6` | 0 | camembert-bio-base | 0.0001 | 6 | 1000 | 0,5554 | 0,8089 | 0,7244 | 0,0401 | 409.7 |
| `camembert-recette-lr2e-4-ep6` | 0 | camembert-bio-base | 0.0002 | 6 | 1000 | 0,6291 | 0,8187 | 0,6529 | 0,0674 | 133.4 |
| `camembert-deploy-ep10-lr1e-4` | 0 | camembert-bio-base | 0.0001 | 10 | 1000 | 0,7362 | 0,8298 | 0,7854 | 0,1113 | 408.3 |
| `camembert-fenetres-recette-retenue` | 0 | camembert-bio-base | 0.0001 | 10 | 1000 | 0,7033 | 0,8243 | 0,6543 | 0,0527 | 656.0 |
| `camembert-graine-ep10-s1` | 0 | camembert-bio-base | 0.0001 | 10 | 1001 | 0,7079 | 0,8131 | 0,7888 | 0,1095 | 214.2 |
| `camembert-graine-ep10-s2` | 0 | camembert-bio-base | 0.0001 | 10 | 1002 | 0,7175 | 0,8187 | 0,7545 | 0,1092 | 221.6 |
| `camembert-graine-ep10-s3` | 0 | camembert-bio-base | 0.0001 | 10 | 1003 | 0,7148 | 0,8285 | 0,7407 | 0,0925 | 223.2 |
| `camembert-graine-ep10-s4` | 0 | camembert-bio-base | 0.0001 | 10 | 1004 | 0,7349 | 0,8215 | 0,7910 | 0,1057 | 223.1 |
| `camembert-recette-lr1e-4-ep10` | 0 | camembert-bio-base | 0.0001 | 10 | 1000 | 0,7714 | 0,8326 | 0,7388 | 0,1074 | 214.6 |
| `camembert-recette-lr2e-4-ep10` | 0 | camembert-bio-base | 0.0002 | 10 | 1000 | 0,6486 | 0,8187 | 0,7066 | 0,0743 | 221.4 |
| `camembert-saturation-ep15` | 0 | camembert-bio-base | 0.0001 | 15 | 1000 | 0,7425 | 0,8243 | 0,9079 | 0,1402 | 323.1 |
| `camembert-saturation-ep20` | 0 | camembert-bio-base | 0.0001 | 20 | 1000 | 0,7384 | 0,8340 | 1,0118 | 0,1402 | 626.0 |
| `camembert-pli1-ep10-s0` | 1 | camembert-bio-base | 0.0001 | 10 | 1000 | 0,7605 | 0,8454 | 0,6866 | 0,0811 | 211.9 |
| `camembert-pli1-ep10-s1` | 1 | camembert-bio-base | 0.0001 | 10 | 1001 | 0,7763 | 0,8621 | 0,6613 | 0,0828 | 211.1 |
| `camembert-pli1-ep10-s2` | 1 | camembert-bio-base | 0.0001 | 10 | 1002 | 0,7679 | 0,8621 | 0,6859 | 0,0816 | 211.1 |
| `camembert-pli1-ep10-s3` | 1 | camembert-bio-base | 0.0001 | 10 | 1003 | 0,7080 | 0,8482 | 0,6462 | 0,0702 | 211.2 |
| `camembert-pli1-ep10-s4` | 1 | camembert-bio-base | 0.0001 | 10 | 1004 | 0,7247 | 0,8370 | 0,6927 | 0,0878 | 211.3 |
| `camembert-pli2-ep10-s0` | 2 | camembert-bio-base | 0.0001 | 10 | 1000 | 0,7392 | 0,8229 | 0,7274 | 0,0963 | 210.9 |
| `camembert-pli2-ep10-s1` | 2 | camembert-bio-base | 0.0001 | 10 | 1001 | 0,7428 | 0,8340 | 0,7077 | 0,0811 | 211.2 |
| `camembert-pli2-ep10-s2` | 2 | camembert-bio-base | 0.0001 | 10 | 1002 | 0,7705 | 0,8368 | 0,7114 | 0,0880 | 214.8 |
| `camembert-pli2-ep10-s3` | 2 | camembert-bio-base | 0.0001 | 10 | 1003 | 0,7675 | 0,8466 | 0,7020 | 0,0746 | 217.4 |
| `camembert-pli2-ep10-s4` | 2 | camembert-bio-base | 0.0001 | 10 | 1004 | 0,7481 | 0,8354 | 0,7467 | 0,0926 | 218.2 |
| `camembert-pli3-ep10-s0` | 3 | camembert-bio-base | 0.0001 | 10 | 1000 | 0,7054 | 0,8257 | 0,7390 | 0,0953 | 212.4 |
| `camembert-pli3-ep10-s1` | 3 | camembert-bio-base | 0.0001 | 10 | 1001 | 0,7461 | 0,8410 | 0,6948 | 0,0852 | 211.3 |
| `camembert-pli3-ep10-s2` | 3 | camembert-bio-base | 0.0001 | 10 | 1002 | 0,7146 | 0,8271 | 0,7349 | 0,0953 | 211.3 |
| `camembert-pli3-ep10-s3` | 3 | camembert-bio-base | 0.0001 | 10 | 1003 | 0,7126 | 0,8298 | 0,6797 | 0,0812 | 211.2 |
| `camembert-pli3-ep10-s4` | 3 | camembert-bio-base | 0.0001 | 10 | 1004 | 0,7208 | 0,8243 | 0,7544 | 0,0948 | 212.9 |
| `camembert-pli4-ep10-s0` | 4 | camembert-bio-base | 0.0001 | 10 | 1000 | 0,7125 | 0,8131 | 0,8048 | 0,0994 | 213.6 |
| `camembert-pli4-ep10-s1` | 4 | camembert-bio-base | 0.0001 | 10 | 1001 | 0,7638 | 0,8271 | 0,7958 | 0,0973 | 212.5 |
| `camembert-pli4-ep10-s2` | 4 | camembert-bio-base | 0.0001 | 10 | 1002 | 0,7728 | 0,8424 | 0,7553 | 0,0891 | 212.1 |
| `camembert-pli4-ep10-s3` | 4 | camembert-bio-base | 0.0001 | 10 | 1003 | 0,7335 | 0,8312 | 0,7555 | 0,0995 | 211.8 |
| `camembert-pli4-ep10-s4` | 4 | camembert-bio-base | 0.0001 | 10 | 1004 | 0,7319 | 0,8298 | 0,7843 | 0,0970 | 211.3 |
| `p1-11-gemma-4-e4b-lr1e-4` | 0 | gemma-4-E4B-it | 0.0001 | 2 | 1000 | 0,4558 | 0,6890 | 1,0659 | 0,0438 | 4225.9 |
| `p1-11-gemma-4-e4b-lr1e-5` | 0 | gemma-4-E4B-it | 1e-05 | 2 | 1000 | 0,1416 | 0,3780 | 2,0237 | 0,0365 | 3705.5 |

## Variance entre runs de même configuration (au moins deux runs : graines et rejeux)

| modèle | variante | pli | époques | taux | n | moyenne | écart-type | min | max |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3.5-4B | recette standard | 0 | 10 | 0.0001 | 2 | 0,7844 | 0,0069 | 0,7795 | 0,7893 |
| Qwen3.5-4B | recette standard | 0 | 2 | 0.0001 | 2 | 0,5837 | 0,0042 | 0,5807 | 0,5867 |
| camembert-bio-base | recette standard | 0 | 10 | 0.0001 | 6 | 0,7305 | 0,0230 | 0,7079 | 0,7714 |
| camembert-bio-base | recette standard | 1 | 10 | 0.0001 | 5 | 0,7475 | 0,0296 | 0,7080 | 0,7763 |
| camembert-bio-base | recette standard | 2 | 10 | 0.0001 | 5 | 0,7536 | 0,0144 | 0,7392 | 0,7705 |
| camembert-bio-base | recette standard | 3 | 10 | 0.0001 | 5 | 0,7199 | 0,0156 | 0,7054 | 0,7461 |
| camembert-bio-base | recette standard | 4 | 10 | 0.0001 | 5 | 0,7429 | 0,0248 | 0,7125 | 0,7728 |

## Systèmes hors pli à cinq plis : macro-F1 (17 chapitres, AUTRE exclu) par pli et regroupée

| système | pli 0 | pli 1 | pli 2 | pli 3 | pli 4 | regroupée (3 586) |
|---|---|---|---|---|---|---|
| TF-IDF caractères équilibré | 0,7184 | 0,6886 | 0,7483 | 0,7073 | 0,7248 | 0,7202 |
| Encodeur moyenné (5 graines) | 0,7331 | 0,7532 | 0,7613 | 0,7428 | 0,7684 | 0,7528 |
| Ensemble encodeur + TF-IDF | 0,7626 | 0,7512 | 0,7923 | 0,7746 | 0,7735 | 0,7721 |
