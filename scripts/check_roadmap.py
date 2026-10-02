#!/usr/bin/env python3
"""Vérifie roadmap_unifié.md contre MICROTACHES.md, et exporte tasks/plan.md et tasks/todo.md.

Contrôles : chaque micro-tâche du backlog apparaît une fois dans la séquence ; aucun identifiant inconnu ;
chaque dépendance précède sa tâche ; les tâches ★ sont dans les étapes R0 à R11 et les non ★ dans R12 à R16 ;
RM-24 ouvre la séquence ; chaque étape déclare objectif, skills, porte et arrêt, et ses skills existent ;
aucun tiret cadratin. Option --export : régénère tasks/plan.md et tasks/todo.md (cases cochées conservées).
Bibliothèque standard uniquement ; code de sortie 1 si une erreur est trouvée.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_microtasks as cm

ROADMAP = ROOT / "roadmap_unifié.md"
SKILLS = ROOT / ".claude" / "skills"
MVP_LAST_STAGE = 11
ROW = re.compile(r"^\| ((?:P\d|RM|R)-\d+|G-P\d) \|(.*)\|\s*$")
STAGE = re.compile(r"^### Étape R(\d+) : (.*)$")
META = re.compile(r"^\*\*(Objectif|Skills à charger|Porte de sortie|Arrêt ou repli si)\*\* : (.*)$")

errors = []


def parse_roadmap(text):
    seq, stages, meta = [], {}, {}
    stage, in_seq = None, False
    for line in text.splitlines():
        if line.startswith("## 5."):
            in_seq = True
            continue
        if line.startswith("## 6."):
            in_seq = False
        if not in_seq:
            continue
        m = STAGE.match(line)
        if m:
            stage = int(m.group(1))
            stages[stage] = m.group(2).strip()
            meta[stage] = {}
            continue
        m = META.match(line)
        if m and stage is not None:
            meta[stage][m.group(1)] = m.group(2).strip()
            continue
        m = ROW.match(line)
        if m and stage is not None:
            seq.append((m.group(1), stage, [c.strip() for c in m.group(2).split("|")]))
    return seq, stages, meta


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    export = "--export" in sys.argv
    mt_text = cm.MT.read_text(encoding="utf-8")
    tasks, _ = cm.parse_tasks(mt_text)
    errors.extend(cm.errors)
    text = ROADMAP.read_text(encoding="utf-8")
    if chr(0x2014) in text or chr(0x2013) in text:
        errors.append("tiret cadratin ou demi-cadratin dans roadmap_unifié.md")

    seq, stages, meta = parse_roadmap(text)
    ids = [s[0] for s in seq]
    pos = {}
    for i, (tid, st, _) in enumerate(seq):
        if tid in pos:
            errors.append(f"{tid} apparaît deux fois dans la séquence")
        pos[tid] = i
        if tid not in tasks:
            errors.append(f"{tid} est dans la séquence mais absent de MICROTACHES.md")
    for tid in tasks:
        if tid not in pos:
            errors.append(f"{tid} est dans MICROTACHES.md mais absent de la séquence")
    if ids and ids[0] != "RM-24":
        errors.append(f"la séquence doit s'ouvrir sur RM-24, elle s'ouvre sur {ids[0]}")

    star_by_phase = {}
    for tid, t in tasks.items():
        if t["star"] and not tid.startswith("G-"):
            star_by_phase.setdefault(cm.phase_of(tid), []).append(tid)
    for tid, st, _ in seq:
        if tid not in tasks:
            continue
        t = tasks[tid]
        deps = []
        for d in t["deps"]:
            deps += star_by_phase.get(cm.phase_of(tid), []) if d == "*" else [d]
        for d in deps:
            if d not in pos:
                continue
            if pos[d] >= pos[tid]:
                errors.append(f"{tid} (étape R{st}) précède sa dépendance {d} (étape R{seq[pos[d]][1]})")
        if t["star"] and st > MVP_LAST_STAGE:
            errors.append(f"{tid} est ★ mais placé en étape R{st} (le MVP s'arrête à R{MVP_LAST_STAGE})")
        if not t["star"] and st <= MVP_LAST_STAGE:
            errors.append(f"{tid} n'est pas ★ mais placé en étape R{st}, dans le MVP")

    skills_ok = {p.name for p in SKILLS.iterdir() if p.is_dir()} if SKILLS.exists() else set()
    for st in sorted(stages):
        for key in ("Objectif", "Skills à charger", "Porte de sortie", "Arrêt ou repli si"):
            if key not in meta.get(st, {}):
                errors.append(f"étape R{st} : ligne « {key} » manquante")
        for sk in re.split(r",\s*", meta.get(st, {}).get("Skills à charger", "").rstrip(".")):
            if sk and sk not in skills_ok:
                errors.append(f"étape R{st} : skill « {sk} » inexistant dans .claude/skills")
    if sorted(stages) != list(range(17)):
        errors.append(f"étapes présentes : {sorted(stages)} (R0 à R16 attendues)")

    print("Étape | tâches | dont ★")
    for st in sorted(stages):
        rows = [tid for tid, s, _ in seq if s == st]
        stars = sum(1 for tid in rows if tid in tasks and tasks[tid]["star"])
        print(f"R{st:<4} | {len(rows):>6} | {stars:>6}   {stages[st]}")
    n_star = sum(1 for tid in ids if tid in tasks and tasks[tid]["star"] and not tid.startswith("G-"))
    n_all = sum(1 for tid in ids if not tid.startswith("G-"))
    print(f"\n{n_all} micro-tâches placées (hors scorecards), dont {n_star} ★ ; "
          f"{len(ids) - n_all} scorecards ; {len(stages)} étapes.")

    if errors:
        print(f"\n{len(errors)} ERREUR(S) :")
        for e in errors:
            print(" -", e)
        return 1

    if export:
        out = ROOT / "tasks"
        out.mkdir(exist_ok=True)
        done = set()
        old = out / "todo.md"
        if old.exists():
            done = set(re.findall(r"^- \[x\] ((?:P\d|RM|R)-\d+|G-P\d)\b", old.read_text(encoding="utf-8"), re.MULTILINE))
        todo = ["# Liste de tâches (générée)", "",
                "Fichier généré par `python3 scripts/check_roadmap.py --export` depuis `roadmap_unifié.md` et `MICROTACHES.md`.",
                "Ne pas l'éditer à la main hors des cases à cocher ; toute autre modification se fait dans le backlog ou la feuille de route.", ""]
        plan = ["# Plan d'exécution (généré)", "",
                "Fichier généré depuis `roadmap_unifié.md`. L'ordre, les portes et les arrêts y sont définis ; le détail des tâches est dans `MICROTACHES.md`.", ""]
        for st in sorted(stages):
            plan += [f"## Étape R{st} : {stages[st]}", ""]
            for key in ("Objectif", "Skills à charger", "Porte de sortie", "Arrêt ou repli si"):
                plan.append(f"- **{key}** : {meta[st][key]}")
            plan.append("")
            todo += [f"## Étape R{st} : {stages[st]}", ""]
            for tid, s, _ in seq:
                if s != st:
                    continue
                t = tasks[tid]
                box = "x" if tid in done else " "
                dep = ", ".join(t["deps"]) if t["deps"] else "aucune"
                todo += [f"- [{box}] {tid} ({t['type']}) : {t['title']}",
                         f"  - Preuve de fin : {t['proof']}",
                         f"  - Skills : {t['skills']} ; dépendances : {dep}"]
            todo.append("")
        (out / "todo.md").write_text("\n".join(todo).rstrip() + "\n", encoding="utf-8")
        (out / "plan.md").write_text("\n".join(plan).rstrip() + "\n", encoding="utf-8")
        print(f"\nExport : {out / 'plan.md'} et {out / 'todo.md'}")
    print("\nOK : aucune erreur.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
