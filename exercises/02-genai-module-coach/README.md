# Exercise 2: Production-Ready Docker for a Simple GenAI App

This exercise uses one simple Python GenAI chat app that calls a local Ollama container.

Students will use the same codebase across the modules:

- Module 1: Docker build best practices, multi-stage builds, Buildx, and multi-architecture image push
- Module 2: image security, SBOM generation, and vulnerability scanning
- Module 3: DevContainer workflow for a consistent student environment
- Module 4: GitHub Actions CI/CD for build, SBOM, scan, and Docker Hub push

## Files

```text
exercises/02-genai-module-coach/
├── app/
│   ├── main.py
│   └── smoke_test.py
├── Dockerfile
├── Dockerfile.bad
├── MODULE1.md
├── MODULE2.md
├── MODULE3.md
├── MODULE4.md
├── compose.yaml
├── requirements.txt
└── README.md
```

## Prerequisites

### Ubuntu VM

```bash
docker --version
docker compose version
docker run hello-world
```

If Docker permission fails:

```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

### Ubuntu on Windows WSL 2

Use Docker Desktop on Windows.

In Docker Desktop:

- Start Docker Desktop
- Enable WSL integration for your Ubuntu distro
- Restart Ubuntu WSL if needed

From PowerShell:

```powershell
wsl --shutdown
```

Open Ubuntu WSL again and test:

```bash
docker ps
docker compose version
```

## Quick Start

Run from this folder:

```bash
cd exercises/02-genai-module-coach
```

Start Ollama:

```bash
docker compose up -d ollama
```

Pull the local model:

```bash
docker compose exec ollama ollama pull qwen2.5:0.5b
```

Build and run the GenAI app:

```bash
docker compose up --build -d genai-chat
```

Open:

```text
http://localhost:8080
```

Check health:

```bash
curl http://localhost:8080/health
```

Expected:

```json
{"status":"ok"}
```

Send a chat message:

```bash
curl http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain Docker multi-stage builds in three bullets."}'
```

Run the smoke test:

```bash
python3 app/smoke_test.py http://localhost:8080
```

## Student Module Guides

Start here:

```text
MODULE1.md
```

Then continue:

```text
MODULE2.md
MODULE3.md
MODULE4.md
```

## Cleanup

Stop containers:

```bash
docker compose down
```

Remove the Ollama model volume only if you want to free disk space:

```bash
docker compose down -v
```
