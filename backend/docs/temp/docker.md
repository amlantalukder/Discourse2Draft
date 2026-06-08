# Docker instructions

This repository includes two docker setups:

- Development: use `docker-compose.yml` (bind-mounts source, fast iteration).
- Production: use `Dockerfile.prod` (build image with pinned dependencies from `requirements.txt`).

1) Quick development (docker-compose)

```bash
docker-compose up --build
```

This mounts the project into the container so you can edit files locally and see changes (depends on how the app and Shiny detect file changes). The compose file exposes port `8011`.

2) Production image (recommended for deployments)

Build the production image (uses `Dockerfile.prod`):

```bash
docker build -f Dockerfile.prod -t word-processor-ai:prod .
```

Run it:

```bash
docker run --rm -p 8011:8011 -e PORT=8011 word-processor-ai:prod
```

3) Quick checks

```bash
docker ps
docker logs --follow <container>
curl -I http://127.0.0.1:8011
```

Notes and troubleshooting
- The prod Dockerfile installs several system packages (build-essential, libpq-dev, libgomp1) that are commonly required by packages used in this project (psycopg2, onnxruntime, chromadb, etc.). If you hit build-time errors complaining about missing headers, add the missing `-dev` package shown in the logs and rebuild.
- The project pins Python to 3.12 in `pyproject.toml`. Use the matching Python base image (the provided `Dockerfile.prod` uses `python:3.12-slim`).
- If you prefer the `uv` workflow (the project previously used an `uv` base image), you can either:

4) UV workflow (recommended if you maintain `uv.lock`)

If you maintain `uv.lock` and want to use the `uv` toolchain to install pinned wheels, use `Dockerfile.uv` which is included in this repo.

Build the uv image:

```bash
docker build -f Dockerfile.uv -t word-processor-ai:uv .
```

Run it:

```bash
docker run --rm -p 8011:8011 -e PORT=8011 word-processor-ai:uv
```

This uses the `uv` base image and runs `uv sync` during the image build to install the exact wheels from `uv.lock`.

- Pros: reproducible installs from `uv.lock`, often faster local iteration if you use `uv` for dev.
- Cons: relies on the `uv` base image. If you prefer a minimal runtime, use `Dockerfile.prod` or a multi-stage build.
- For a robust production image you can further reduce size by using a multi-stage build that compiles wheels in a builder image and copies only installed packages into the runtime image.

Optional next steps
- Add a small HTTP `/health` endpoint in `app.py` that returns 200 OK. This makes the healthcheck easier to validate with HTTP instead of low-level TCP checks.
- Create `docker-compose.override.yml` for development-only services (e.g., a local vector DB, Postgres) and environment variables.
- Add CI pipeline steps that build and smoke-test the image on push (GitHub Actions sample available on request).

