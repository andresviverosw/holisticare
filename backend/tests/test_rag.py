"""
RAG pipeline regression tests.

Run: pytest tests/ -v

These tests validate pipeline contracts without hitting real APIs.
Use mock fixtures to isolate each layer.
"""

import pytest
import json
from unittest.mock import MagicMock, patch


# ─── Fixtures ─────────────────────────────────────────────────

SAMPLE_INTAKE = {
    "patient_id": "00000000-0000-0000-0000-000000000001",
    "age": 45,
    "sex": "F",
    "chief_complaint": "Dolor lumbar crónico con irradiación a pierna izquierda",
    "duration_weeks": 8,
    "prior_treatments": ["fisioterapia convencional", "AINES"],
    "medications": ["ibuprofeno 400mg", "omeprazol"],
    "contraindications": ["embarazo descartado", "marcapasos: NO"],
    "baseline_scores": {
        "NRS_pain": 7,
        "ODI": 45,
        "PSQI": 14,
    },
}

SAMPLE_CHUNKS = [
    {
        "ref_id": "REF-AABBCCDD",
        "text": "Lumbar stabilization physiotherapy reduces ODI scores by 40% over 6 weeks in chronic LBP patients.",
        "score": 0.91,
        "rerank_score": 0.95,
        "metadata": {"therapy_type": ["physiotherapy"], "evidence_level": "A", "language": "en"},
    },
    {
        "ref_id": "REF-11223344",
        "text": "Acupunctura en puntos BL23 y GB30 muestra reducción significativa del dolor radicular lumbar.",
        "score": 0.87,
        "rerank_score": 0.88,
        "metadata": {"therapy_type": ["acupuncture"], "evidence_level": "B", "language": "es"},
    },
    {
        "ref_id": "REF-CONTRA01",
        "text": "Contraindicación: acupunctura en zona lumbar evitar si paciente usa anticoagulantes.",
        "score": 0.80,
        "rerank_score": 0.82,
        "metadata": {"therapy_type": ["acupuncture"], "has_contraindication": True, "language": "es"},
    },
]

SAMPLE_PLAN = {
    "plan_id": "test-plan-id",
    "patient_id": "00000000-0000-0000-0000-000000000001",
    "generated_at": "2026-03-01T00:00:00+00:00",
    "requires_practitioner_review": True,
    "status": "pending_review",
    "citations_used": ["REF-AABBCCDD", "REF-11223344"],
    "weeks": [
        {
            "week": 1,
            "goals": ["Reducir dolor NRS de 7 a 5"],
            "therapies": [
                {
                    "type": "physiotherapy",
                    "frequency": "3x/semana",
                    "duration_minutes": 45,
                    "rationale": "Evidencia nivel A para LBP crónico [REF-AABBCCDD]",
                    "citations": ["REF-AABBCCDD"],
                }
            ],
            "contraindications_flagged": ["Verificar anticoagulantes antes de acupuntura [REF-CONTRA01]"],
            "outcome_checkpoints": ["NRS al final de semana 1"],
        }
    ],
    "confidence_note": "Contexto suficiente para recomendaciones de fisioterapia. Acupuntura requiere verificación.",
    "diet_recommendations": {
        "eat": [
            {
                "item": "Vegetales de hoja verde",
                "rationale": "Patron antiinflamatorio [REF-AABBCCDD]",
                "citations": ["REF-AABBCCDD"],
            }
        ],
        "avoid": [
            {
                "item": "Ultraprocesados altos en azucar",
                "rationale": "Asociado a peor dolor reportado [REF-11223344]",
                "citations": ["REF-11223344"],
            }
        ],
    },
    "retrieval_metadata": {
        "queries_used": ["dolor lumbar crónico irradiación"],
        "candidates_retrieved": 3,
        "chunks_passed_to_llm": 3,
        "reranker_backend": "crossencoder",
    },
}


# ─── Output contract tests ─────────────────────────────────────

