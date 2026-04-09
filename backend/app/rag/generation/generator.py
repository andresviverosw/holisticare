"""
Plan Generator — Phase 4 of the RAG architecture.

Responsibilities:
- Assemble the final prompt with clinical context chunks
- Call Claude API and get structured JSON treatment plan
- Validate output structure
- Return plan dict ready for DB storage
"""

import json
import uuid
from datetime import datetime, timezone

from app.core.config import get_settings
from app.rag.llm_chat import complete_claude_or_openai

settings = get_settings()


SYSTEM_PROMPT = """You are a clinical decision support assistant for holistic rehabilitation.
You generate evidence-based treatment plan suggestions for licensed practitioners.

RULES — follow strictly:
1. ONLY use information from the clinical context provided (referenced by REF-ID)
2. Cite the REF-ID for every clinical recommendation using the format [REF-XXXXXX]
3. Explicitly flag ALL contraindications found in the context
4. Never make definitive diagnoses
5. Always output valid JSON — no preamble, no markdown fences
6. If the context is insufficient for a recommendation, say so explicitly in confidence_note
7. requires_practitioner_review must ALWAYS be true — never override this
8. Write rationale in the same language as the patient profile (es or en)"""


PLAN_SCHEMA_EXAMPLE = {
    "plan_id": "uuid",
    "patient_id": "uuid",
    "generated_at": "ISO 8601",
    "weeks": [
        {
            "week": 1,
            "goals": ["string"],
            "therapies": [
                {
                    "type": "string",
                    "frequency": "string",
                    "duration_minutes": 0,
                    "rationale": "string",
                    "citations": ["REF-XXXXXX"]
                }
            ],
            "contraindications_flagged": ["string"],
            "outcome_checkpoints": ["string"]
        }
    ],
    "confidence_note": "string",
    "requires_practitioner_review": True,
    "citations_used": ["REF-XXXXXX"]
}


def build_context_block(chunks: list[dict]) -> str:
    """Format retrieved chunks into a labeled context block."""
    lines = []
    for chunk in chunks:
        ref = chunk.get("ref_id", "REF-UNKNOWN")
        text = chunk.get("text", "")
        lines.append(f"[{ref}]\n{text}")
    return "\n\n".join(lines)


class PlanGenerator:
    """Generates a structured treatment plan using Claude + retrieved context."""

    def generate(
        self,
        patient_id: str,
        clinical_summary: str,
        chunks: list[dict],
        num_weeks: int = 4,
        language: str = "es",
    ) -> dict:
        """
        Args:
            patient_id: UUID of the patient
            clinical_summary: condensed intake profile (from QueryBuilder)
            chunks: reranked clinical chunks [{ref_id, text, metadata, rerank_score}]
            num_weeks: length of the plan
            language: 'es' or 'en' for output language

        Returns:
            Validated plan dict with status='pending_review'
        """
        context_block = build_context_block(chunks)
        citations_in_context = [c["ref_id"] for c in chunks]

        user_message = f"""PATIENT CLINICAL SUMMARY:
{clinical_summary}

RETRIEVED CLINICAL CONTEXT:
{context_block}

TASK:
Generate a {num_weeks}-week holistic treatment plan for this patient.
Output language: {"Spanish" if language == "es" else "English"}

Your output must be a valid JSON object matching this schema:
{json.dumps(PLAN_SCHEMA_EXAMPLE, indent=2)}

Replace 'uuid' values with actual UUIDs. patient_id = {patient_id}.
Only cite REF-IDs that appear in the RETRIEVED CLINICAL CONTEXT above."""

        raw = complete_claude_or_openai(
            system=SYSTEM_PROMPT,
            user=user_message,
            max_tokens=2000,
        )
        plan = self._parse_and_validate(raw, patient_id, citations_in_context)
        return plan

    def _parse_and_validate(
        self,
        raw: str,
        patient_id: str,
        allowed_citations: list[str],
    ) -> dict:
        """Parse JSON output and enforce safety constraints."""
        # Strip accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        plan = json.loads(raw)

        # Safety constraints — non-negotiable
        plan["plan_id"] = str(uuid.uuid4())
        plan["patient_id"] = patient_id
        plan["generated_at"] = datetime.now(timezone.utc).isoformat()
        plan["requires_practitioner_review"] = True  # always enforced
        plan["status"] = "pending_review"

        # Citation integrity: strip any hallucinated REF-IDs
        used = plan.get("citations_used", [])
        plan["citations_used"] = [r for r in used if r in allowed_citations]

        return plan
