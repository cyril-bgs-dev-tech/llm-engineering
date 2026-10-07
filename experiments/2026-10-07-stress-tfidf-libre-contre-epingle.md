# Fiche préenregistrée : le TF-IDF tombe-t-il moins en panne quand le processus est épinglé sur un cœur que sans épinglage ? (mesure d'infrastructure ; suite de `2026-10-07-stress-tfidf-par-coeur`)

Écrite le 07/10/2026 avant tout essai de cette fiche. Motif : le run `20261007-044852-stress-tfidf-par-coeur` (fiche précédente, arrêtée par sa règle N31) a donné **5 pannes sur 65 essais** (2 segfaults, 3 `TypeError` dont deux signatures nouvelles), toutes sur des bras épinglés (cœurs 1, 3, 6, 17, 22), sans cœur à deux pannes ; le plan mélangé n'a tiré qu'**un seul essai « libre »** avant l'arrêt : la comparaison libre contre épinglé, qui était la question (a), n'a donc pas été mesurée. Cette fiche ne reprend que cette comparaison.

- **question** : le taux de panne brute (code de sortie non nul) du TF-IDF caractères est-il différent entre un processus libre et un processus épinglé sur un seul cœur ?
- **référence** : bras « libre » ; **variante** : bras « épinglé » (cœur tiré uniformément parmi 0 à 31, graine 20261007 ; le premier run a déjà 64 essais épinglés avec 5 pannes, **non réutilisés** dans la comparaison pour garder l'entrelacement).
- **jeux, mesure, processus fils** : identiques à la fiche précédente (1 500 premiers patients de développement, `fit_transform` brut sans relance, empreinte SHA-256, `nice -n 10`, 300 s au plus par essai).
- **plan** : 64 essais libres et 64 essais épinglés, ordre mélangé (graine 20261007), un processus à la fois (environ 24 minutes).
- **critère de décision** : test exact de Fisher bilatéral sur les taux de panne : p < 0,05 → « le taux diffère » (sens donné par les taux) ; sinon « non résolu » (borne haute indiquée). Une divergence d'empreinte quelle qu'elle soit est rapportée à part.
- **règle d'arrêt anticipé (N31)** : arrêt après 10 pannes au total ou si la mémoire disponible passe sous 20 000 Mio ; dans ce cas le verdict est « non résolu » sauf si le test est déjà significatif sur les essais faits et que chaque bras en compte au moins 20.
- **budget** : au plus 40 minutes de CPU, un cœur à la fois, moins de 3 Gio de RAM, aucun GPU, aucune lecture hors du dossier.
- **prédiction** : taux libre supérieur ou égal au taux épinglé (0,6) mais « non résolu » à cette taille (0,55) ; « le taux diffère » avec l'épinglage meilleur (0,25) ; « le taux diffère » avec l'épinglage pire (0,1) ; divergence silencieuse (0,05).