class TestPlanOutputContracts:
    """
    These tests validate that the pipeline output always
    satisfies safety and regulatory contracts — regardless of LLM output.
    """

    def test_requires_practitioner_review_always_true(self):
        assert SAMPLE_PLAN["requires_practitioner_review"] is True

    def test_status_always_pending_review(self):
        assert SAMPLE_PLAN["status"] == "pending_review"

    def test_plan_is_valid_json_serializable(self):
        serialized = json.dumps(SAMPLE_PLAN)
        parsed = json.loads(serialized)
        assert parsed["plan_id"] == SAMPLE_PLAN["plan_id"]

    def test_citations_only_from_retrieved_context(self):
        allowed = {c["ref_id"] for c in SAMPLE_CHUNKS}
        used = set(SAMPLE_PLAN.get("citations_used", []))
        assert used.issubset(allowed), f"Hallucinated citations: {used - allowed}"

    def test_contraindications_present_in_output(self):
        contra_chunks = [c for c in SAMPLE_CHUNKS if c["metadata"].get("has_contraindication")]
        assert len(contra_chunks) > 0, "No contraindication chunks in test data"

        output_contras = []
        for week in SAMPLE_PLAN.get("weeks", []):
            output_contras.extend(week.get("contraindications_flagged", []))

        assert len(output_contras) > 0, "Contraindications not surfaced in plan output"

    def test_plan_has_required_fields(self):
        required = ["plan_id", "patient_id", "generated_at", "weeks",
                    "requires_practitioner_review", "citations_used", "status", "diet_recommendations"]
        for field in required:
            assert field in SAMPLE_PLAN, f"Missing required field: {field}"

    def test_weeks_have_required_structure(self):
        for week in SAMPLE_PLAN["weeks"]:
            assert "week" in week
            assert "goals" in week
            assert "therapies" in week
            assert "contraindications_flagged" in week
            assert "outcome_checkpoints" in week

    def test_diet_recommendations_have_required_structure(self):
        diet = SAMPLE_PLAN["diet_recommendations"]
        assert "eat" in diet and isinstance(diet["eat"], list)
        assert "avoid" in diet and isinstance(diet["avoid"], list)
        for entry in diet["eat"] + diet["avoid"]:
            assert "item" in entry
            assert "rationale" in entry
            assert "citations" in entry


# ─── Generator unit tests ─────────────────────────────────────

class TestPlanGeneratorValidation:
    def test_hallucinated_citations_stripped(self):
        from app.rag.generation.generator import PlanGenerator

        gen = PlanGenerator()
        raw_plan = {
            "plan_id": "x",
            "patient_id": "p1",
            "generated_at": "now",
            "requires_practitioner_review": True,
            "citations_used": ["REF-AABBCCDD", "REF-HALLUCINATED"],
            "weeks": [],
            "confidence_note": "test",
        }
        allowed = ["REF-AABBCCDD", "REF-11223344"]

        result = gen._parse_and_validate(
            raw=json.dumps(raw_plan),
            patient_id="p1",
            allowed_citations=allowed,
        )

        assert "REF-HALLUCINATED" not in result["citations_used"]
        assert "REF-AABBCCDD" in result["citations_used"]

    def test_requires_practitioner_review_enforced(self):
        from app.rag.generation.generator import PlanGenerator

        gen = PlanGenerator()
        # Even if LLM sets it to False, it must be overridden to True
        raw_plan = {
            "plan_id": "x",
            "patient_id": "p1",
            "generated_at": "now",
            "requires_practitioner_review": False,  # LLM tried to override
            "citations_used": [],
            "weeks": [],
            "confidence_note": "test",
        }
        result = gen._parse_and_validate(
            raw=json.dumps(raw_plan),
            patient_id="p1",
            allowed_citations=[],
        )

        assert result["requires_practitioner_review"] is True

    def test_diet_recommendations_default_shape_is_added(self):
        from app.rag.generation.generator import PlanGenerator

        gen = PlanGenerator()
        raw_plan = {
            "plan_id": "x",
            "patient_id": "p1",
            "generated_at": "now",
            "requires_practitioner_review": True,
            "citations_used": [],
            "weeks": [],
            "confidence_note": "test",
        }
        result = gen._parse_and_validate(
            raw=json.dumps(raw_plan),
            patient_id="p1",
            allowed_citations=[],
        )
        assert result["diet_recommendations"] == {"eat": [], "avoid": []}

    def test_hallucinated_citations_stripped_from_diet_recommendations(self):
        from app.rag.generation.generator import PlanGenerator

        gen = PlanGenerator()
        raw_plan = {
            "plan_id": "x",
            "patient_id": "p1",
            "generated_at": "now",
            "requires_practitioner_review": True,
            "citations_used": ["REF-AABBCCDD"],
            "weeks": [],
            "confidence_note": "test",
            "diet_recommendations": {
                "eat": [{"item": "Pescado", "rationale": "x", "citations": ["REF-AABBCCDD", "REF-FAKE"]}],
                "avoid": [{"item": "Azucar", "rationale": "y", "citations": ["REF-FAKE"]}],
            },
        }
        result = gen._parse_and_validate(
            raw=json.dumps(raw_plan),
            patient_id="p1",
            allowed_citations=["REF-AABBCCDD"],
        )
        assert result["diet_recommendations"]["eat"][0]["citations"] == ["REF-AABBCCDD"]
        assert result["diet_recommendations"]["avoid"][0]["citations"] == []


