# Environnement reproductible du projet. Construit sans GPU ; l'exécution sur GPU demande `docker run --gpus all`.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 PYTHONUTF8=1 HF_HOME=/work/artifacts/hf_cache
WORKDIR /work
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
# git sert aux tests (plancher) et à l'empreinte de code des runs ; installé après la synchronisation pour garder son cache
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
COPY src ./src
COPY hardware ./hardware
COPY tests ./tests
COPY scripts ./scripts
COPY task_specs ./task_specs
RUN mkdir -p results
CMD ["uv", "run", "--frozen", "python", "-m", "pytest", "-q", "-m", "not gpu"]
