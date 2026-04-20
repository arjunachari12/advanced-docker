# Exercise 2: Production-Ready Docker with a Simple Ollama GenAI App

## Use Case

This exercise uses a small GenAI chat application as the common use case for teaching the first four workshop modules:

- Module 1: Advanced Docker Image Building
- Module 2: Image Security, SBOMs, and Vulnerability Scanning
- Module 3: DevContainers and AI-Augmented Development with MCP-style tooling
- Module 4: CI/CD Automation with GitHub Actions and Docker

The application is intentionally simple: a Python FastAPI web app sends chat messages to a local Ollama model running in Docker.

## Files

```text
exercises/02-genai-module-coach/
├── app/
│   ├── main.py
│   └── smoke_test.py
├── security/
│   └── sbom-and-scan.md
├── Dockerfile
├── Dockerfile.bad
├── compose.yaml
├── requirements.txt
└── README.md
```

The CI workflow for this exercise is at repo root:

```text
.github/workflows/genai-chat-build-scan-sbom.yml
```

The DevContainer config is also at repo root:

```text
.devcontainer/devcontainer.json
```

## Before You Start

### Ubuntu on a VM

```bash
docker --version
docker compose version
docker run hello-world
```

If your user cannot run Docker:

```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

### Ubuntu on Windows WSL 2

Use Docker Desktop for Windows with WSL integration enabled for your Ubuntu distro.

From Ubuntu WSL:

```bash
docker --version
docker compose version
docker run hello-world
```

If Docker is not reachable:

1. Start Docker Desktop on Windows.
2. Enable WSL integration for your Ubuntu distro.
3. Restart WSL from PowerShell:

```powershell
wsl --shutdown
```

Then reopen Ubuntu WSL and retry `docker ps`.

## Start the Lab

Run these commands from this folder:

```bash
docker compose up -d ollama
docker compose exec ollama ollama pull qwen2.5:0.5b
docker compose up --build -d genai-chat
```

Open:

```text
http://localhost:8080
```

Try:

```text
Explain Docker multi-stage builds in three bullets.
```

Call the API directly:

```bash
curl http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Say hello from a Dockerized GenAI app."}'
```

Run the smoke test:

```bash
python3 app/smoke_test.py http://localhost:8080
```

## Module 1: Advanced Docker Image Building

Compare the wrong and right Dockerfiles.

Wrong way:

```bash
docker build -f Dockerfile.bad -t genai-chat:bad .
```

Right way:

```bash
docker build -f Dockerfile -t genai-chat:prod .
```

Compare size and layers:

```bash
docker images | grep genai-chat
docker history genai-chat:bad
docker history genai-chat:prod
```

Teaching points:

- `Dockerfile.bad` uses `python:latest`, copies the whole build context too early, installs as root, and runs development reload mode.
- `Dockerfile` uses a multi-stage build, dependency caching, a slim runtime stage, a non-root user, and a health check.
- `compose.yaml` uses service DNS: the app talks to Ollama through `http://ollama:11434`, not `localhost`.

## Module 2: Image Security, SBOMs, and Vulnerability Scanning

Build the production image:

```bash
docker build -t genai-chat:prod .
```

Generate an SBOM and scan the image:

```bash
cat security/sbom-and-scan.md
```

Suggested tools:

- Syft for SBOM generation
- Trivy for CVE scanning
- Docker Scout for CVEs and remediation recommendations

Teaching points:

- SBOMs document what is inside the image.
- Scanners find known vulnerabilities in OS and language packages.
- Non-root users, slim images, health checks, and fewer packages reduce runtime risk.

## Module 3: DevContainers and AI-Augmented Development

Open this repository in VS Code and use:

```text
Dev Containers: Reopen in Container
```

The file `../../.devcontainer/devcontainer.json` provides:

- Python tooling
- Docker CLI access from inside the dev container
- Docker and GitHub Actions VS Code extensions

Teaching points:

- DevContainers give every learner the same development environment.
- Docker access inside the dev container lets learners build, run, scan, and test images consistently.
- This is the foundation for adding AI tools, MCP servers, or code agents later.

## Module 4: CI/CD Automation with GitHub Actions and Docker

Review:

```bash
cat ../../.github/workflows/genai-chat-build-scan-sbom.yml
```

The workflow:

- builds the production Dockerfile
- generates an SBOM
- uploads the SBOM as an artifact
- scans the image with Trivy
- uploads SARIF results to GitHub code scanning

Teaching points:

- CI should build the same production image developers build locally.
- SBOM and scan results should be produced automatically.
- Pull requests can be blocked on high or critical vulnerabilities.

## Run the App Directly on Ubuntu

Keep Ollama in Docker:

```bash
docker compose up -d ollama
docker compose exec ollama ollama pull qwen2.5:0.5b
```

Install Python dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Run the app on the Ubuntu host:

```bash
OLLAMA_BASE_URL=http://localhost:11434 \
OLLAMA_MODEL=qwen2.5:0.5b \
uvicorn app.main:app --host 127.0.0.1 --port 8080
```

## Troubleshooting

### The Model Is Missing

```bash
docker compose exec ollama ollama pull qwen2.5:0.5b
```

### The App Cannot Reach Ollama

When the app runs inside Compose:

```text
OLLAMA_BASE_URL=http://ollama:11434
```

When the app runs directly on Ubuntu:

```text
OLLAMA_BASE_URL=http://localhost:11434
```

### Port 8080 Is Busy

Change the host port in `compose.yaml`:

```yaml
ports:
  - "8081:8080"
```

Then open:

```text
http://localhost:8081
```

## Clean Up

Stop containers:

```bash
docker compose down
```

Remove the Ollama model volume only when you want to free disk space:

```bash
docker compose down -v
```
