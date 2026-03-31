"""
scripts/ingest.py — CLI script for ingesting clinical PDFs into pgvector.

Usage:
    python -m scripts.ingest --source data/mock
    python -m scripts.ingest --source data/raw --force
"""

import argparse
import sys
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.ingestion.loader import DocumentLoader, ChunkingPipeline
from app.rag.ingestion.embedder import Embedder


def run(source_dir: str, force_reindex: bool = False):
    print(f"\n{'='*60}")
    print(f"HolistiCare — Clinical Knowledge Ingestion")
    print(f"Source: {source_dir} | Force reindex: {force_reindex}")
    print(f"{'='*60}\n")

    loader = DocumentLoader()
    chunker = ChunkingPipeline()
    embedder = Embedder()

    # Load documents
    print("📄 Loading PDFs...")
    documents = loader.load(source_dir)
    print(f"   Found {len(documents)} documents\n")

    if not documents:
        print("No PDFs found. Exiting.")
        return

    total_chunks = 0

    for doc in documents:
        source_file = doc.metadata.get("file_name", "unknown")
        print(f"⚙️  Processing: {source_file}")

        try:
            # Chunk
            pairs = chunker.process([doc])
            print(f"   → {len(pairs)} chunks created")

            # Embed + store
            stored = embedder.embed_and_store(pairs, source_file)
            skipped = len(pairs) - stored
            print(f"   → {stored} stored, {skipped} skipped (already indexed)")

            embedder.log_ingestion(source_file, stored, "success")
            total_chunks += stored

        except Exception as e:
            print(f"   ❌ Failed: {e}")
            embedder.log_ingestion(source_file, 0, "failed", str(e))

    print(f"\n{'='*60}")
    print(f"✅ Ingestion complete — {total_chunks} new chunks indexed")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HolistiCare clinical knowledge ingestion")
    parser.add_argument("--source", default="data/mock", help="Source directory with PDFs")
    parser.add_argument("--force", action="store_true", help="Force reindex existing chunks")
    args = parser.parse_args()
    run(args.source, args.force)
