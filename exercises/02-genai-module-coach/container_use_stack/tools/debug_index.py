from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    index_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out/index.json")
    index = json.loads(index_path.read_text(encoding="utf-8"))

    errors = []
    documents = index.get("documents", [])
    if index.get("document_count") != len(documents):
        errors.append("document_count does not match documents length")
    if len(documents) < 3:
        errors.append("expected at least three docs in the index")

    for document in documents:
        for field in ("id", "title", "summary", "keywords"):
            if not document.get(field):
                errors.append(f"{document.get('id', '<unknown>')} missing {field}")

    if errors:
        print("Self-debug failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Self-debug passed: {len(documents)} indexed docs are queryable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
