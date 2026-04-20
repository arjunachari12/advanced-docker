# Module 1: Docker Build Best Practices and Multi-Architecture Builds

## Goal

In this module you will:

- compare a bad Dockerfile with a production-ready Dockerfile
- build Docker images locally
- understand multi-stage builds
- use Docker Buildx for multi-architecture builds
- push one image tag to Docker Hub for both `linux/amd64` and `linux/arm64`

Run all commands from this folder:

```bash
cd exercises/02-genai-module-coach
```

## Part 1: Understand the Application

The app is a small Python FastAPI service.

Important files:

```text
app/main.py
requirements.txt
compose.yaml
Dockerfile
Dockerfile.bad
```

The app talks to Ollama by HTTP.

Inside Docker Compose, the app uses:

```text
http://ollama:11434
```

That works because `ollama` is the Compose service name.

## Part 2: Run the App with Docker Compose

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

Check containers:

```bash
docker compose ps
```

Check health:

```bash
curl http://localhost:8080/health
```

Expected:

```json
{"status":"ok"}
```

Check Ollama readiness from the app:

```bash
curl http://localhost:8080/ready
```

Send a message:

```bash
curl http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain containers in one short paragraph."}'
```

## Part 3: Build the Bad Image

Build the intentionally bad image:

```bash
docker build -f Dockerfile.bad -t genai-chat:bad .
```

Look at `Dockerfile.bad`:

```bash
cat Dockerfile.bad
```

Problems to discuss:

- `python:latest` changes over time
- app files are copied before dependencies are installed
- packages are installed as root
- development reload mode is used in the container
- `localhost` is used for Ollama, which is wrong from inside another container

## Part 4: Build the Production Image

Build the production image:

```bash
docker build -f Dockerfile -t genai-chat:prod .
```

Look at the Dockerfile:

```bash
cat Dockerfile
```

Good practices to discuss:

- multi-stage build
- dependency layer caching
- slim runtime image
- virtual environment copied from builder stage
- non-root user
- health check
- production command without reload mode

## Part 5: Compare the Images

List image sizes:

```bash
docker images | grep genai-chat
```

Inspect image layers:

```bash
docker history genai-chat:bad
docker history genai-chat:prod
```

Question:

```text
Which image is smaller and why?
```

## Part 6: Build with Docker Buildx

Check Buildx:

```bash
docker buildx version
docker buildx ls
```

Build a local image with Buildx:

```bash
docker buildx build -t genai-chat:buildx-local --load .
```

Run it locally:

```bash
docker run --rm -d \
  --name genai-chat-buildx-local \
  -p 8081:8080 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  genai-chat:buildx-local
```

Check health:

```bash
curl http://localhost:8081/health
```

Clean up:

```bash
docker rm -f genai-chat-buildx-local
```

## Part 7: Create a Multi-Architecture Builder

Use a `docker-container` builder for multi-architecture builds:

```bash
docker buildx create --use --driver docker-container
```

Bootstrap it:

```bash
docker buildx inspect --bootstrap
```

Check it:

```bash
docker buildx ls
```

## Part 8: Push a Multi-Architecture Image to Docker Hub

Login:

```bash
docker login
```

Set your Docker Hub username:

```bash
export DOCKERHUB_USERNAME=yourname
```

Example:

```bash
export DOCKERHUB_USERNAME=arjunachari12
```

Build and push for AMD64 and ARM64:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t "$DOCKERHUB_USERNAME/genai-chat:latest" \
  --push .
```

Push both a version tag and `latest`:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t "$DOCKERHUB_USERNAME/genai-chat:1.0.0" \
  -t "$DOCKERHUB_USERNAME/genai-chat:latest" \
  --push .
```

Inspect the pushed image:

```bash
docker buildx imagetools inspect "$DOCKERHUB_USERNAME/genai-chat:latest"
```

Look for:

```text
linux/amd64
linux/arm64
```

## Notes

- `--load` is for local single-platform builds.
- `--push` is for multi-platform builds.
- Docker cannot load a multi-platform manifest list into the classic local image store.
- ARM64 builds can be slow on AMD64 machines because emulation may be used.

## Module 1 Cleanup

```bash
docker rm -f genai-chat-buildx-local
docker compose down
```

