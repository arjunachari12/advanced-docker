# Docker Notes

Docker packages applications with their runtime dependencies. A Dockerfile describes how to build an image, and a container is a running instance of that image.

Useful commands:

```bash
docker build -t my-app .
docker run --rm my-app
docker ps
```

For production images, prefer small base images, non-root users, health checks, and repeatable dependency installation.
