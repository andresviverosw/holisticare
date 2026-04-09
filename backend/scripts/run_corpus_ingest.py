#!/usr/bin/env python3
"""
Run RAG ingestion from inside the backend container (WORKDIR /app).

  docker compose exec backend env PYTHONPATH=/app python scripts/run_corpus_ingest.py \\
    --source-dir data/corpus --force-reindex

Does not use HTTP; safe for long runs. Requires the same env as the API (OpenAI key, DB).
"""
from __future__ import annotations

import argparse
import json
import sys

from app.services.ingestion_service import IngestionService


def main() -> int:
    p = argparse.ArgumentParser(description="Index PDF/HTML under source_dir into pgvector.")
    p.add_argument(
        "--source-dir",
        default="data/corpus",
        help="Path relative to /app (default: data/corpus)",
    )
    p.add_argument(
        "--force-reindex",
        action="store_true",
        help="Remove existing chunks per source file before re-embedding",
    )
    args = p.parse_args()
    try:
        result = IngestionService().ingest(args.source_dir, force_reindex=args.force_reindex)
    except FileNotFoundError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
