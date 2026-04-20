from __future__ import annotations

import json
import sys
import urllib.request


def get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))

def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    print(get_json(f"{base_url}/health"))
    print(get_json(f"{base_url}/ready"))
    response = post_json(
        f"{base_url}/api/chat",
        {"message": "Say hello from a Dockerized GenAI app in one sentence."},
    )
    print(response["answer"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
