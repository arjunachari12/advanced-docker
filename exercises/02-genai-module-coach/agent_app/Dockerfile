FROM python:3.12-slim

WORKDIR /agent

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AGENT_TASK="Build and deploy a GenAI container safely."

RUN useradd --create-home --uid 10001 agentuser

COPY --chown=agentuser:agentuser agent.py /agent/agent.py

USER agentuser

ENTRYPOINT ["python", "agent.py"]
