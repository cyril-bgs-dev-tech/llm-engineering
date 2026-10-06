# Surveilleur de silence (mode de nuit)

But : si l'assistant reste plus de 5 minutes sans agir, la continuation du projet est relancée sans intervention humaine.

## Mécanismes (trois couches)
1. **Tâche périodique de la session** (`CronCreate`, toutes les 5 minutes) : elle ne se déclenche que lorsque la session est inactive ; son message ordonne de lire cette page et de reprendre le travail. C'est le surveilleur actif.
2. **Réveil de fin de tour** (`ScheduleWakeup`, 5 à 25 minutes) : chaque tour d'attente se termine par un réveil armé, comme redondance.
3. **Témoin d'activité** (`scripts/silence_watch.sh`, processus détaché) : toutes les 60 secondes, il lit la dernière activité (journal de nuit, dernier commit, dernier run enregistré, journaux de lots) ; si plus de 300 secondes se sont écoulées, il écrit une ligne dans `results/logs/silence.log` (date, durée du silence). Le journal sert d'audit : comparer les silences au déclenchement du surveilleur actif.

## Cadence adaptative (04/10/2026, 04h30Z)
Pendant un run GPU long où le seul travail utile est l'attente (Qwen3.5-4B à 10 époques, fin vers 07h45Z), la tâche périodique passe de 5 à 20 minutes (id c90fbd46 : minutes 7, 27 et 47 de chaque heure) : un déclenchement toutes les 5 minutes ne fait que consommer des tours sans travail à faire. Elle repasse à 5 minutes dès que le run est terminé et qu'un lot de la file est à lancer. Le témoin détaché continue de mesurer le silence chaque minute.

## Cadence du 04/10/2026 à 18h00Z
Pendant le LoRA des plis 2 à 4 (fin du pli 2 vers 19h30Z, pli 3 vers 23h00Z, pli 4 vers 02h30Z), la tâche périodique passe à 20 minutes (id 64695581, minutes 7, 27 et 47 de l'heure locale, remplace d0d09631). Elle repasse à 5 minutes quand un lot est à lancer sans attente.

## Procédure de reprise (à suivre à chaque déclenchement)
1. Lire la fin de `tasks/JOURNAL_NUIT_2026-10-02.md` et `tasks/FILE_DE_TRAVAIL_NUIT.md`.
2. Vérifier les lots en cours : processus `scripts/p1_finetune.py`, `nvidia-smi`, journaux de lot dans le répertoire de session (`scratchpad/p1_11/*.log`) ; consigner les runs terminés (`RESULTATS.md`), puis les comparaisons appariées.
3. Si un lot est en cours et que rien n'est à consigner : prendre le premier élément **faisable sans GPU** de `FILE_DE_TRAVAIL_NUIT.md`.
4. Choisir à chaque embranchement l'option la plus qualitative et la plus professionnelle (règle N23) : tracer le choix et son motif au journal ; ne jamais toucher aux exclusions (test scellé, protocole gelé sans ADR, push, location, API payante, lecture hors dossier, envoi externe).
4b. Archiver les journaux de lot dans le dépôt : `bash scripts/archive_logs.sh <scratchpad>/p1_11` (audit GLM v4, G-c3).
5. Écrire une ligne « reprise par surveilleur à HH:MMZ : ... » au journal, commiter, puis armer un `ScheduleWakeup`.
6. Ne jamais rendre la main avec une file vide (N21) : la file est inépuisable par construction.

## Limites connues
Les tâches périodiques vivent dans la session (perdues à sa fermeture) et expirent après 7 jours. Le témoin d'activité détaché ne peut pas relancer l'assistant : il ne fait que mesurer.

## Cadence du 06/10/2026 à 13h50Z
File vide et GPU libre, en attente des réponses de Cyril (Q22 à Q25) : la tâche périodique passe à une fois par heure (id eda5b075, minute 7, remplace 69f29474). Elle repasse à 5 minutes dès qu'un lot est à lancer sans attente.
