set -eu

name="doc-index-ai-module7-test"
docker rm -f "$name" >/dev/null 2>&1 || true

docker run -d --name "$name" doc-index-ai:module7 >/dev/null

cleanup() {
  docker rm -f "$name" >/dev/null 2>&1 || true
}
trap cleanup EXIT

for _ in $(seq 1 30); do
  if docker exec "$name" python - <<'PY' >/dev/null 2>&1
import urllib.request
urllib.request.urlopen("http://127.0.0.1:8092/health", timeout=2).read()
PY
  then
    break
  fi
  sleep 1
done

docker exec "$name" python - <<'PY'
import json
import urllib.parse
import urllib.request

base = "http://127.0.0.1:8092"
health = json.loads(urllib.request.urlopen(f"{base}/health", timeout=5).read())
assert health["status"] == "ok", health

query = urllib.parse.urlencode({"q": "model runner"})
search = json.loads(urllib.request.urlopen(f"{base}/search?{query}", timeout=5).read())
assert search["results"], search
print("Smoke test passed:", search["results"][0]["title"])
PY
