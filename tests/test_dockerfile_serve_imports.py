"""L'image de service ne copie qu'une liste fixe de modules : chaque module de llmft importé (transitivement) par scripts/serve_tfidf.py doit y figurer,
sinon l'image se construit puis échoue au démarrage (régression du 17/10 : http_service importe drift_monitor)."""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _llmft_imports(path: Path) -> set[str]:
    out = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("llmft"):
            out |= {f"{node.module}.{a.name}" for a in node.names} | {node.module}
        elif isinstance(node, ast.Import):
            out |= {a.name for a in node.names if a.name.startswith("llmft")}
    files = set()
    for name in out:
        f = ROOT / "src" / Path(*name.split(".")).with_suffix(".py")
        if f.exists():
            files.add(f.relative_to(ROOT).as_posix())
    return files


def test_l_image_copie_tous_les_modules_dont_le_service_a_besoin() -> None:
    copied = set(re.findall(r"src/llmft/[a-z_]+\.py", (ROOT / "Dockerfile.serve").read_text(encoding="utf-8")))
    needed, todo = set(), ["scripts/serve_tfidf.py"]
    while todo:
        for f in _llmft_imports(ROOT / todo.pop()) - needed:
            needed.add(f)
            todo.append(f)
    assert needed - copied == set(), f"modules absents de Dockerfile.serve : {sorted(needed - copied)}"
