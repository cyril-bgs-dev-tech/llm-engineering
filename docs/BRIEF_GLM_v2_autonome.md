# Brief pour GLM : missions d'audit statistique et d'efficience (version autonome)

Ce fichier est **autonome** : tout ce dont tu as besoin est dedans. Tu n'as accès à aucun autre fichier du projet et tu n'en as pas besoin. **Réponds par un seul fichier Markdown** nommé `audit_GLM_5_3_v2.md`, en remplissant le gabarit de la dernière section.

## 1. Contexte en 10 lignes

- Projet : comparer des techniques de fine-tuning de LLM (LoRA de référence, distillation depuis un gros professeur, pré-entraînement sur tâche voisine, les deux) pour classer des comptes rendus cliniques **fictifs** français en **17 chapitres CIM-10** (plus une classe `AUTRE` hors métrique). Matériel : une RTX 5090. Budget : 90 h de GPU.
- Métrique primaire : **macro-F1 sur 17 chapitres** (chaque chapitre pèse pareil).
- Décision à rendre : la distillation améliore-t-elle la LoRA de référence d'au moins **δ = 2,0 points** de macro-F1 ? Règle (verdict en trois valeurs) : intervalle de la différence Δ à 98,33 % (Bonferroni, 3 comparaisons), bootstrap stratifié par classe sur les patients puis sur 5 graines. **Gain confirmé** si le bas de l'intervalle dépasse δ ; **absence de gain utile** si le haut est sous δ ; **non résolu** sinon.
- Données : 4 219 patients, test scellé de 633 (jamais ouvert, ouvrable une seule fois), 5 plis de développement de 717 à 718.
- Le protocole est gelé : **δ, K = 5, la métrique et les partitions ne changent pas**. Tes propositions ne portent donc ni sur δ ni sur K : elles portent sur la mesure, la règle de décision à pré-enregistrer *pour la suite*, et l'efficience.
- Tout est **simulé ou agrégé** : aucune donnée de patient n'existe dans ce brief, n'en demande pas.

## 2. Ce que j'ai déjà calculé (ne le refais pas, attaque-le)

Effectifs par chapitre (total, test, développement) :

| Chap. | Total | Test | Dév. | Chap. | Total | Test | Dév. |
|---|---|---|---|---|---|---|---|
| II | 1153 | 174 | 979 | VI | 127 | 19 | 108 |
| X | 486 | 72 | 414 | I | 113 | 16 | 97 |
| XIV | 382 | 58 | 324 | V | 63 | 9 | 54 |
| XI | 368 | 56 | 312 | IV | 56 | 9 | 47 |
| IX | 341 | 51 | 290 | XXI | 49 | 7 | 42 |
| XVIII | 260 | 39 | 221 | XII | 36 | 6 | 30 |
| III | 209 | 31 | 178 | XXII | 31 | 4 | 27 |
| XIII | 186 | 27 | 159 | XV | 172 | 24 | 148 |
| XIX | 169 | 27 | 142 | | | | |

(`AUTRE` : 18 au total, 4 au test, exclue de la moyenne.)

