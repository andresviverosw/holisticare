"""
Query construction — Phase 2 of the RAG architecture.

Responsibilities:
- Summarize patient intake profile into a dense clinical summary
- Expand that summary into multiple search queries (multi-query)
"""

import anthropic
from app.core.config import get_settings

settings = get_settings()
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


SUMMARIZER_PROMPT = """You are a clinical summarization assistant for a holistic rehabilitation platform.

Given a patient's intake JSON, produce a concise 100–150 word clinical summary
optimized for semantic search against a knowledge base of clinical guidelines.

Focus on:
- Chief complaint and duration
- Relevant medical history and comorbidities
- Current medications and contraindications
- Prior treatments and outcomes
- Baseline outcome scores (pain, function, sleep, mood)

Return ONLY the clinical summary. No preamble, no labels."""


QUERY_EXPANSION_PROMPT = """You are a clinical search assistant for a holistic rehabilitation knowledge base.

Given a patient clinical summary, generate {n} distinct search queries to retrieve
relevant clinical guidelines and protocols. Each query should approach the case
from a different angle:
1. Symptom-focused (what the patient presents with)
2. Treatment-focused (what therapies are relevant)
3. Contraindication-focused (what to avoid and why)
4. Outcome-focused (expected recovery trajectory)

Patient summary:
{summary}

Return ONLY a JSON array of {n} query strings. No preamble, no labels.
Example: ["query 1", "query 2", "query 3", "query 4"]"""


class QueryBuilder:
    """Builds search queries from a patient intake profile."""

    def build_clinical_summary(self, intake_json: dict) -> str:
        """Compress intake profile into a search-optimized clinical summary."""
        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": f"{SUMMARIZER_PROMPT}\n\nPatient intake:\n{intake_json}",
                }
            ],
        )
        return response.content[0].text.strip()

    def expand_queries(self, clinical_summary: str) -> list[str]:
        """Generate multi-query variants from the clinical summary."""
        n = settings.num_query_variants
        prompt = QUERY_EXPANSION_PROMPT.format(n=n, summary=clinical_summary)

        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )

        import json
        raw = response.content[0].text.strip()
        try:
            queries = json.loads(raw)
            if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
                return queries[:n]
        except json.JSONDecodeError:
            pass

        # Fallback: use the summary itself as the single query
        return [clinical_summary]
