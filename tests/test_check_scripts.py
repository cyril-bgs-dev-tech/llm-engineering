"""Les trois contrôles de `make check` (backlog, feuille de route, wiki) échouent quand on leur présente un défaut (RM-10)."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FILES = ["MICROTACHES.md", "PLAN_PROJET_V6.md", "BOITE_A_OUTILS.md", "roadmap_unifié.md"]


@pytest.fixture
def box(tmp_path):
    """Copie minimale du projet : scripts, documents de pilotage, noms des skills, wiki."""
    (tmp_path / "scripts").mkdir()
    for s in ("check_microtasks.py", "check_roadmap.py", "check_wiki.py"):
        shutil.copy(ROOT / "scripts" / s, tmp_path / "scripts" / s)
    for f in FILES:
        shutil.copy(ROOT / f, tmp_path / f)
    for d in (ROOT / ".claude/skills").iterdir():
        if d.is_dir():
            (tmp_path / ".claude/skills" / d.name).mkdir(parents=True)
            (tmp_path / ".claude/skills" / d.name / "SKILL.md").write_text("x", encoding="utf-8")
    shutil.copytree(ROOT / "knowledge", tmp_path / "knowledge", ignore=shutil.ignore_patterns("raw", "assets"))
    return tmp_path


def run(box, script):
    return subprocess.run([sys.executable, f"scripts/{script}"], cwd=box, capture_output=True, text=True, check=False)


def edit(box, name, old, new):
    p = box / name
    text = p.read_text(encoding="utf-8")
    assert old in text, f"motif introuvable pour la mutation : {old!r}"
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


@pytest.mark.parametrize("script", ["check_microtasks.py", "check_roadmap.py", "check_wiki.py"])
def test_the_unmodified_project_passes(box, script):
    assert run(box, script).returncode == 0, run(box, script).stdout[-600:]


def test_backlog_rejects_a_gpu_task_without_preflight(box):
    text = (box / "MICROTACHES.md").read_text(encoding="utf-8")
    row = next(x for x in text.splitlines() if x.startswith("| P0-06 |"))  # tâche GPU
    assert "vram-preflight" in row
    (box / "MICROTACHES.md").write_text(text.replace(row, row.replace(", vram-preflight", "")), encoding="utf-8")
    r = run(box, "check_microtasks.py")
    assert r.returncode == 1 and "P0-06" in r.stdout and "vram-preflight" in r.stdout


def test_backlog_rejects_a_skill_that_does_not_exist(box):
    edit(box, "MICROTACHES.md", "interview-me", "skill-inexistant")
    r = run(box, "check_microtasks.py")
    assert r.returncode == 1 and "skill-inexistant" in r.stdout


def test_backlog_rejects_a_star_count_that_drifted_from_the_plan(box):
    import re

    path = box / "PLAN_PROJET_V6.md"
    text = path.read_text(encoding="utf-8")
    assert re.search(r"\d+ des \d+ micro-tâches", text), "le plan annonce le nombre de tâches sur le chemin court"
    path.write_text(re.sub(r"\d+ des \d+ micro-tâches", "91 des 159 micro-tâches", text, count=1), encoding="utf-8")  # annonce volontairement fausse
    r = run(box, "check_microtasks.py")
    assert r.returncode == 1 and "annonce 91" in r.stdout


def test_backlog_rejects_a_dependency_on_a_missing_task(box):
    edit(box, "MICROTACHES.md", "| P0-04 |", "| P0-04 |")  # garde-fou : la ligne existe
    text = (box / "MICROTACHES.md").read_text(encoding="utf-8")
    line = next(x for x in text.splitlines() if x.startswith("| P0-05 |"))
    (box / "MICROTACHES.md").write_text(text.replace(line, line.rsplit("|", 2)[0] + "| P0-99 |"), encoding="utf-8")
    assert run(box, "check_microtasks.py").returncode == 1


def test_roadmap_rejects_a_task_placed_before_its_dependency(box):
    text = (box / "roadmap_unifié.md").read_text(encoding="utf-8")
    rows = [x for x in text.splitlines() if x.startswith(("| P0-04 |", "| P0-05 |"))]
    assert len(rows) == 2
    swapped = text.replace(rows[0], "@@A@@").replace(rows[1], rows[0]).replace("@@A@@", rows[1])
    (box / "roadmap_unifié.md").write_text(swapped, encoding="utf-8")
    assert run(box, "check_roadmap.py").returncode == 1


def test_roadmap_rejects_a_task_missing_from_the_sequence(box):
    text = (box / "roadmap_unifié.md").read_text(encoding="utf-8")
    row = next(x for x in text.splitlines() if x.startswith("| P0-05 |"))
    (box / "roadmap_unifié.md").write_text(text.replace(row + "\n", "", 1), encoding="utf-8")
    assert run(box, "check_roadmap.py").returncode == 1


def test_wiki_check_rejects_a_broken_link_and_an_unreadable_report(box):
    page = box / "knowledge/wiki/pages/zz-piege.md"
    page.write_text("---\ntitle: p\ncategory: Analyses\nsummary: s\ntags: [x]\nsources: [a]\ncreated: 2026-10-02\nupdated: 2026-10-02\n---\n\n[[nulle-part](pages/nulle-part.md)]\n", encoding="utf-8")
    assert run(box, "check_wiki.py").returncode == 1
    page.unlink()
    (box / "knowledge/bin/lint-mechanical.py").write_text("print('pas du json')\n", encoding="utf-8")
    assert run(box, "check_wiki.py").returncode == 2  # un rapport illisible n'est jamais « propre »
