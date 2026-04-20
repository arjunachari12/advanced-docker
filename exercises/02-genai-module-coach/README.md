# Exercise 2: Production-Ready Docker for a Simple GenAI App

## What You Will Learn

This exercise uses one simple Python GenAI chat app that calls a local Ollama container.

Use this same app to teach:

- Module 1: Docker image build best practices, multi-stage builds, and multi-architecture builds with Buildx
- Module 2: Image security, SBOM generation with Syft, and vulnerability scanning with Trivy
- Module 3: DevContainer basics for a repeatable development environment
- Module 4: CI/CD ideas for build, scan, SBOM, and push

## Folder Contents

```text
exercises/02-genai-module-coach/
├── app/
│   ├── main.py
│   └── smoke_test.py
├── Dockerfile
├── Dockerfile.bad
├── compose.yaml
├── requirements.txt
└── README.md
```

## Before You Start

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

Open Ubuntu again and test:

```bash
docker ps
docker compose version
```

## Start Ollama and the GenAI App

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

Build and run the app:

```bash
docker compose up --build -d genai-chat
```

Open the app:

```text
http://localhost:8080
```

Test with curl:

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

## Module 1: Docker Build Best Practices

This folder has two Dockerfiles.

Wrong way:

```text
Dockerfile.bad
```

Right way:

```text
Dockerfile
```

### Build the Bad Image

```bash
docker build -f Dockerfile.bad -t genai-chat:bad .
```

Problems in `Dockerfile.bad`:

- Uses `python:latest`
- Copies all files before installing dependencies
- Installs packages as root
- Uses development reload mode
- Sets `OLLAMA_BASE_URL` to `localhost`, which is wrong inside a container

### Build the Production Image

```bash
docker build -f Dockerfile -t genai-chat:prod .
```

Good practices in `Dockerfile`:

- Uses multi-stage build
- Copies `requirements.txt` before app code for better cache reuse
- Uses a slim Python runtime image
- Runs as a non-root user
- Adds a container health check
- Uses Compose service DNS: `http://ollama:11434`

### Compare Images

```bash
docker images | grep genai-chat
```

Compare layers:

```bash
docker history genai-chat:bad
docker history genai-chat:prod
```

## Module 1: Multi-Architecture Build with Docker Buildx

Goal:

Build one image tag that can run on both:

- `linux/amd64`
- `linux/arm64`

### Step 1: Check Buildx

```bash
docker buildx version
docker buildx ls
```

### Step 2: Create a Buildx Builder

Use the Docker container driver for multi-architecture builds:

```bash
docker buildx create --use --driver docker-container
```

Bootstrap the builder:

```bash
docker buildx inspect --bootstrap
```

### Step 3: Test a Local Build First

Use `--load` for a single-platform local test:

```bash
docker buildx build -t genai-chat:buildx-local --load .
```

Run it:

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

### Step 4: Login to Docker Hub

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

### Step 5: Build and Push Multi-Architecture Image

Replace `yourname` with your Docker Hub username.

Simple command:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t yourname/genai-chat:latest \
  --push .
```

Using an environment variable:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t "$DOCKERHUB_USERNAME/genai-chat:latest" \
  --push .
```

Versioned tag:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t "$DOCKERHUB_USERNAME/genai-chat:1.0.0" \
  -t "$DOCKERHUB_USERNAME/genai-chat:latest" \
  --push .
```

### Step 6: Inspect the Multi-Arch Image

```bash
docker buildx imagetools inspect "$DOCKERHUB_USERNAME/genai-chat:latest"
```

Look for:

```text
linux/amd64
linux/arm64
```

### Important Notes

- `--load` works for local single-platform builds.
- `--push` is used for real multi-platform builds.
- Docker cannot load a multi-platform manifest list into the classic local image store.
- If arm64 builds are slow on an amd64 machine, that is normal because emulation may be used.

## Module 2: Security, SBOM, and Vulnerability Scanning

For this module, use the bad image first so students can inspect and scan it.

### Build an Insecure Image

```bash
docker build -f Dockerfile.bad -t insecure-image:latest .
```

Check it:

```bash
docker images | grep insecure-image
```

## Module 2: Syft SBOM

Syft creates a Software Bill of Materials.

### Install Syft

```bash
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh
```

Move it into your path:

```bash
sudo mv ./bin/syft /usr/local/bin/
```

Check version:

```bash
syft version
```

### Generate SBOM Output

Show packages in the terminal:

```bash
syft insecure-image:latest
```

Table output:

```bash
syft insecure-image:latest -o table
```

JSON output:

```bash
syft insecure-image:latest -o json > sbom.json
```

SPDX JSON output:

```bash
syft insecure-image:latest -o spdx-json > sbom.spdx.json
```

CycloneDX JSON output:

```bash
syft insecure-image:latest -o cyclonedx-json > sbom.cyclonedx.json
```

### What to Discuss

- What packages are inside the image?
- Which packages came from the OS?
- Which packages came from Python?
- Why is `python:latest` risky?
- Why is SBOM useful in CI/CD?

## Module 2: Trivy Vulnerability Scanning

Trivy scans images for known vulnerabilities.

### Install Trivy on Ubuntu

```bash
sudo apt update
sudo apt install wget apt-transport-https gnupg lsb-release -y
```

Add the Trivy repository key:

```bash
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
```

Add the repository:

```bash
echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | sudo tee -a /etc/apt/sources.list.d/trivy.list
```

Install Trivy:

```bash
sudo apt update
sudo apt install trivy -y
```

Check version:

```bash
trivy --version
```

### Scan the Insecure Image

```bash
trivy image insecure-image:latest
```

Scan only high and critical vulnerabilities:

```bash
trivy image --severity HIGH,CRITICAL insecure-image:latest
```

Ignore unfixed vulnerabilities:

```bash
trivy image --ignore-unfixed insecure-image:latest
```

Save JSON output:

```bash
trivy image -f json -o trivy-report.json insecure-image:latest
```

### Scan the Production Image

Build the production image:

```bash
docker build -f Dockerfile -t genai-chat:prod .
```

Scan it:

```bash
trivy image genai-chat:prod
```

Compare:

```bash
trivy image --severity HIGH,CRITICAL insecure-image:latest
trivy image --severity HIGH,CRITICAL genai-chat:prod
```

### What to Discuss

- Did the production image reduce the attack surface?
- Are there fewer packages?
- Are there fewer critical or high vulnerabilities?
- Which vulnerabilities are from the base image?
- Which vulnerabilities are from app dependencies?

## Optional: Docker Scout

If Docker Scout is available:

```bash
docker scout cves insecure-image:latest
docker scout recommendations insecure-image:latest
```

## Module 3: DevContainer Discussion

This repo has a DevContainer file at:

```text
.devcontainer/devcontainer.json
```

Use it later to teach:

- consistent developer environments
- Docker CLI inside a dev container
- VS Code Docker extension
- GitHub Actions extension
- AI/MCP tooling as a next step

## Module 4: CI/CD Discussion

This repo has a GitHub Actions workflow at:

```text
.github/workflows/genai-chat-build-scan-sbom.yml
```

Use it later to teach:

- build image in CI
- generate SBOM in CI
- scan image in CI
- upload scan results
- push to Docker Hub after checks pass

## Cleanup

Stop app containers:

```bash
docker compose down
```

Remove the Ollama model volume only if you want to free disk space:

```bash
docker compose down -v
```

Remove temporary images:

```bash
docker rmi genai-chat:bad genai-chat:prod genai-chat:buildx-local insecure-image:latest
```

