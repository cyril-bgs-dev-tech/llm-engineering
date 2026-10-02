---
name: paired-comparison
description: Décide si une variante bat la référence avec un test apparié et un intervalle de confiance. À utiliser pour comparer deux configurations, deux modèles ou deux recettes, pour clore une expérience préenregistrée, ou avant d'écrire « meilleur », « gain » ou « amélioration ».
---

# Comparaison appariée

« 0,71 contre 0,70 » ne dit rien tant qu'on ne sait pas si l'écart dépasse le bruit. On compare donc **les mêmes exemples, les mêmes graines, les mêmes plis**, et on décide avec le critère écrit d'avance dans la fiche préenregistrée.

## Étapes

1. **Charger** les prédictions brutes des deux runs depuis le registre (`run-registry`) ; vérifier qu'ils couvrent exactement les mêmes identifiants d'exemples.
2. **Bootstrap apparié** (au moins 2 000 rééchantillonnages, graine fixée) sur la différence de la métrique principale : moyenne, intervalle à 95 %.
3. **Test complémentaire** selon la métrique : McNemar pour l'exactitude, permutation appariée pour la macro-F1 ou la log loss, Wilcoxon sur les scores par pli si plusieurs graines.
4. **Plusieurs graines** : si la variance entre graines dépasse l'écart observé, la conclusion est « non résolu », et la fiche dit combien de graines supplémentaires il faudrait.
5. **Appliquer le critère de décision** de la fiche, sans le reformuler : gain confirmé, absence de gain, ou non résolu.
6. **Écrire le verdict** dans la fiche d'expérience et dans `RESULTATS.md`, avec intervalle et `run_id` des deux côtés.

**Terminé quand** le verdict est l'un des trois mots ci-dessus, appuyé par l'intervalle à 95 % et le test, et consigné aux deux endroits.

## Comparaisons multiples

Plus de trois variantes contre la même référence : correction de Holm sur les p-valeurs. Sur DiaMED (environ 150 cas de test), les intervalles seront larges : les décisions fines se prennent sur MorFITT, CLISTER ou en validation croisée répétée, comme le prévoit le plan.
