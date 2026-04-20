# Exercise 3: Simple DevContainer

This tiny exercise shows the basic DevContainer workflow without any Docker Compose or GenAI setup.

## Goal

Use a checked-in DevContainer file to give every student the same Python environment.

## Files

```text
exercises/03-simple-devcontainer/
├── .devcontainer/
│   └── devcontainer.json
├── hello.py
├── test_hello.py
└── README.md
```

## Open In A DevContainer

From Ubuntu or WSL:

```bash
cd /path/to/advanced-docker/exercises/03-simple-devcontainer
code .
```

In VS Code:

```text
Dev Containers: Reopen in Container
```

When the container starts, the `postCreateCommand` runs:

```bash
python --version && python hello.py
```

## Try It

Open a terminal inside the DevContainer:

```bash
python --version
python hello.py
python -m unittest test_hello.py
```

Expected app output:

```text
Hello from a Python DevContainer!
```

## What To Notice

- The Python version comes from `.devcontainer/devcontainer.json`.
- VS Code opens the folder inside the container.
- The source files stay on your machine, but commands run in the container.