class TestVectorRetrieverPgVectorQuery:
    """PGVectorStore.query expects a VectorStoreQuery (LlamaIndex API)."""

    @patch("app.rag.retrieval.vector_search.get_vector_store")
    @patch("app.rag.retrieval.vector_search.get_embed_model")
    def test_retrieve_calls_query_with_vector_store_query(
        self, mock_get_embed, mock_get_vs
    ):
        from llama_index.core.vector_stores.types import VectorStoreQuery
        from app.rag.retrieval.vector_search import VectorRetriever, RetrievalConfig

        mock_get_embed.return_value.get_text_embedding.return_value = [0.1, 0.2]
        vs = MagicMock()
        mock_get_vs.return_value = vs
        from llama_index.core.schema import TextNode

        node = TextNode(text="chunk", metadata={"ref_id": "REF-1"})
        vs.query.return_value = MagicMock(nodes=[node], similarities=[0.91])

        retriever = VectorRetriever()
        cfg = RetrievalConfig(language="es")
        out = retriever.retrieve(["single query"], cfg, top_k=6)

        vs.query.assert_called_once()
        arg0 = vs.query.call_args[0][0]
        assert isinstance(arg0, VectorStoreQuery)
        assert arg0.query_embedding == [0.1, 0.2]
        assert arg0.similarity_top_k == 6
        assert arg0.filters is not None
        assert len(out) == 1
        assert out[0]["ref_id"] == "REF-1"
        assert out[0]["score"] == pytest.approx(0.91)


class TestNutritionSafetyGuards:
    def test_blocks_diet_entries_matching_intake_contraindications_or_allergies(self):
        from app.rag.pipeline import apply_nutrition_safety_guards

        plan = {
            "diet_recommendations": {
                "eat": [
                    {
                        "item": "Pescado azul",
                        "rationale": "Aporta omega 3",
                        "citations": ["REF-AABBCCDD"],
                    },
                    {
                        "item": "Frutas frescas",
                        "rationale": "Fibra y antioxidantes",
                        "citations": ["REF-11223344"],
                    },
                ],
                "avoid": [],
            }
        }
        intake = {
            "contraindications": ["anticoagulantes"],
            "allergies": ["pescado"],
        }

        out = apply_nutrition_safety_guards(plan, intake)

        assert len(out["diet_recommendations"]["eat"]) == 1
        assert out["diet_recommendations"]["eat"][0]["item"] == "Frutas frescas"
        assert len(out["nutrition_safety_flags"]) == 1
        assert out["nutrition_safety_flags"][0]["action"] == "blocked"
        assert "pescado" in out["nutrition_safety_flags"][0]["matched_terms"]

    def test_pipeline_applies_nutrition_safety_guards(self):
        from app.rag.pipeline import RAGPipeline

        pipe = RAGPipeline()
        pipe.query_builder = MagicMock()
        pipe.retriever = MagicMock()
        pipe.reranker = MagicMock()
        pipe.generator = MagicMock()

        pipe.query_builder.build_clinical_summary.return_value = "summary"
        pipe.query_builder.expand_queries.return_value = ["query"]
        pipe.retriever.retrieve.return_value = [{"ref_id": "REF-A", "text": "ctx"}]
        pipe.reranker.rerank.return_value = [{"ref_id": "REF-A", "text": "ctx"}]
        pipe.generator.generate.return_value = {
            "plan_id": "p",
            "patient_id": "pat",
            "generated_at": "now",
            "requires_practitioner_review": True,
            "status": "pending_review",
            "citations_used": ["REF-A"],
            "weeks": [],
            "confidence_note": "ok",
            "diet_recommendations": {
                "eat": [
                    {"item": "Pescado", "rationale": "Proteina", "citations": ["REF-A"]},
                    {"item": "Avena", "rationale": "Fibra", "citations": ["REF-A"]},
                ],
                "avoid": [],
            },
        }

        result = pipe.generate_plan(
            patient_id="pat",
            intake_json={
                "profile_version": "generic_holistic_v0",
                "chief_complaint": "x",
                "conditions": ["c"],
                "goals": ["g"],
                "allergies": ["pescado"],
            },
            available_therapies=["fisioterapia"],
            preferred_language="es",
        )

        assert result["diet_recommendations"]["eat"] == [
            {"item": "Avena", "rationale": "Fibra", "citations": ["REF-A"]}
        ]
        assert result["nutrition_safety_flags"][0]["item"] == "Pescado"
