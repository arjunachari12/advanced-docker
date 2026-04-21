# Dagger Notes

Dagger lets teams define CI/CD workflows as code. A Dagger function can mount source code, run tests in containers, build images, and publish artifacts.

Useful commands:

```bash
dagger functions
dagger call test-agent
dagger call publish-agent --image=example/genai-agent:latest
```

The key idea is to make workflow logic portable and reproducible by running the steps in containers.
