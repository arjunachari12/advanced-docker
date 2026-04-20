# Module 4: CI/CD with GitHub Actions and Docker

## Goal

In this module you will:

- review a GitHub Actions workflow
- build the production Docker image in CI
- generate an SBOM in CI
- scan the image with Trivy in CI
- optionally push the image to Docker Hub

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

## Part 3: Commit the Workflow

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

## Part 4: Watch the Workflow in GitHub

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
```

Download the SBOM artifact from the workflow run.

## Part 5: Optional Docker Hub Push from CI

To push from GitHub Actions, create Docker Hub credentials.

In GitHub:

```text
Repository -> Settings -> Secrets and variables -> Actions -> New repository secret
```

Create:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

Add this login step after Buildx setup:

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

Change the build step if you want to push:

```yaml
- name: Build and push image
  uses: docker/build-push-action@v6
  with:
    context: exercises/02-genai-module-coach
    file: exercises/02-genai-module-coach/Dockerfile
    platforms: linux/amd64,linux/arm64
    tags: |
      ${{ secrets.DOCKERHUB_USERNAME }}/genai-chat:latest
      ${{ secrets.DOCKERHUB_USERNAME }}/genai-chat:${{ github.sha }}
    push: true
```

For the first CI lesson, keep `load: true` and do not push. Add Docker Hub push after students understand build, SBOM, and scan.

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

