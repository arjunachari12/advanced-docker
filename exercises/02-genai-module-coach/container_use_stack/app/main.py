from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from fastapi import FastAPI, Query


INDEX_PATH = Path(os.getenv("INDEX_PATH", "/app/index.json"))
MODEL_RUNNER_BASE_URL = os.getenv("MODEL_RUNNER_BASE_URL", "http://model-runner.docker.internal/engines/v1").rstrip("/")
MODEL_RUNNER_MODEL = os.getenv("MODEL_RUNNER_MODEL", "ai/smollm2:latest")

app = FastAPI(title="Self-Debugging Doc Index AI Stack", version="1.0.0")


def load_index() -> dict:
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/search")
async def search(q: str = Query(min_length=1)) -> dict:
    return {"query": q, **search_index(q)}


def search_index(q: str) -> dict:
    terms = {term.lower() for term in q.split()}
    index = load_index()
    scored = []
    for document in index.get("documents", []):
        haystack = " ".join(
            [
                document.get("title", ""),
                document.get("summary", ""),
                " ".join(document.get("keywords", [])),
            ]
        ).lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            scored.append((score, document))

    results = [
        document
        for _, document in sorted(scored, key=lambda item: (-item[0], item[1]["id"]))
    ]
    return {"count": len(results), "results": results[:5]}


def model_runner_answer(question: str, context: str) -> str:
    payload = {
        "model": MODEL_RUNNER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Answer using only the provided documentation context. Keep it short.",
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        "max_tokens": 100,
        "temperature": 0.2,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{MODEL_RUNNER_BASE_URL}/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()


def looks_low_quality(answer: str) -> bool:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", answer.lower())
    if len(words) < 4:
        return True
    non_space = [char for char in answer if not char.isspace()]
    if non_space and max(non_space.count(char) for char in set(non_space)) / len(non_space) > 0.45:
        return True
    most_common_word = max(words.count(word) for word in set(words))
    return most_common_word / len(words) > 0.35


@app.get("/ask")
async def ask(q: str = Query(min_length=1)) -> dict:
    search_result = search_index(q)
    context = "\n".join(
        f"- {doc['title']}: {doc['summary']}" for doc in search_result["results"][:3]
    )
    fallback = context or "No matching docs found."
    try:
        answer = model_runner_answer(q, context)
        if looks_low_quality(answer):
            answer = fallback
            source = "retrieval-fallback: weak model output"
        else:
            source = "model-runner"
    except (TimeoutError, urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
        answer = fallback
        source = f"retrieval-fallback: {exc}"

    return {
        "query": q,
        "answer": answer or fallback,
        "source": source,
        "matches": search_result["results"][:3],
    }


@app.get("/debug")
async def debug() -> dict:
    index = load_index()
    documents = index.get("documents", [])
    return {
        "index_path": str(INDEX_PATH),
        "document_count": index.get("document_count"),
        "documents_loaded": len(documents),
        "status": "healthy" if index.get("document_count") == len(documents) else "mismatch",
    }
