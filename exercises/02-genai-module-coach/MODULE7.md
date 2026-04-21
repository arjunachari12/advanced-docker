# Module 7: Agentic Workflows Using container-use

## Goal

In this module you will:

- understand the container-use pattern for one-shot and modular workflows
- run workflow steps in isolated containers
- compose a declarative workflow from index, debug, build, and smoke-test steps
- deploy a self-debugging doc-indexing AI stack

## Use Case

The stack indexes the module notes, validates the generated index, builds a containerized API, and exposes search and question-answer endpoints.

The workflow is intentionally small, but the pattern is real:

```text
docs
  -> index in isolated Python container
  -> debug index in isolated Python container
  -> build API image in isolated Docker CLI container
  -> smoke test the app in isolated Docker CLI container
  -> deploy doc-index API
```

This is the same shape teams use for safer agentic workflows: each step has a declared image, command, inputs, and outputs.

## What Is container-use?

For this lab, `container-use` means running each agent or automation step in a short-lived container instead of directly on your host.

This gives you:

- a fresh execution environment per step
- fewer host dependency problems
- a simple audit trail of commands
- a repeatable workflow definition
- a safer place to run AI-generated or AI-assisted tool steps

The local runner for this module is:

```text
container_use_stack/container_use.py
```

The declarative workflow is:

```text
container_use_stack/workflows/doc_index_debug.yaml
```

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
└── container_use.py
```

## Part 1: Review The Workflow

Open:

```bash
cat container_use_stack/workflows/doc_index_debug.yaml
```

The workflow has four steps:

```text
index-docs
debug-index
build-api-image
smoke-test-api
```

Each step declares:

```text
image
command
needs
```

Two steps also mount the Docker socket because they need to build or run containers.

## Part 2: Run The Full Workflow

From this folder:

```bash
cd exercises/02-genai-module-coach
```

Run:

```bash
python3 container_use_stack/container_use.py \
  container_use_stack/workflows/doc_index_debug.yaml
```

Expected result:

```text
Indexed 3 documents into out/index.json
Self-debug passed: 3 indexed docs are queryable.
Smoke test passed: Docker Notes
Workflow complete.
```

## Part 3: Inspect The Generated Index

```bash
cat container_use_stack/out/index.json
```

The index contains:

- document IDs
- summaries
- extracted keywords

The debug step checks that the index is internally consistent before the API image is built.

## Part 4: Deploy The Stack

The workflow builds this image:

```text
doc-index-ai:module7
```

Run it with Compose:

```bash
docker compose -f compose.container-use.yaml up -d
```

Open:

```text
http://localhost:8092/health
```

Search the docs:

```bash
curl "http://localhost:8092/search?q=model%20runner"
```

Ask the doc assistant:

```bash
curl "http://localhost:8092/ask?q=how%20does%20dagger%20help"
```

If Docker Model Runner is available, `/ask` uses it. If not, the API falls back to retrieved document snippets.

## Part 5: Why This Is Agentic

The workflow has a small self-debug loop:

```text
build index -> inspect index -> fail early if broken
```

In a larger agentic workflow, an AI coding agent could generate or update docs, then this workflow would isolate the generated tool execution in containers before accepting the result.

The important safety habit:

```text
Do not let one agent step directly mutate everything on the host.
Give it a container, a narrow mount, and a clear output.
```

## Part 6: Extend It

Try one change:

- add a new Markdown file under `container_use_stack/docs`
- rerun the workflow
- search for the new topic

Then try a deliberate break:

- edit `debug_index.py` to require four docs
- rerun the workflow
- notice that the image build is blocked

## Cleanup

```bash
docker compose -f compose.container-use.yaml down
docker rmi doc-index-ai:module7
```
