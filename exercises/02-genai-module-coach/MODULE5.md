# Module 5: Agentic Workflow Composition with Dagger

## Goal

In this module you will:

- understand Dagger and the "workflows as code" idea
- define a pipeline with the Dagger Python SDK
- build and test a tiny containerized AI agent
- run the agent against a local Ollama endpoint
- keep an offline fallback for demos and troubleshooting
- publish the agent image to a registry from the Dagger workflow

## Use Case

The agent in this module is a small DevOps release coach.

The user gives it a task like:

```text
Create a release plan for the agent image
```

The agent asks local Ollama for a short plan with concrete container commands. This helps a student or operator decide what to do next when shipping a containerized AI app:

```text
build -> test -> scan -> publish
```

The point is not to create a magical autonomous production bot. The point is to show how an AI helper can be packaged as a container and then controlled by a Dagger workflow.

## What Is Dagger?

Dagger lets you write CI/CD and automation workflows as regular code.

Instead of spreading logic across shell scripts, YAML, and local machine state, a Dagger workflow can compose:

- source directories
- containers
- tests
- registry publishing
- secrets
- LLM-backed tools

The important idea:

```text
Treat the workflow itself like application code.
```

In this module, the Dagger workflow is written in Python at:

```text
src/genai_agent_pipeline/main.py
```

The tiny agent app is at:

```text
agent_app/
```

## Files

```text
exercises/02-genai-module-coach/
├── agent_app/
│   ├── Dockerfile
│   ├── agent.py
│   └── test_agent.py
├── src/
│   └── genai_agent_pipeline/
│       ├── __init__.py
│       └── main.py
├── dagger.json
├── pyproject.toml
└── MODULE5.md
```

## Prerequisites

Install:

- Docker Desktop or Docker Engine
- Dagger CLI

Check:

```bash
docker ps
dagger version
```

Run commands from this folder:

```bash
cd exercises/02-genai-module-coach
```

## Part 1: Start Ollama

Start Ollama from the earlier module:

```bash
docker compose up -d ollama
docker compose exec ollama ollama pull qwen2.5:0.5b
```

Ollama is exposed on:

```text
http://localhost:11434
```

## Part 2: Run The Agent Locally

The agent uses Ollama by default.

```bash
python3 agent_app/agent.py "Create a release plan for an AI agent image"
```

Expected shape:

```text
1. Build the image...
2. Run checks...
3. Publish...
```

The exact words can vary because Ollama is generating the response.

If Ollama returns a free-form answer instead of three numbered steps, the agent normalizes the output and includes a short `Ollama note`.

If Ollama is unavailable, the agent prints a deterministic fallback and explains why it could not reach the LLM.

To force the offline fallback:

```bash
python3 agent_app/agent.py --offline "Create a release plan for an AI agent image"
```

Run tests:

```bash
cd agent_app
python3 -m unittest test_agent.py
cd ..
```

## Part 3: Build The Agent Container Locally

```bash
docker build -t genai-agent:local ./agent_app
```

Run it with Ollama from a container:

```bash
docker run --rm \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e OLLAMA_MODEL=qwen2.5:0.5b \
  genai-agent:local "Explain why workflows as code helps teams"
```

## Part 4: Inspect The Dagger Functions

List the workflow functions:

```bash
dagger functions
```

You should see:

```text
build-agent
test-agent
run-agent
run-agent-offline
run-agent-with-llm
dry-run-deploy
publish-agent
```

Each function is regular Python code in:

```text
src/genai_agent_pipeline/main.py
```

## Part 5: Test With Dagger

Run the tests inside a clean Python container:

```bash
dagger call test-agent
```

Run the built agent container through Dagger. This calls Ollama at `http://host.docker.internal:11434`:

```bash
dagger call run-agent --task="Create a release plan for the agent image"
```

This is the first composition:

```text
source directory -> test container -> built agent container -> stdout
```

If you need a different Ollama URL or model, use:

```bash
dagger call run-agent-with-llm \
  --task="Give three steps to ship this agent safely" \
  --ollama-base-url="http://host.docker.internal:11434" \
  --model="qwen2.5:0.5b"
```

To test without Ollama:

```bash
dagger call run-agent-offline --task="Create a release plan for the agent image"
```

## Part 6: Dry-Run Deployment

Before publishing, run the deployment gate:

```bash
dagger call dry-run-deploy --image=ttl.sh/genai-agent-demo
```

The workflow runs tests, runs the agent, and then prints the publish command.

## Part 7: Publish The Agent Image

For a temporary public registry, use `ttl.sh`:

```bash
dagger call publish-agent --image=ttl.sh/genai-agent-demo-$(date +%s):1h
```

For Docker Hub, log in first:

```bash
docker login
dagger call publish-agent --image=DOCKERHUB_USERNAME/genai-agent:latest
```

The publish workflow does this:

```text
test-agent -> run-agent with Ollama -> build-agent -> publish image
```

That is the core agentic workflow composition pattern.

## Part 8: What To Discuss

- What changed when the workflow moved from YAML to Python?
- Which parts are reproducible because they run in containers?
- Why is local Ollama useful for a classroom AI workflow?
- How would you add SBOM generation or Trivy scanning as another Dagger function?
- What should happen before `publish-agent` is allowed to deploy?

## Troubleshooting

### Dagger Cannot Reach Docker

Check:

```bash
docker ps
```

If Docker fails in WSL, confirm Docker Desktop is running and WSL integration is enabled.

### Dagger Shows Cloud Or Telemetry Messages

The local workflow can still pass. To hide the Dagger Cloud setup prompt, run:

```bash
export DAGGER_NO_NAG=1
```

If you still see telemetry export warnings, treat them as non-blocking unless the Dagger command exits with an error.

### Ollama Is Not Reachable From The Agent Container

Use:

```text
http://host.docker.internal:11434
```

If that does not work on your Linux setup, use the host IP address that containers can reach.

## Module 5 Cleanup

Remove local images if needed:

```bash
docker rmi genai-agent:local genai-agent:module5-test
```
