# Module 4: CI/CD with GitHub Actions and Docker

## Goal

In this module you will:

- review a GitHub Actions workflow
- build the production Docker image in CI
- generate an SBOM in CI
- scan the image with Trivy in CI
- push the image to Docker Hub after the scan step passes

The workflow file is at the repo root:

```text
.github/workflows/genai-chat-build-scan-sbom.yml
```

Run local commands from this folder:

```bash
cd exercises/02-genai-module-coach
```

## Part 1: Review the Workflow

Open the workflow:

```bash
cat ../../.github/workflows/genai-chat-build-scan-sbom.yml
```

The workflow runs on:

```text
push to main
pull_request
```

Main steps:

```text
Checkout
Set up Docker Buildx
Build image
Generate SBOM with Syft
Upload SBOM artifact
Scan image with Trivy
Upload Trivy SARIF results
Login to Docker Hub
Tag image for Docker Hub
Push image to Docker Hub
```

## Part 2: Test the Same Build Locally

Before pushing to GitHub, make sure the Dockerfile builds locally.

```bash
docker build -f Dockerfile -t genai-chat:ci-test .
```

Run the image:

```bash
docker run --rm -d \
  --name genai-chat-ci-test \
  -p 8082:8080 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  genai-chat:ci-test
```

Check health:

```bash
curl http://localhost:8082/health
```

Expected:

```json
{"status":"ok"}
```

Clean up:

```bash
docker rm -f genai-chat-ci-test
```

## Part 3: Configure Docker Hub Secrets

Create a Docker Hub repository named:

```text
genai-chat
```

Create a Docker Hub access token, then add these GitHub repository secrets:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

In GitHub:

```text
Repository -> Settings -> Secrets and variables -> Actions -> New repository secret
```

The workflow pushes these tags on `push` to `main`:

```text
DOCKERHUB_USERNAME/genai-chat:latest
DOCKERHUB_USERNAME/genai-chat:<git-sha>
```

Pull requests still build, generate an SBOM, and scan, but they do not push to Docker Hub.

## Part 4: Commit the Workflow

From the repo root:

```bash
git status
git add .github/workflows/genai-chat-build-scan-sbom.yml
git add .devcontainer/devcontainer.json
git add exercises/02-genai-module-coach/MODULE4.md
git commit -m "Add CI/CD workflow for GenAI Docker app"
```

Push:

```bash
git push
```

## Part 5: Watch the Workflow in GitHub

Open your GitHub repository.

Go to:

```text
Actions
```

Select:

```text
genai-chat-build-scan-sbom
```

Check that these steps pass:

```text
Build image
Generate SBOM with Syft
Scan image with Trivy
Push image to Docker Hub
```

Download the SBOM artifact from the workflow run.

## Part 6: Troubleshooting

### Workflow Does Not Start

Check that the file is committed at:

```text
.github/workflows/genai-chat-build-scan-sbom.yml
```

### SARIF Upload Fails

Check workflow permissions:

```yaml
permissions:
  contents: read
  security-events: write
  actions: read
```

### Docker Hub Push Fails

Check:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

Also confirm the Docker Hub token has permission to push images.

## Module 4 Cleanup

Remove the local CI test image if needed:

```bash
docker rmi genai-chat:ci-test
```
