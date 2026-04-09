"""Print ingestion_log aggregates and recent failures (run: PYTHONPATH=/app python scripts/ingestion_log_report.py)."""
from __future__ import annotations

from app.core.config import get_settings
import psycopg2


def main() -> None:
    s = get_settings()
    conn = psycopg2.connect(s.database_url_sync)
    cur = conn.cursor()
    cur.execute(
        "SELECT status, COUNT(*) FROM ingestion_log GROUP BY status ORDER BY status"
    )
    print("ingestion_log by status:", cur.fetchall())

    cur.execute(
        """
        SELECT source_file, COUNT(*) AS n,
               MAX(LEFT(COALESCE(error_msg, ''), 120))
        FROM ingestion_log
        WHERE status = 'failed'
        GROUP BY source_file
        ORDER BY n DESC, source_file
        LIMIT 50
        """
    )
    rows = cur.fetchall()
    print("failed files (distinct, by failure count):")
    for r in rows:
        print("---", r[0][:100] if r[0] else "", "| failures:", r[1], "| example:", r[2])

    cur.execute(
        """
        SELECT source_file, chunk_count,
               LEFT(COALESCE(error_msg, ''), 200)
        FROM ingestion_log
        WHERE status = 'failed'
        ORDER BY run_at DESC
        LIMIT 15
        """
    )
    print("\nmost recent 15 failure rows:")
    for r in cur.fetchall():
        print("---", r[0][:80] if r[0] else "", "|", r[2])
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
