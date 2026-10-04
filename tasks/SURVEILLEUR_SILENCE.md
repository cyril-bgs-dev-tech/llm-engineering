# Surveilleur de silence (mode de nuit)

But : si l'assistant reste plus de 5 minutes sans agir, la continuation du projet est relancée sans intervention humaine.

## Mécanismes (trois couches)
1. **Tâche périodique de la session** (`CronCreate`, toutes les 5 minutes) : elle ne se déclenche que lorsque la session est inactive ; son message ordonne de lire cette page et de reprendre le travail. C'est le surveilleur actif.
2. **Réveil de fin de tour** (`ScheduleWakeup`, 5 à 25 minutes) : chaque tour d'attente se termine par un réveil armé, comme redondance.
3. **Témoin d'activité** (`scripts/silence_watch.sh`, processus détaché) : toutes les 60 secondes, il lit la dernière activité (journal de nuit, dernier commit, dernier run enregistré, journaux de lots) ; si plus de 300 secondes se sont écoulées, il écrit une ligne dans `results/logs/silence.log` (date, durée du silence). Le journal sert d'audit : comparer les silences au déclenchement du surveilleur actif.

## Procédure de reprise (à suivre à chaque déclenchement)
1. Lire la fin de `tasks/JOURNAL_NUIT_2026-10-02.md` et `tasks/FILE_DE_TRAVAIL_NUIT.md`.
2. Vérifier les lots en cours : processus `scripts/p1_finetune.py`, `nvidia-smi`, journaux de lot dans le répertoire de session (`scratchpad/p1_11/*.log`) ; consigner les runs terminés (`RESULTATS.md`), puis les comparaisons appariées.
3. Si un lot est en cours et que rien n'est à consigner : prendre le premier élément **faisable sans GPU** de `FILE_DE_TRAVAIL_NUIT.md`.
4. Choisir à chaque embranchement l'option la plus qualitative et la plus professionnelle (règle N23) : tracer le choix et son motif au journal ; ne jamais toucher aux exclusions (test scellé, protocole gelé sans ADR, push, location, API payante, lecture hors dossier, envoi externe).
5. Écrire une ligne « reprise par surveilleur à HH:MMZ : ... » au journal, commiter, puis armer un `ScheduleWakeup`.
6. Ne jamais rendre la main avec une file vide (N21) : la file est inépuisable par construction.

## Limites connues
Les tâches périodiques vivent dans la session (perdues à sa fermeture) et expirent après 7 jours. Le témoin d'activité détaché ne peut pas relancer l'assistant : il ne fait que mesurer.
