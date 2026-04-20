from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")

app = FastAPI(title="Ollama GenAI Chat", version="1.0.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    model: str
    answer: str


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ollama GenAI Chat</title>
  <style>
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #161616;
      background: #f2f6f7;
    }
    main {
      max-width: 860px;
      margin: 0 auto;
      padding: 32px 20px;
    }
    h1 {
      margin: 0 0 8px;
      font-size: 2rem;
    }
    textarea {
      width: 100%;
      min-height: 120px;
      box-sizing: border-box;
      padding: 12px;
      border: 1px solid #9aa8ad;
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
      background: #176d5d;
      font: inherit;
      cursor: pointer;
    }
    button:disabled {
      background: #6f7f7b;
      cursor: wait;
    }
    pre {
      min-height: 180px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      padding: 16px;
      border-radius: 8px;
      color: #edf7f5;
      background: #111617;
    }
    .meta {
      color: #4b5b60;
    }
  </style>
</head>
<body>
  <main>
    <h1>Ollama GenAI Chat</h1>
    <p class="meta">A simple app container calling a local Ollama container.</p>
    <form id="chat-form">
      <label for="message"><strong>Message</strong></label>
      <textarea id="message">Explain Docker multi-stage builds in three bullets.</textarea>
      <button id="send-button" type="submit">Send</button>
    </form>
    <h2>Model Response</h2>
    <pre id="answer">Ready.</pre>
  </main>
  <script>
    const form = document.querySelector("#chat-form");
    const button = document.querySelector("#send-button");
    const answer = document.querySelector("#answer");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      button.disabled = true;
      answer.textContent = "Thinking...";
      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({message: document.querySelector("#message").value})
        });
        const data = await response.json();
        answer.textContent = response.ok ? data.answer : data.detail;
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
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"Ollama is not ready: {exc}") from exc

    model_names = [model.get("name", "") for model in data.get("models", [])]
    return {
        "status": "ready",
        "ollama_base_url": OLLAMA_BASE_URL,
        "ollama_model": OLLAMA_MODEL,
        "model_available": OLLAMA_MODEL in model_names,
        "available_models": model_names,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    request_body = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "You are a concise assistant. Prefer practical examples and commands.",
            },
            {"role": "user", "content": payload.message},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=request_body)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text
        if "model" in detail.lower() and "not found" in detail.lower():
            detail = f"Model {OLLAMA_MODEL} is not available. Pull it with: ollama pull {OLLAMA_MODEL}"
        raise HTTPException(status_code=502, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Cannot reach Ollama at {OLLAMA_BASE_URL}: {exc}") from exc

    answer = data.get("message", {}).get("content", "").strip()
    return ChatResponse(model=OLLAMA_MODEL, answer=answer or "Ollama returned an empty response.")

