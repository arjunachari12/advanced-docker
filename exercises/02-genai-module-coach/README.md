# Exercise 2: Production-Ready Docker for a Simple GenAI App

This exercise uses small Python GenAI apps that call local models through Ollama, Docker Model Runner, and Dagger workflows.

## What This Code Does

This folder is a teaching lab for containerized GenAI workflows.

It includes:

- a local Ollama chat app for Docker lessons
- a Dagger-based AI agent that turns a shipping task into a short workflow plan
- a Docker Model Runner app that calls a local model through an OpenAI-compatible API
- a container-use style workflow that indexes docs, self-checks the generated data, and deploys a searchable doc assistant

The main idea across all modules is:

```text
put AI apps and workflow steps inside containers so they are easier to run, test, debug, and teach
```

Students will use the same codebase across the modules:

- Module 1: Docker build best practices, multi-stage builds, Buildx, and multi-architecture image push
- Module 2: image security, SBOM generation, and vulnerability scanning
- Module 3: DevContainer workflow for a consistent student environment
- Module 4: GitHub Actions CI/CD for build, SBOM, scan, and Docker Hub push
- Module 5: Dagger workflow composition for building and deploying an AI agent
- Module 6: Docker Model Runner for containerized local GenAI apps
- Module 7: container-use style isolated workflows for a doc-indexing AI stack

## Files

```text
exercises/02-genai-module-coach/
├── app/
│   ├── main.py
│   └── smoke_test.py
├── agent_app/
│   ├── Dockerfile
│   ├── agent.py
│   └── test_agent.py
├── model_runner_app/
│   ├── main.py
│   └── smoke_test.py
├── container_use_stack/
│   ├── app/
│   ├── docs/
│   ├── tools/
│   ├── workflows/
│   └── container_use.py
├── src/
│   └── genai_agent_pipeline/
│       ├── __init__.py
│       └── main.py
├── Dockerfile
├── Dockerfile.bad
├── Dockerfile.model-runner
├── MODULE1.md
├── MODULE2.md
├── MODULE3.md
├── MODULE4.md
├── MODULE5.md
├── MODULE6.md
├── MODULE7.md
├── compose.container-use.yaml
├── compose.model-runner.yaml
├── compose.yaml
├── dagger.json
├── pyproject.toml
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
MODULE5.md
MODULE6.md
MODULE7.md
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
