# Module 3: DevContainers for a Repeatable Docker Lab Environment

## Goal

In this module you will:

- understand why DevContainers help students
- open the repo in a containerized development environment
- run Docker commands from the DevContainer
- build and test the GenAI app from the same environment

## Why DevContainers?

DevContainers help every student use the same development setup.

They reduce problems like:

- different Python versions
- missing extensions
- inconsistent command-line tools
- local machine setup drift

## DevContainer File

This repo has a DevContainer config at the repo root:

```text
.devcontainer/devcontainer.json
```

It is intentionally kept at the repo root because VS Code detects DevContainers from there when students open the full repository.

## Prerequisites

Install:

- Docker Desktop or Docker Engine
- Visual Studio Code
- VS Code Dev Containers extension

For WSL students:

- Use Docker Desktop with WSL integration enabled
- Open the repository from Ubuntu WSL

## Part 1: Open in VS Code

From Ubuntu or WSL:

```bash
cd /home/arjun/advanced-docker
code .
```

In VS Code:

```text
Dev Containers: Reopen in Container
```

Wait for the container to build.

## Part 2: Verify Tools

Open a VS Code terminal inside the DevContainer.

Check Python:

```bash
python --version
```

Check Docker:

```bash
docker --version
docker compose version
docker ps
```

If Docker commands fail inside the DevContainer, check:

- Docker Desktop is running
- WSL integration is enabled
- the DevContainer includes Docker-outside-of-Docker support

## Part 3: Run the GenAI App from the DevContainer

Move to the exercise:

```bash
cd exercises/02-genai-module-coach
```

Start Ollama:

```bash
docker compose up -d ollama
```

Pull the model:

```bash
docker compose exec ollama ollama pull qwen2.5:0.5b
```

Build and start the app:

```bash
docker compose up --build -d genai-chat
```

Check health:

```bash
curl http://localhost:8080/health
```

Expected:

```json
{"status":"ok"}
```

Run the smoke test:

```bash
python app/smoke_test.py http://localhost:8080
```

## Part 4: Build Images from the DevContainer

Build the bad image:

```bash
docker build -f Dockerfile.bad -t genai-chat:bad .
```

Build the production image:

```bash
docker build -f Dockerfile -t genai-chat:prod .
```

Compare:

```bash
docker images | grep genai-chat
```

## Part 5: Discuss AI-Augmented Development

Once the environment is consistent, students can safely add AI tools later:

- code assistants
- MCP servers
- Docker AI tools
- containerized agents
- security scanners

The key idea:

```text
Put the development environment in code, then every student starts from the same baseline.
```

## Module 3 Cleanup

```bash
docker compose down
```

