# Container-Use Style Doc Indexing Stack

This folder is a small teaching project that demonstrates the `container-use` pattern with tools you can run locally.

In this repo, we simulate `container-use` with a tiny Python runner:

```text
container_use.py
```

It reads a declarative workflow file and runs each step in an isolated container.

## What This Code Does

This product is a small AI-powered documentation assistant.

It:

- reads Markdown notes from `docs/`
- builds a JSON search index
- validates that index before promotion
- builds a containerized API
- lets you search the docs or ask questions over them

The flow is:

```text
docs
  -> index docs
  -> self-check the generated index
  -> build API image
  -> smoke test the image
  -> run the doc assistant
```

That gives students the main agentic workflow idea:

```text
generate something
  -> inspect it in an isolated container
  -> only promote it if checks pass
```

## Why This Matters

Even without a full coding agent, this is already useful:

- each step runs in a clean container
- failures stop the workflow early
- the host machine stays less coupled to tool setup
- the workflow is easy to read, rerun, and extend

This is the same pattern larger AI systems use when they let an agent write code, run tests, inspect results, and decide the next step.

## Files

```text
container_use_stack/
├── app/
│   ├── Dockerfile
│   └── main.py
├── docs/
│   ├── dagger.md
│   ├── docker.md
│   └── model-runner.md
├── tools/
│   ├── debug_index.py
│   ├── index_docs.py
│   └── smoke_container.sh
├── workflows/
│   └── doc_index_debug.yaml
├── container_use.py
└── README.md
```

## The Workflow Definition

The declarative workflow lives here:

[doc_index_debug.yaml](/home/arjun/advanced-docker/exercises/02-genai-module-coach/container_use_stack/workflows/doc_index_debug.yaml)

It defines four steps:

```text
index-docs
debug-index
build-api-image
smoke-test-api
```

In plain English:

1. create the index
2. verify the index is valid
3. build the API container
4. run a quick smoke test

## How The Runner Works

The runner lives here:

[container_use.py](/home/arjun/advanced-docker/exercises/02-genai-module-coach/container_use_stack/container_use.py)

It:

- reads the YAML workflow
- starts a short-lived container per step
- mounts this folder into `/workspace`
- runs the declared command
- stops the workflow if a step fails

That is the core `container-use` idea in a very small, teachable form.

## Run The Workflow

From the exercise folder:

```bash
cd /home/arjun/advanced-docker/exercises/02-genai-module-coach
python3 container_use_stack/container_use.py \
  container_use_stack/workflows/doc_index_debug.yaml
```

Expected shape of output:

```text
Indexed 3 documents into out/index.json
Self-debug passed: 3 indexed docs are queryable.
Smoke test passed: Docker Notes
Workflow complete.
```

## Start The API

After the workflow builds the image, run:

```bash
docker compose -f compose.container-use.yaml up -d
```

Then test:

```bash
curl http://localhost:8092/health
curl http://localhost:8092/debug
curl "http://localhost:8092/search?q=model%20runner"
curl "http://localhost:8092/ask?q=how%20does%20dagger%20help"
```

What the endpoints do:

- `/health` confirms the service is up
- `/debug` reports index health
- `/search` returns matching docs
- `/ask` tries a local model first, then falls back to retrieval if needed

## Two Ways To Think About container-use

### Option 1: Agent-driven workflow

If you later connect an MCP-compatible coding client, the client can act as the planner and use a container workflow like this as its execution layer.

That gives you a loop like:

```text
prompt
  -> agent chooses a step
  -> step runs in container
  -> result is inspected
  -> next step is chosen
```

### Option 2: Manual simulation

This is the path already implemented in this repo.

You act like the agent brain:

```text
write workflow
  -> run step in container
  -> inspect artifact
  -> accept or fix
```

This is still very valuable because it teaches:

- isolated execution
- reproducible environments
- inspect-before-promote workflow design
- how larger agent systems stay safer

## Tested Locally

This stack was tested locally with:

```bash
python3 container_use_stack/container_use.py \
  container_use_stack/workflows/doc_index_debug.yaml
docker compose -f compose.container-use.yaml up -d --force-recreate
curl http://localhost:8092/health
curl http://localhost:8092/debug
curl "http://localhost:8092/search?q=model%20runner"
curl "http://localhost:8092/ask?q=how%20does%20dagger%20help"
```

## Cleanup

```bash
docker compose -f compose.container-use.yaml down
docker rmi doc-index-ai:module7
```
