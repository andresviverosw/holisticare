from __future__ import annotations

import io
from typing import Any

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def build_approved_plan_pdf(plan_id: str, plan_json: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER
    y = height - 50

    def write_line(text: str, *, step: int = 16, bold: bool = False) -> None:
        nonlocal y
        if y < 60:
            pdf.showPage()
            y = height - 50
        pdf.setFont("Helvetica-Bold" if bold else "Helvetica", 10)
        pdf.drawString(48, y, text[:110])
        y -= step

    write_line("HolistiCare - Plan de tratamiento aprobado", bold=True)
    write_line(f"Plan ID: {plan_id}")
    write_line(f"Estado: {plan_json.get('status', 'unknown')}")
    write_line("")

    weeks = plan_json.get("weeks") or []
    if not weeks:
        write_line("No hay semanas generadas en este plan.")
    for week in weeks:
        write_line(f"Semana {week.get('week', '-')}", bold=True)
        goals = week.get("goals") or []
        if goals:
            write_line("Objetivos:", bold=True)
            for goal in goals:
                write_line(f"- {goal}")
        therapies = week.get("therapies") or []
        if therapies:
            write_line("Terapias:", bold=True)
            for therapy in therapies:
                t_type = therapy.get("type", "terapia")
                freq = therapy.get("frequency", "")
                duration = therapy.get("duration_minutes")
                duration_txt = f" ({duration} min)" if duration else ""
                write_line(f"- {t_type} {freq}{duration_txt}".strip())
        checkpoints = week.get("outcome_checkpoints") or []
        if checkpoints:
            write_line("Puntos de evaluacion:", bold=True)
            for checkpoint in checkpoints:
                write_line(f"- {checkpoint}")
        write_line("")

    notes = plan_json.get("practitioner_notes")
    if notes:
        write_line("Notas del practicante:", bold=True)
        for line in str(notes).splitlines():
            write_line(line)

    citations = plan_json.get("citations_used") or []
    if citations:
        write_line("")
        write_line("Referencias:", bold=True)
        write_line(", ".join(map(str, citations)))

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.read()
