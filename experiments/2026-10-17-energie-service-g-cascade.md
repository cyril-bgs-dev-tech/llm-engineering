# Fiche préenregistrée : énergie du service de G en cascade E puis G (suite de RM-60 ; mesure d'infrastructure, hors qualité)

Écrite le 17/10/2026 avant tout essai de cette fiche. Motif : la latence du service de G en cascade est mesurée (run `20261017-015754-service-g-cascade`), son énergie ne l'est pas ; c'est l'un des trois manques qui retiennent la note d'efficience à 8 (`docs/presentation/PREUVES.md`, réévaluation du 17/10). Mesure courte (moins de 10 minutes de GPU), avec tampon de santé : elle n'est pas un calcul long publié au sens de la conséquence de RM-64.

- **question** : quelle énergie la carte consomme-t-elle pour 1 000 patients sur chacun des deux chemins du service (E seul, G complet), et quelle énergie moyenne en découle pour la part de routage hors pli de RM-60 (82,26 % par E) ?
- **référence** : G d'un seul tenant, 10,5 Wh pour 1 000 patients (banc sans HTTP, run `20261007-094117-service-g-bout-en-bout-gpu`).
- **variante** : le service de `scripts/service_g_cascade.py` (mode `energie`), mêmes modèles gelés (ADR-016), chemins forcés (τ = 0 pour E, τ = 1,01 pour G).
- **jeux** : les 200 premiers patients du pli 0 de développement, texte seul, aucune étiquette lue ; test scellé non lu.
- **mesure** : puissance de la carte lue par `nvidia-smi` (`llmft.energy.PowerSampler`, une lecture toutes les 0,5 s environ) pendant des passages complets répétés jusqu'à **au moins 15 s de charge par chemin** ; un passage d'échauffement non mesuré par chemin ; **énergie = puissance moyenne × durée mesurée** (indépendante du temps de lecture de chaque échantillon) ; énergie attendue = 0,8226 × chemin E + 0,1774 × chemin G. Énergie de la carte seulement (processeur non mesuré), puissance au repos de la carte incluse, comme le 07/10.
- **critère d'acceptation de la mesure** (descriptive, sans verdict statistique) : au moins 20 échantillons de puissance par chemin, sinon la mesure est déclarée insuffisante et n'entre pas dans la fiche de déploiement.
- **limite écrite d'avance** : la mesure du 07/10 sommait les échantillons à intervalle supposé de 1 s ; la méthode diffère, la comparaison aux 10,5 Wh est donc indicative ; la comparaison des deux chemins, elle, se fait dans la même mesure.
- **règle d'arrêt anticipé (N31)** : sans objet (un seul run) ; garde N27 (VRAM au-dessus de 30 000 Mio, RAM disponible sous 20 000 Mio).
- **budget** : moins de 10 minutes de GPU sous `scripts/run_guarded.sh`, environnement des lots GPU.
- **prédiction** (probabilités subjectives de l'assistante) : chemin E entre 0,6 et 2,0 Wh pour 1 000 patients (0,6) ; chemin G entre 8 et 13 Wh (0,7) ; énergie attendue entre 2 et 4 Wh (0,65) ; au moins 20 échantillons par chemin (0,9).
