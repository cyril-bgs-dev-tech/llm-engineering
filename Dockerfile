# Environnement reproductible du projet. Construit sans GPU ; l'exécution sur GPU demande `docker run --gpus all`.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 PYTHONUTF8=1 HF_HOME=/work/artifacts/hf_cache
WORKDIR /work
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
# git sert aux tests (plancher) et à l'empreinte de code des runs ; procps (free, ps) sert au garde mémoire testé par tests/test_run_guarded.py ; installés après la synchronisation pour garder son cache
RUN apt-get update && apt-get install -y --no-install-recommends git procps && rm -rf /var/lib/apt/lists/*
COPY src ./src
COPY hardware ./hardware
COPY tests ./tests
COPY scripts ./scripts
COPY task_specs ./task_specs
# documents de pilotage, noms des skills et wiki lus par tests/test_check_scripts.py
COPY MICROTACHES.md PLAN_PROJET_V6.md BOITE_A_OUTILS.md roadmap_unifié.md ./
COPY .claude/skills ./.claude/skills
COPY knowledge ./knowledge
RUN mkdir -p results
CMD ["uv", "run", "--frozen", "python", "-m", "pytest", "-q", "-m", "not gpu"]