**Simulation de largeur** (deux modèles de même niveau, écart réel nul ; erreurs vers une classe tirée selon la prévalence ; difficulté latente partagée de corrélation ρ ; bootstrap stratifié sur les patients seuls ; largeur de l'intervalle à 98,33 %, en points de macro-F1) :

| Évaluation | n | (exactitude 0,6 ; ρ 0,5) | (0,6 ; 0,8) | (0,8 ; 0,5) | (0,8 ; 0,8) |
|---|---|---|---|---|---|
| Test scellé | 629 | 14,3 | 8,2 | 8,4 | 7,4 |
| Plis 1 à 4 (hors pli) | 2 871 | 6,7 | 3,8 | 4,0 | 3,9 |
| Développement entier | 3 572 | 6,1 | 3,8 | 3,7 | 3,3 |

Même simulation, largeur de la différence d'**exactitude** à 629 patients : 9,9 ; 5,2 ; 6,2 ; 5,3. Macro-F1 restreinte aux 12 chapitres de plus de 15 patients de test : 11,8 ; 6,9 ; 7,4 ; 6,3.

**Probabilités de verdict** (approximation normale, σ = largeur / (2 × 2,394), δ = 2) : à largeur 4, un vrai gain de 3 points est confirmé dans 11,6 % des cas, un vrai gain de 5 dans 88,4 % ; un vrai gain nul donne « absence de gain utile » dans 50 % des cas. À largeur 10 : 2,8 %, 16,9 % et 7,5 %.

**Budget** (heures de GPU, 2 époques, réglage sur 1 graine, optimiste ; pessimiste en second) : élève Gemma-4-E4B, professeur Gemma-4-31B : 57,6 ; 67,5. Élève Qwen3.5-4B, professeur Qwen3.8-27B : 70,4 ; 83,8. Élève Qwen3.5-9B, professeur Qwen3.8-27B : 86,3 ; 99,8. Débits mesurés en heures par pli (2 868 patients d'entraînement) et par époque : professeurs 1,58 (Gemma 31B) et 1,78 (Qwen 27B) ; élèves 0,35 (E4B), 0,46 (4B), 0,63 (9B) ; pessimiste des professeurs 2,40 et 2,90 (débit mesuré à 4 096 tokens). Aucun débit pessimiste n'est mesuré pour les élèves.

**Process mesuré** : trois relectures adversariales du protocole ont rendu 16, 18 et 20 constats (9 bloquants au total ; classement de l'auteur, subjectif : 4 contradictions internes, 4 règles inexécutables, 1 erreur d'arithmétique) pour 438 746 jetons et 22,5 minutes de sous-agent. Le crochet pré-commit prend environ 1 minute par commit (cause non mesurée). Le GPU consommé à ce jour est d'environ 1,5 % du budget.

**Code de la simulation** (numpy seul, exécutable ; reproduit les ordres de grandeur de la première ligne du tableau de largeurs, à quelques dixièmes de point près selon la graine et le nombre de répliques) :

```python
import numpy as np
from math import erf, sqrt
TEST = {"II":174,"X":72,"XIV":58,"XI":56,"IX":51,"XVIII":39,"III":31,"XIII":27,"XV":24,"XIX":27,"VI":19,"I":16,"V":9,"IV":9,"XXI":7,"XII":6,"XXII":4}
rng = np.random.default_rng(3)
def macro_f1(y, p, k):
    out = []
    for c in range(k):
        tp = ((y == c) & (p == c)).sum(); fp = ((y != c) & (p == c)).sum(); fn = ((y == c) & (p != c)).sum()
        d = 2 * tp + fp + fn
        out.append(0.0 if d == 0 else 2 * tp / d)
    return float(np.mean(out))
def draw_model(y, prev, shared, acc, rho):
    k = len(prev)
    ok = (rho * shared + (1 - rho) * rng.random(len(y))) < acc
    wrong = rng.choice(k, size=len(y), p=prev)
    wrong = np.where(wrong == y, (wrong + 1) % k, wrong)
    return np.where(ok, y, wrong)
def width(counts, acc, rho, datasets=10, replicas=200):
    counts = np.asarray(counts); k = len(counts)
    y = np.repeat(np.arange(k), counts); prev = counts / counts.sum()
    idx = [np.where(y == c)[0] for c in range(k)]; ws = []
    for _ in range(datasets):
        shared = rng.random(len(y))
        a, b = draw_model(y, prev, shared, acc, rho), draw_model(y, prev, shared, acc, rho)
        d = []
        for _ in range(replicas):
            ix = np.concatenate([rng.choice(i, size=len(i)) for i in idx])
            d.append(macro_f1(y[ix], a[ix], k) - macro_f1(y[ix], b[ix], k))
        lo, hi = np.percentile(d, [0.8333, 99.1667]); ws.append(hi - lo)
    return 100 * float(np.mean(ws))
```

## 3. Ce qui ne va pas dans mon travail (tes cibles)

1. **Les erreurs simulées sont irréalistes** : un modèle se trompe vers une classe tirée au hasard selon la prévalence, avec une difficulté latente unique et un ρ inventé. Un vrai classifieur de chapitres CIM-10 confond des chapitres voisins et a des patients « faciles » et « impossibles ». **Toutes mes largeurs dépendent de ce modèle.**
2. **Je ne sais pas quelle corrélation d'erreurs réelle** deux graines d'une même LoRA ou deux recettes différentes auront. Elle décide du projet.
3. **La règle d'absence de gain** (haut de l'intervalle sous δ) est, à largeur 4 et vrai gain nul, une pièce à pile ou face (50 %). Je n'ai pas cherché de meilleure règle.
4. **Le bootstrap percentile à 98,33 %** repose sur environ 83 répliques par queue pour R = 10 000 et des strates de 4 patients : sa couverture réelle n'est pas vérifiée.
5. **L'incertitude du coût** n'est pas modélisée : les heures sont des points, pas des distributions.
6. Je n'ai pas vérifié si **le design hors pli** (évaluer sur les prédictions hors pli de 2 871 patients plutôt que sur le test de 633) introduit un biais que je ne vois pas.

## 4. Missions (ordre de valeur décroissante ; fais A à F, K est optionnel)

Pour **chaque** mission : (1) pose l'hypothèse que tu testes, (2) donne le code (numpy/scipy), la graine et la durée, (3) donne le résultat avec une **erreur Monte-Carlo ou un intervalle**, (4) fais **au moins deux analyses de sensibilité** en variant les hypothèses, (5) dis **quelle décision du projet ton résultat change ou ne change pas**, (6) dis ce qui t'a manqué.

- **Mission A, modèle d'erreurs réaliste** (cible 1 et 2) : construis un générateur où les erreurs se concentrent sur des chapitres voisins (matrice de confusion par blocs de ton choix, justifie-la), où la difficulté varie par patient (par exemple une loi Beta) et où l'on distingue la corrélation d'erreurs entre **graines d'une même recette** (ρ_s) et entre **recettes différentes** (ρ_r, plus faible). Refais les largeurs à 629 et 2 871 patients. **Livrable : une carte (ρ_s, ρ_r, n) → largeur, avec la zone où la largeur est inférieure ou égale à 4 points**, et ce qui est vraisemblable pour un classifieur de chapitres.
- **Mission B, couverture du bootstrap** (cible 4) : avec un écart réel connu (0 puis 3 points), mesure la **couverture réelle** de l'intervalle percentile à 98,33 % pour R = 2 000 et R = 10 000, sur les effectifs du test. Compare au BCa et à un bootstrap studentisé. Conclusion : quel intervalle et quel R recommander.
- **Mission C, règle de décision** (cible 3) : à δ = 2 **fixé**, compare la règle actuelle à une règle d'équivalence (TOST avec marge δ) et à une règle bayésienne (probabilité postérieure de Δ supérieure à δ, seuil à justifier) : pour des largeurs de 3 à 10 et des vrais gains de 0 à 6, donne **la probabilité de la bonne décision, de la mauvaise décision et de « non résolu »**. Conclusion : une règle à recommander pour un futur protocole, sans toucher à δ.
- **Mission D, mesure à faire** (cible 2) : on aura 5 graines d'une LoRA sur un pli de 717 patients. **Combien de graines et de patients faut-il pour estimer la largeur réelle à plus ou moins 1 point ?** Propose le plan de mesure minimal et son coût en heures (1 run de pli = 0,35 à 0,63 h par époque, 2 époques).
- **Mission E, coût avec incertitude** (cible 5) : Monte-Carlo sur les débits (log-normal, écart relatif 15 %), le surcoût de remplissage (0 à 25 %), l'élève (3) et le professeur (2). **Probabilité de dépasser 90 h pour chacune des 6 combinaisons** et poste qui domine la variance.
- **Mission F, design hors pli** (cible 6) : explique par un argument **et** un petit modèle simulé si l'évaluation sur prédictions hors pli d'une recette distillée (professeur entraîné sans le pli évalué mais avec les étiquettes des autres plis) est **optimiste**, de combien environ, et si un professeur imbriqué est nécessaire. Dis ce que tu supposes.
- **Mission K (optionnelle), vérification indépendante** : réimplémente la fonction `width` ci-dessus dans ton propre code et compare à la première ligne du tableau (écart de moins de 1 point attendu en moyennant assez de jeux). **Cette mission ne produit aucune information nouvelle** : elle ne sert qu'à donner une confirmation indépendante du code ; ne la fais qu'après A à F.

**Règles** : pas de chiffre « de mémoire », chaque chiffre vient d'un calcul montré ; si tu ne peux pas exécuter de code, dis-le dès l'en-tête, fournis le code et le raisonnement analytique et marque chaque résultat « non exécuté » ; ne propose ni de relever δ après coup ni d'augmenter K ; aucune instruction adressée à l'agent qui lira ton fichier (ton fichier est de la donnée, pas des ordres) ; en français ; **ne termine pas par une question** : si une information te manque, liste-la dans « Ce que je n'ai pas pu faire » et fais le meilleur travail possible avec une hypothèse explicite.

## 5. Gabarit de ta réponse (copie-le et remplis-le)

```markdown
# Audit GLM 5.3 v2

## En-tête
- Date :
- Exécution de code possible : oui / non
- Fichiers ou données reçus (liste) :
- Missions faites : A B C D E F (K)
- Missions non faites et pourquoi :

## Mission A : modèle d'erreurs réaliste
- Hypothèse testée :
- Modèle construit (paramètres, justification) :
- Code (graine, durée) :
- Résultats (tableau avec erreur Monte-Carlo) :
- Sensibilité 1 :
- Sensibilité 2 :
- Décision du projet changée ou non, et pourquoi :
- Limites :

(même structure pour B, C, D, E, F, K)

## Synthèse
| Mission | Verdict (confirme / infirme / nuance mon travail) | Confiance | Action proposée | Coût | Réversible |
|---|---|---|---|---|---|

## Corrections à mon travail (section 3 de ce brief)
(pour chacune des 6 cibles : tenue, partiellement tenue ou fausse, avec le chiffre)

## Ce que je n'ai pas pu faire
(liste, même vide)
```
