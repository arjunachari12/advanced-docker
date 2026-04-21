from __future__ import annotations

import os
import re
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


MODEL_RUNNER_BASE_URL = os.getenv(
    "MODEL_RUNNER_BASE_URL",
    "http://model-runner.docker.internal/engines/v1",
).rstrip("/")
MODEL_RUNNER_MODEL = os.getenv("MODEL_RUNNER_MODEL", "ai/llama3.2:latest")

app = FastAPI(title="Docker Model Runner GenAI App", version="1.0.0")


class ExplainRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)


class ExplainResponse(BaseModel):
    model: str
    answer: str
    warning: str | None = None


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Docker Model Runner GenAI App</title>
  <style>
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #171717;
      background: #f5f7f8;
    }
    main {
      max-width: 820px;
      margin: 0 auto;
      padding: 32px 20px;
    }
    textarea {
      width: 100%;
      min-height: 110px;
      box-sizing: border-box;
      padding: 12px;
      border: 1px solid #9aa6ac;
      border-radius: 8px;
      font: inherit;
      background: white;
    }
    button {
      margin-top: 12px;
      padding: 10px 14px;
      border: 0;
      border-radius: 8px;
      color: white;
      background: #0f6b6f;
      font: inherit;
      cursor: pointer;
    }
    button:disabled {
      background: #728082;
      cursor: wait;
    }
    pre {
      min-height: 160px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      padding: 16px;
      border-radius: 8px;
      color: #edf7f7;
      background: #111618;
    }
    .meta {
      color: #516166;
    }
  </style>
</head>
<body>
  <main>
    <h1>Docker Model Runner GenAI App</h1>
    <p class="meta">A containerized app calling a local model through Docker Model Runner.</p>
    <form id="form">
      <label for="topic"><strong>Topic</strong></label>
      <textarea id="topic">Explain Docker Model Runner in two beginner-friendly sentences.</textarea>
      <button id="send" type="submit">Ask Model Runner</button>
    </form>
    <h2>Response</h2>
    <pre id="answer">Ready.</pre>
  </main>
  <script>
    const form = document.querySelector("#form");
    const button = document.querySelector("#send");
    const answer = document.querySelector("#answer");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      button.disabled = true;
      answer.textContent = "Thinking...";
      try {
        const response = await fetch("/api/explain", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({topic: document.querySelector("#topic").value})
        });
        const data = await response.json();
        if (response.ok) {
          answer.textContent = data.warning ? `${data.answer}\\n\\n${data.warning}` : data.answer;
        } else {
          answer.textContent = data.detail;
        }
      } catch (error) {
        answer.textContent = String(error);
      } finally {
        button.disabled = false;
      }
    });
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return INDEX_HTML


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{MODEL_RUNNER_BASE_URL}/models")
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Docker Model Runner is not ready at {MODEL_RUNNER_BASE_URL}: {exc}",
        ) from exc

    model_ids = [model.get("id", "") for model in data.get("data", [])]
    return {
        "status": "ready",
        "model_runner_base_url": MODEL_RUNNER_BASE_URL,
        "model_runner_model": MODEL_RUNNER_MODEL,
        "model_available": MODEL_RUNNER_MODEL in model_ids,
        "available_models": model_ids,
    }


def looks_low_quality(answer: str) -> bool:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", answer.lower())
    if len(words) < 4:
        return True
    if not words:
        return True
    most_common_count = max(words.count(word) for word in set(words))
    return most_common_count / len(words) > 0.35


@app.post("/api/explain", response_model=ExplainResponse)
async def explain(payload: ExplainRequest) -> ExplainResponse:
    request_body = {
        "model": MODEL_RUNNER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You explain Docker and local AI concepts to beginners. "
                    "Answer in two short sentences. Avoid markdown."
                ),
            },
            {"role": "user", "content": payload.topic},
        ],
        "max_tokens": 80,
        "temperature": 0.2,
    }

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{MODEL_RUNNER_BASE_URL}/chat/completions",
                json=request_body,
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=exc.response.text) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Cannot reach Docker Model Runner at {MODEL_RUNNER_BASE_URL}: {exc}",
        ) from exc

    answer = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    warning = None
    if looks_low_quality(answer):
        warning = (
            "Warning: the local model returned a weak answer. Try a larger compatible "
            "model image or increase resources for Docker Model Runner."
        )
    return ExplainResponse(
        model=MODEL_RUNNER_MODEL,
        answer=answer or "The model returned an empty response.",
        warning=warning,
    )
