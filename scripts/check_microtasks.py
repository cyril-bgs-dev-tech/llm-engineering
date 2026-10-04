#!/usr/bin/env python3
"""Vérifie la cohérence de MICROTACHES.md et son accord avec PLAN_PROJET_V6.md.

Contrôles : identifiants uniques, dépendances existantes et sans cycle, chemin court (★) fermé,
nombre de tâches par phase, couverture des catégories de qualité Q1 à Q12 à chaque porte
(comparée aux planchers du plan), identifiants cités par le plan, absence de tirets cadratins.
Bibliothèque standard uniquement. Code de sortie 1 si une erreur est trouvée.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MT = ROOT / "MICROTACHES.md"
PLAN = ROOT / "PLAN_PROJET_V6.md"
EXPECTED = {"P0": 47, "P1": 26, "P2": 12, "P3": 15, "P4": 10, "P5": 12, "P6": 8, "R": 5, "RM": 55}
GATES = ["P0", "P1", "P2", "P3", "P4", "P5"]
ROW = re.compile(r"^\| ((?:P\d|RM|R)-\d+|G-P\d) \|(.*)\|\s*$")

errors, warnings = [], []


def phase_of(task_id):
    return task_id.split("-")[0] if not task_id.startswith("G-") else task_id[2:]


def parse_tasks(text):
    tasks = {}
    order = []
    for line in text.splitlines():
        m = ROW.match(line)
        if not m:
            continue
        tid = m.group(1)
        cells = [c.strip() for c in m.group(2).split("|")]
        if len(cells) != 7:
            errors.append(f"{tid}: {len(cells)+1} colonnes au lieu de 8")
            continue
        star, typ, title, q, skills, proof, deps = cells
        if tid in tasks:
            errors.append(f"identifiant en double : {tid}")
        tasks[tid] = {
            "star": star == "★", "type": typ, "title": title,
            "q": re.findall(r"Q\d+", q), "skills": skills, "proof": proof,
            "deps": [] if deps in ("-", "") else [d.strip() for d in deps.split(",")],
        }
        order.append(tid)
    return tasks, order


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    text = MT.read_text(encoding="utf-8")
    tasks, _order = parse_tasks(text)

    # 1. caractères interdits
    if chr(0x2014) in text or chr(0x2013) in text:
        errors.append("tiret cadratin ou demi-cadratin présent dans MICROTACHES.md")

    # 2. nombre de tâches par phase
    counts = {}
    for tid in tasks:
        if tid.startswith("G-"):
            continue
        counts[phase_of(tid)] = counts.get(phase_of(tid), 0) + 1
    for ph, n in EXPECTED.items():
        if counts.get(ph) != n:
            errors.append(f"phase {ph} : {counts.get(ph)} tâches, {n} attendues")

    # 3. numérotation continue
    for ph, n in EXPECTED.items():
        for i in range(1, n + 1):
            tid = f"{ph}-{i:02d}"
            if tid not in tasks:
                errors.append(f"identifiant manquant : {tid}")

    # 4. dépendances
    star_by_phase = {}
    for tid, t in tasks.items():
        if t["star"] and not tid.startswith("G-"):
            star_by_phase.setdefault(phase_of(tid), []).append(tid)
    graph = {}
    for tid, t in tasks.items():
        deps = []
        for d in t["deps"]:
            if d == "*":
                deps += star_by_phase.get(phase_of(tid), [])
            elif d not in tasks:
                errors.append(f"{tid} dépend de {d}, qui n'existe pas")
            else:
                deps.append(d)
        graph[tid] = deps

    # 5. cycles
    state = {}

    def visit(n, stack):
        if state.get(n) == 1:
            errors.append("cycle : " + " > ".join(stack + [n]))
            return
        if state.get(n) == 2:
            return
        state[n] = 1
        for d in graph[n]:
            visit(d, stack + [n])
        state[n] = 2

    for tid in tasks:
        visit(tid, [])

    # 6. chemin court fermé
    for tid, t in tasks.items():
        if t["star"] and not tid.startswith("G-"):
            for d in graph[tid]:
                if not tasks[d]["star"]:
                    errors.append(f"chemin court ouvert : {tid} (★) dépend de {d} (non ★)")

    # 7. micro-tâche GPU ou spike : mention du pré-vol ou d'un skill de calcul
    for tid, t in tasks.items():
        if t["type"] not in ("GPU", "spike", "décision", "doc", "code", "mesure"):
            errors.append(f"{tid}: type inconnu « {t['type']} »")
        if not t["q"]:
            errors.append(f"{tid}: aucune catégorie de qualité")
        if not t["proof"]:
            errors.append(f"{tid}: preuve de fin vide")

    # 7b. RM-10 : toute tâche GPU ou spike cite le pré-vol, et tout skill cité existe
    skills_dir = ROOT / ".claude" / "skills"
    installed = {d.name for d in skills_dir.iterdir() if d.is_dir()} if skills_dir.exists() else set()
    for tid, t in tasks.items():
        if t["type"] in ("GPU", "spike") and "vram-preflight" not in t["skills"]:
            errors.append(f"{tid}: tâche {t['type']} sans le skill vram-preflight")
        if installed:
            for name in (s.strip().strip("`") for s in re.split(r"[,;]| et ", t["skills"])):
                if name and name not in installed:
                    errors.append(f"{tid}: skill cité mais absent de .claude/skills : {name}")

    # 8. couverture Q par porte, face aux planchers du plan
    floors = {}
    for line in PLAN.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (Q\d+) [^|]*\| (\d) \| (\d) \| (\d) \| (\d) \| (\d) \| (\d) \|\s*$", line)
        if m:
            floors[m.group(1)] = [int(m.group(i)) for i in range(2, 8)]
    if len(floors) != 12:
        errors.append(f"planchers lus dans le plan : {len(floors)} catégories au lieu de 12")

    def coverage(only_star):
        cov = {}
        for q in floors:
            row = []
            for gi, g in enumerate(GATES):
                phases = set(GATES[: gi + 1])
                n = sum(1 for tid, t in tasks.items()
                        if q in t["q"] and phase_of(tid) in phases
                        and (t["star"] or not only_star))
                row.append(n)
            cov[q] = row
        return cov

    full = coverage(False)
    mvp = coverage(True)
    print("Couverture (nombre de micro-tâches par catégorie, cumulé jusqu'à chaque porte)")
    print("catégorie  | " + " | ".join(f"G-{g}" for g in GATES) + "  (plancher entre parenthèses)")
    for q in sorted(floors, key=lambda s: int(s[1:])):
        cells = []
        for gi in range(6):
            f = floors[q][gi]
            n = full[q][gi]
            flag = ""
            if f >= 1 and n < f:
                flag = "!"
                errors.append(f"{q} à G-{GATES[gi]} : {n} micro-tâche(s) pour un plancher de {f}")
            cells.append(f"{n:>2}({f}){flag}")
        print(f"{q:<10} | " + " | ".join(cells))
    print("\nChemin court seul (★) :")
    for q in sorted(floors, key=lambda s: int(s[1:])):
        print(f"{q:<10} | " + " | ".join(f"{mvp[q][gi]:>2}" for gi in range(6)))
        if mvp[q][5] == 0:
            warnings.append(f"{q} : aucune micro-tâche ★ (le chemin court ne le couvre pas)")

    # 9. identifiants cités par le plan et la boîte à outils
    for name in ("PLAN_PROJET_V6.md", "BOITE_A_OUTILS.md", "roadmap_unifié.md"):
        p = ROOT / name
        if not p.exists():
            continue
        for ref in sorted(set(re.findall(r"\b(P[0-6]-\d{2}|RM-\d{2}|R-\d{2})\b", p.read_text(encoding="utf-8")))):
            if ref not in tasks:
                errors.append(f"{name} cite {ref}, absent de MICROTACHES.md")

    n_star = sum(1 for tid, t in tasks.items() if t["star"] and not tid.startswith("G-"))
    n_all = sum(1 for tid in tasks if not tid.startswith("G-"))
    # RM-10 : les comptes ★ annoncés par le plan sont lus ici, jamais recopiés à la main
    claim = re.search(r"(\d+) des (\d+) micro-tâches de `MICROTACHES.md` sont marquées ★", PLAN.read_text(encoding="utf-8"))
    if not claim:
        errors.append("PLAN_PROJET_V6.md ne contient plus la phrase des comptes ★ ; le contrôle ne peut pas comparer")
    elif (int(claim.group(1)), int(claim.group(2))) != (n_star, n_all):
        errors.append(f"le plan annonce {claim.group(1)} ★ sur {claim.group(2)} ; MICROTACHES.md en compte {n_star} sur {n_all}")
    print(f"\n{n_all} micro-tâches (hors scorecards), dont {n_star} sur le chemin court ★ ; "
          f"{len(tasks) - n_all} scorecards.")
    for w in warnings:
        print("AVERTISSEMENT :", w)
    if errors:
        print(f"\n{len(errors)} ERREUR(S) :")
        for e in errors:
            print(" -", e)
        return 1
    print("\nOK : aucune erreur.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
