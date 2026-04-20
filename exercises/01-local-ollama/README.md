# Exercise 1: Run a Local Ollama Model in Docker

## Goal

Run Ollama as a Docker container, pull a small local model, and interact with it from:

- inside the Ollama container, and
- the Ubuntu host shell through Ollama's HTTP API.

This exercise works on regular Ubuntu on a VM and Ubuntu inside Windows WSL 2.

## Model

Use `qwen2.5:0.5b`.

It is a compact model suitable for classroom labs and lower-resource machines. Ollama lists the `0.5b` variant at about 398 MB, while still giving useful instruction-following behavior for short lab prompts.

Reference: <https://ollama.com/library/qwen2.5>

## Before You Start

### Ubuntu on a VM

Check Docker:

```bash
docker --version
docker compose version
docker run hello-world
```

If Docker is installed but your user cannot run it, add your user to the Docker group and log out/in:

```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

### Ubuntu on Windows WSL 2

Use Docker Desktop on Windows with WSL integration enabled.

Check from Ubuntu WSL:

```bash
docker --version
docker compose version
docker run hello-world
```

If Docker commands fail in WSL:

- Start Docker Desktop on Windows.
- Open Docker Desktop settings.
- Enable WSL integration for your Ubuntu distro.
- Restart the Ubuntu WSL terminal.

## Step 1: Start Ollama in Docker

```bash
docker volume create ollama

docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama:latest
```

Check the container:

```bash
docker ps --filter name=ollama
docker logs ollama --tail 30
```

## Step 2: Pull the Small Model

```bash
docker exec -it ollama ollama pull qwen2.5:0.5b
```

List models:

```bash
docker exec -it ollama ollama list
```

## Step 3: Interact from Inside the Container

Run a one-shot prompt:

```bash
docker exec -it ollama ollama run qwen2.5:0.5b "Explain Docker containers in two short sentences."
```

Start an interactive chat:

```bash
docker exec -it ollama ollama run qwen2.5:0.5b
```

Try:

```text
What is the difference between an image and a container?
```

Exit the chat with:

```text
/bye
```

## Step 4: Interact from Ubuntu with HTTP

From the Ubuntu VM or WSL shell:

```bash
curl http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:0.5b",
    "stream": false,
    "messages": [
      {
        "role": "user",
        "content": "Give me three Dockerfile best practices."
      }
    ]
  }'
```

Expected result:

- The response is JSON.
- The answer text is under `message.content`.

## Step 5: Clean Up

Stop and remove the container:

```bash
docker stop ollama
docker rm ollama
```

Keep the model cache volume for the next exercise:

```bash
docker volume ls | grep ollama
```

Remove the model cache only if you want to free disk space:

```bash
docker volume rm ollama
```

## Troubleshooting

### Port 11434 Is Already in Use

You may already have Ollama running on the host.

Check:

```bash
curl http://localhost:11434/api/tags
```

If that works, either use the existing service or stop the old container:

```bash
docker ps --filter publish=11434
```

### WSL Cannot Reach Docker

Restart Docker Desktop and the WSL distro:

```powershell
wsl --shutdown
```

Then reopen Ubuntu WSL and retry:

```bash
docker ps
```

### Pull Is Slow

The first pull downloads the model. Keep the `ollama` Docker volume so later exercises reuse the same model.
