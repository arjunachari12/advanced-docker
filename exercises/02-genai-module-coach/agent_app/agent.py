from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request


DEFAULT_MODEL = "qwen2.5:0.5b"


def ollama_note(answer: str) -> str:
    compact = " ".join(answer.strip().split())
    return compact[:160] if compact else "Ollama returned an empty response."


def normalize_ollama_answer(answer: str, task: str) -> str:
    steps = []
    for line in answer.splitlines():
        cleaned = line.strip()
        if re.match(r"^\d+[\.\)]\s+", cleaned):
            steps.append(re.sub(r"^\d+[\.\)]\s+", f"{len(steps) + 1}. ", cleaned))
        if len(steps) == 3:
            break
    if len(steps) == 3:
        return "\n".join(steps)

    return f"{local_plan(task)}\n\nOllama note: {ollama_note(answer)}"


def local_plan(task: str) -> str:
    """Return a deterministic plan when no LLM endpoint is configured."""
    normalized = " ".join(task.strip().split())
    lowered = normalized.lower()

    if any(word in lowered for word in ("test", "verify", "quality")):
        focus = "run the fastest feedback loop first, then promote the same artifact"
        command = "dagger call test-agent"
    elif any(word in lowered for word in ("release", "deploy", "ship", "publish")):
        focus = "build a release candidate, scan it, and publish only after checks pass"
        command = "dagger call publish-agent --image=<registry>/genai-agent:<tag>"
    elif any(word in lowered for word in ("docker", "container", "image")):
        focus = "explain the container boundary, Dockerfile inputs, and runtime command"
        command = "docker build -t genai-agent:local ./agent_app"
    else:
        focus = "turn the request into a small repeatable workflow with clear inputs"
        command = "dagger call run-agent --task=<task>"

    return (
        "Agent plan:\n"
        f"1. Understand the request: {normalized}\n"
        f"2. Focus: {focus}.\n"
        f"3. First command: {command}"
    )


def ollama_plan(task: str, base_url: str, model: str) -> str:
    """Ask a local Ollama-compatible chat endpoint for a short plan."""
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a DevOps release coach for a Docker and Dagger lab. "
                    "Help the user ship a containerized AI agent safely. "
                    "Return exactly three numbered lines and no extra text. "
                    "Prefer concrete Docker or Dagger commands."
                ),
            },
            {"role": "user", "content": task},
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    return normalize_ollama_answer(data.get("message", {}).get("content", ""), task)


def run_agent(task: str, use_ollama: bool = True) -> str:
    if not use_ollama:
        return local_plan(task)

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)
    try:
        answer = ollama_plan(task, base_url, model)
    except (TimeoutError, urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
        return f"{local_plan(task)}\n\nLLM fallback reason: {exc}"

    return answer or local_plan(task)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ollama-powered DevOps release coach agent")
    parser.add_argument(
        "task",
        nargs="?",
        default=os.getenv("AGENT_TASK", "Build and deploy a GenAI container safely."),
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip Ollama and use the deterministic local fallback planner.",
    )
    parser.add_argument("--use-llm", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    print(run_agent(args.task, use_ollama=not args.offline))


if __name__ == "__main__":
    main()
