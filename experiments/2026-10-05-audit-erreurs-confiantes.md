# Fiche préenregistrée : audit des erreurs confiantes du TF-IDF (P2-06, levier 3 de l'audit GLM v6, EXPLORE)

Écrite après une **lecture pilote de 10 cas** (déclarée : ces 10 cas sont rapportés à part, non comptés dans le verdict) et avant la lecture des 20 cas suivants. Développement seulement ; aucune étiquette n'est modifiée ; texte fictif ; seuls des agrégats sortent du dépôt.

- **question** : parmi les 65 erreurs confiantes du TF-IDF caractères équilibré (probabilité de la classe prédite > 0,90, probabilité de la vraie classe < 0,10, cinq plis, 3 586 patients), quelle part vient d'une étiquette contestable ou d'une paire de diagnostics rivaux défendable, plutôt que d'une erreur du modèle ?
- **échantillon** : tirage reproductible (graine 5) de l'ordre des 65 cas ; cas 1 à 10 : pilote (déjà lus) ; **cas 11 à 30 : audit préenregistré**.
- **gabarit à trois verdicts par cas** (lecture de la conclusion et du contexte du compte rendu, comparaison avec le code et le libellé de l'étiquette du scénario et avec le chapitre prédit) : (E) **étiquette contestable** : le compte rendu établit un diagnostic précis qui relève d'un autre chapitre que l'étiquette, et le chapitre prédit est le plus cohérent avec le texte ; (R) **rivale défendable** : les deux chapitres sont défendables d'après le texte (règles de codage, conventions) ; (M) **erreur du modèle** : le texte désigne clairement le chapitre de l'étiquette.
- **limite déclarée** : le relecteur est l'assistante, non un codeur médical ; les verdicts sont une évaluation exploratoire à contre-expertiser par un professionnel du codage avant toute citation externe.
- **critère de décision** (appliqué aux 20 cas préenregistrés) : « bruit d'étiquette établi » si (E) ≥ 40 % ; « ambiguïté de codage établie » si (E) + (R) ≥ 60 % ; « erreur du modèle dominante » si (M) ≥ 50 % ; sinon « mixte ».
- **budget** : lecture seule, aucun calcul ; une demi-journée.
- **prédiction** : (E) + (R) ≥ 60 % (probabilité 0,75) ; (E) ≥ 40 % (0,35) ; (M) ≥ 50 % (0,1).
