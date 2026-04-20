# Module 2: SBOM and Vulnerability Scanning

Run these commands from `exercises/02-genai-module-coach`.

## Build the Production Image

```bash
docker build -t genai-chat:prod .
```

## Generate an SBOM with Syft

Install Syft:

```bash
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b ./bin
```

Generate SPDX JSON:

```bash
./bin/syft genai-chat:prod -o spdx-json > sbom.spdx.json
```

Inspect packages:

```bash
./bin/syft genai-chat:prod
```

## Scan with Trivy

Install Trivy on Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo gpg --dearmor -o /usr/share/keyrings/trivy.gpg
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install -y trivy
```

Scan:

```bash
trivy image --severity HIGH,CRITICAL genai-chat:prod
```

## Scan with Docker Scout

```bash
docker scout cves genai-chat:prod
docker scout recommendations genai-chat:prod
```

## Discussion Points

- The production Dockerfile uses a slim pinned family instead of `python:latest`.
- Dependencies are installed in a builder stage.
- The runtime stage runs as a non-root user.
- The image has a health check.
- SBOM output can be stored as a CI artifact.
- Vulnerability scans can fail a pull request when critical issues are found.

