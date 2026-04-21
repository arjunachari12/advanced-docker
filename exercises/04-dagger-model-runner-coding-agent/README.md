# Mini Challenge: Build a Coding Agent with Dagger + Docker Model Runner

## Goal

Build a simple AI coding agent that:

1. takes a feature request
2. uses a local model to generate Python code
3. saves the code into `app.py`
4. runs the code inside a container
5. displays the output

## What This Project Does

This folder contains a single-agent coding workflow. Dagger orchestrates the steps and Docker Model Runner provides the local LLM.

The flow is:

```text
prompt -> Docker Model Runner -> generate code -> reviewer pass -> save app.py -> run in python container -> print output
```

## Files

```text
exercises/04-dagger-model-runner-coding-agent/
├── dagger.json
├── pyproject.toml
├── README.md
└── src/
    └── mini_coding_agent/
        ├── __init__.py
        └── main.py
```

## Prerequisites

- Docker Model Runner enabled
- `ai/llama3.2` available locally
- Dagger CLI installed

Check:

```bash
docker model status
docker model list
dagger version
```

If needed:

```bash
docker model pull ai/llama3.2
```

## Run The Challenge

Go to this folder:

```bash
cd exercises/04-dagger-model-runner-coding-agent
```

Generate code and run it:

```bash
dagger call run-app \
  --feature-request="Create a Python function that returns the factorial of a number and print factorial of 5."
```

Expected output:

```text
Program output:
120
```

## Save The Generated File

Export `app.py` to a local folder:

```bash
mkdir -p generated
dagger call save-app \
  --feature-request="Create a Python function that returns the factorial of a number and print factorial of 5." \
  export --path generated/app.py
```

Then inspect it:

```bash
cat generated/app.py
python3 generated/app.py
```

## Dagger Functions

List available functions:

```bash
dagger functions
```

You should see:

```text
generate-code
save-app
run-app
```

## Bonus

The project includes a small reviewer pass already. If the first generated file is not valid runnable Python, or fails at execution time, the code is sent back to the local model with feedback and retried once.
