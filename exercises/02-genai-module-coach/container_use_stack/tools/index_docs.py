from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


STOPWORDS = {
    "a",
    "and",
    "are",
    "as",
    "by",
    "for",
    "in",
    "is",
    "it",
    "of",
    "or",
    "the",
    "to",
    "with",
}


def tokenize(text: str) -> list[str]:
    return [
        word
        for word in re.findall(r"[a-z][a-z0-9-]+", text.lower())
        if word not in STOPWORDS and len(word) > 2
    ]


def summarize(text: str) -> str:
    for line in text.splitlines():
        cleaned = line.strip(" #")
        if cleaned:
            return cleaned[:180]
    return "No summary available."


def build_index(docs_dir: Path) -> dict:
    documents = []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        keywords = [word for word, _ in Counter(tokenize(text)).most_common(8)]
        documents.append(
            {
                "id": path.stem,
                "path": str(path),
                "title": summarize(text),
                "summary": summarize(text),
                "keywords": keywords,
            }
        )

    return {
        "version": 1,
        "document_count": len(documents),
        "documents": documents,
    }


def main() -> int:
    docs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("out/index.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    index = build_index(docs_dir)
    output.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"Indexed {index['document_count']} documents into {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
