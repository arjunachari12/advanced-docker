# Module 6: GenAI Containerization with Docker Model Runner

## Goal

In this module you will:

- understand Docker Model Runner use cases
- pull and run a local model as a Docker-managed model artifact
- call the model from a containerized GenAI app
- discuss CPU and GPU configuration tradeoffs
- deploy a small GenAI app that uses Model Runner instead of an Ollama container

## Use Case

The app in this module answers beginner Docker questions by calling a local model through Docker Model Runner.

The pattern is:

```text
Browser or curl
  -> containerized FastAPI app
  -> Docker Model Runner API
  -> local model image
```

This is useful when you want local AI inference without running a separate model server container in your Compose stack. Docker manages the model lifecycle, storage, and API surface.

## What Is Docker Model Runner?

Docker Model Runner lets Docker pull, store, run, and serve AI models as OCI artifacts. It exposes OpenAI-compatible and Ollama-compatible APIs, so containerized apps can call local models without changing much application code.

Common use cases:

- local GenAI app development
- private AI assistants on a laptop or workstation
- testing OpenAI-compatible code without cloud APIs
- packaging GGUF or Safetensors models as registry artifacts
- running CPU-friendly models locally and GPU-backed models on supported hosts

## Files

```text
exercises/02-genai-module-coach/
├── model_runner_app/
│   ├── main.py
│   └── smoke_test.py
├── Dockerfile.model-runner
├── compose.model-runner.yaml
└── MODULE6.md
```

## Prerequisites

Install or enable:

- Docker Desktop or Docker Engine with Docker Model Runner
- Docker Compose v2
- A supported local model

Check Model Runner:

```bash
docker model status
docker model list
```

If Model Runner is not enabled in Docker Desktop:

```bash
docker desktop enable model-runner
```

Host-side TCP access is useful for calling the API from your host shell:

```bash
docker desktop enable model-runner --tcp 12434
```

The app in this module runs in a container, so it uses:

```text
http://model-runner.docker.internal/engines/v1
```

## Part 1: Pull A Small Model

This module uses `ai/smollm2` because it is small enough for most student machines.

```bash
docker model pull ai/smollm2
docker model list
```

Optional CLI test:

```bash
docker model run ai/smollm2 "Explain Docker Model Runner in one sentence."
```

If the CLI streams for too long, stop it with `Ctrl+C`. The app uses the HTTP API with a token limit.

## Part 2: Check The Model Runner API From A Container

Run:

```bash
docker run --rm curlimages/curl:8.16.0 \
  http://model-runner.docker.internal/engines/v1/models
```

Expected shape:

```json
{"object":"list","data":[{"id":"ai/smollm2:latest"}]}
```

## Part 3: Review The App

Open:

```text
model_runner_app/main.py
```

Important environment variables:

```text
MODEL_RUNNER_BASE_URL=http://model-runner.docker.internal/engines/v1
MODEL_RUNNER_MODEL=ai/smollm2:latest
```

The app calls:

```text
POST /engines/v1/chat/completions
```

That is the OpenAI-compatible chat endpoint exposed by Docker Model Runner.

## Part 4: Build And Run The App

```bash
docker compose -f compose.model-runner.yaml up --build -d
```

Open:

```text
http://localhost:8091
```

Check health:

```bash
curl http://localhost:8091/health
```

Expected:

```json
{"status":"ok"}
```

Check Model Runner readiness:

```bash
curl http://localhost:8091/ready
```

Run the smoke test:

```bash
python3 model_runner_app/smoke_test.py http://localhost:8091
```

## Part 5: CPU, GPU, And Model Compatibility

Docker Model Runner can use different inference engines depending on your host and model format.

Key ideas:

- `llama.cpp` is the default engine and is best for CPU-friendly GGUF models.
- `vLLM` is designed for higher-throughput workloads and requires supported NVIDIA GPU setups.
- Diffusers is used for image generation models and also needs supported GPU configuration.
- Small quantized models are better for classroom demos.
- Larger models need more RAM, more VRAM, and a longer first pull.

Check current backend status:

```bash
docker model status
docker model ps
```

Inspect a model:

```bash
docker model inspect ai/smollm2
```

## Part 6: Swap Models

Pull another compatible model image:

```bash
docker model pull MODEL_NAME
```

Then run the app with a different model:

```bash
MODEL_RUNNER_MODEL=MODEL_NAME docker compose -f compose.model-runner.yaml up --build -d
```

Use a model that your CPU or GPU can actually run. Model image compatibility depends on:

- model format
- inference engine
- hardware backend
- available memory
- context size

## Troubleshooting

### `docker model` Is Not Recognized

Update Docker Desktop or Docker Engine and enable Docker Model Runner.

### App Cannot Reach Model Runner

The app must call:

```text
http://model-runner.docker.internal/engines/v1
```

If you run on Docker Engine and that DNS name is unavailable, add a host mapping or use the host gateway address documented for your environment.

### Host Curl To `localhost:12434` Fails

Enable host-side TCP support:

```bash
docker desktop enable model-runner --tcp 12434
```

The containerized app does not require this when `model-runner.docker.internal` works.

### Model Output Looks Weak

Small models are fast and classroom-friendly, but they can produce weak answers. Try:

- a larger compatible model
- a lower temperature
- a more specific prompt
- more CPU/GPU resources

## Module 6 Cleanup

```bash
docker compose -f compose.model-runner.yaml down
docker model unload ai/smollm2
```
