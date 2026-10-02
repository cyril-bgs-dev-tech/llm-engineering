# Rapport du fil synthétique (make smoke)

Durée : 9.7 s, runs enregistrés pendant le fil : 2.

| Maillon | Résultat |
|---|---|
| contrat | toy_sentiment, 2 classes |
| contrat invalide rejeté | contrat : Value error, identifiants de classe dupliqués : ['positif'] |
| chaîne complète | run 20261002-095630-chain-toy-sentiment-cpu, macro_f1 1.000 |
| rejeu identique | mêmes partitions (SHA-256) et mêmes métriques à graine égale |
| fuite piégée détectée (partitions) | identifiant toy0024 présent dans le test et le pli 0 |
| fuite piégée détectée (quasi-doublon) | similarité 0.8571 |

Le « rejeu » vérifie la reproductibilité à graine égale ; la reprise d'un entraînement interrompu est prouvée à part (spike P0-13, pertes identiques sur 20 pas).
