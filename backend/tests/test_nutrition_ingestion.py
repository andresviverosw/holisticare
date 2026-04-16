from __future__ import annotations

from llama_index.core.schema import Document

from app.rag.ingestion.loader import ChunkingPipeline, infer_topics


def test_infer_topics_detects_nutrition_from_text():
    text = "Plan de nutricion antiinflamatoria con dieta rica en vegetales."
    assert infer_topics(text, "guide.pdf") == ["nutrition"]


def test_infer_topics_detects_nutrition_from_source_file_name():
    assert infer_topics("General rehab notes.", "rehab_nutrition_main.pdf") == ["nutrition"]


def test_chunking_pipeline_attaches_nutrition_topic():
    doc = Document(
        text="Nutricion clinica para dolor cronico y alimentos a evitar.",
        metadata={"file_name": "main.pdf", "page_label": "1"},
    )
    pairs = ChunkingPipeline().process([doc])
    assert pairs
    _, metadata = pairs[0]
    assert "nutrition" in metadata.topic
