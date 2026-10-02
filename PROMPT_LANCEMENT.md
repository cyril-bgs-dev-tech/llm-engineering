# Prompt de lancement du projet (à coller dans une session ouverte dans `LLM_finetuning/`)

Version 3, 01/10/2026. Ce prompt reprend l'exécution là où la feuille de route l'a laissée.

---

Tu travailles sur le projet LLM_finetuning. `CLAUDE.md` est chargé. **`roadmap_unifié.md` est ton guide d'exécution** : l'ordre des étapes, les portes d'arrêt et les skills à charger à chaque étape. `PLAN_PROJET_V6.md` est la spécification, `MICROTACHES.md` le détail de chaque micro-tâche et sa preuve de fin, `BOITE_A_OUTILS.md` la liste des outils et papiers avec leur statut de vérification.

1. **Contrôle de départ.** Lance `python3 scripts/check_microtasks.py` et `python3 scripts/check_roadmap.py` (verts attendus). Lis `tasks/todo.md` : la première case non cochée est ta prochaine tâche. Ne la commence qu'après avoir chargé les skills de son étape.
2. **Avance dans l'ordre de la feuille de route**, une micro-tâche à la fois, en la clôturant sur sa preuve de fin. Coche la case dans `tasks/todo.md` seulement quand la preuve existe.
3. **À chaque porte d'arrêt**, présente à Cyril un résumé court : ce qui est prouvé, ce qui ne l'est pas, ce que la porte décide. Ne passe pas la porte sans sa réponse si la décision est la sienne.
4. **Décisions de Cyril** : propose avec un défaut recommandé et attends. Ne comble jamais une décision ouverte par une supposition.
5. **Spike bloquant en échec** : arrête-toi et présente le plan B du plan V6, section 9.
6. **Quand tu modifies le backlog ou la feuille de route**, relance les deux vérificateurs et régénère `tasks/` avec `python3 scripts/check_roadmap.py --export`.
