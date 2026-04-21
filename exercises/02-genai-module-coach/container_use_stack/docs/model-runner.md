# Docker Model Runner Notes

Docker Model Runner runs local AI models through Docker. It can expose OpenAI-compatible and Ollama-compatible APIs to apps.

Useful commands:

```bash
docker model status
docker model pull ai/smollm2
docker model list
```

Small models are good for demos, but larger models usually give better answers and need more CPU, RAM, or GPU resources.
