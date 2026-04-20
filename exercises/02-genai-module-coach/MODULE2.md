# Module 2: Image Security, SBOM, and Vulnerability Scanning

## Goal

In this module you will:

- build an intentionally insecure image
- generate an SBOM with Syft
- scan images with Trivy
- compare the bad image with the production image

Run all commands from this folder:

```bash
cd exercises/02-genai-module-coach
```

## Part 1: Build the Insecure Image

Build from the bad Dockerfile:

```bash
docker build -f Dockerfile.bad -t insecure-image:latest .
```

Check the image:

```bash
docker images | grep insecure-image
```

Inspect the Dockerfile:

```bash
cat Dockerfile.bad
```

Security problems to discuss:

- floating base image tag: `python:latest`
- root package installation
- more packages than needed
- development server reload mode
- no health check
- bad container-to-container networking assumption

## Part 2: Install Syft

Syft creates an SBOM, which means Software Bill of Materials.

Install Syft:

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

## Part 3: Generate an SBOM

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

Check generated files:

```bash
ls -lh sbom*.json
```

Questions:

```text
What OS packages are inside the image?
What Python packages are inside the image?
Why is this useful before deployment?
```

## Part 4: Install Trivy

Install required packages:

```bash
sudo apt update
sudo apt install wget apt-transport-https gnupg lsb-release -y
```

Add the Trivy repository key:

```bash
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
```

Add the Trivy repository:

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

## Part 5: Scan the Insecure Image

Run a full scan:

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

Check the report:

```bash
ls -lh trivy-report.json
```

## Part 6: Build and Scan the Production Image

Build the production image:

```bash
docker build -f Dockerfile -t genai-chat:prod .
```

Scan it:

```bash
trivy image genai-chat:prod
```

Compare high and critical vulnerabilities:

```bash
trivy image --severity HIGH,CRITICAL insecure-image:latest
trivy image --severity HIGH,CRITICAL genai-chat:prod
```

Questions:

```text
Which image has fewer packages?
Which image has fewer vulnerabilities?
Which vulnerabilities come from the base image?
Which vulnerabilities come from Python dependencies?
```

## Optional: Docker Scout

If Docker Scout is available:

```bash
docker scout cves insecure-image:latest
docker scout recommendations insecure-image:latest
```

## Module 2 Cleanup

Remove generated reports if you do not need them:

```bash
rm -f sbom.json sbom.spdx.json sbom.cyclonedx.json trivy-report.json
```

