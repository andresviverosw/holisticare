"""Clinician-informed synthetic patient archetypes (SYNTH-01)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Archetype:
    id: str
    label_es: str
    clinician_role: str
    chief_complaint: str
    conditions: list[str]
    goals: list[str]
    therapies: list[str]
    contraindications: list[str] = field(default_factory=list)
    allergies: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)
    age_range: str = "30-40"
    sex_at_birth: str = "F"
    baseline_pain: int = 6
    psychosocial_summary: str = ""
    prior_interventions: list[str] = field(default_factory=list)
    diet_avoid_hint: str | None = None


ARCHETYPES: tuple[Archetype, ...] = (
    Archetype(
        id="osteo_lumbar",
        label_es="Lumbalgia crónica (osteopatía / fisioterapia)",
        clinician_role="osteopath",
        chief_complaint="Dolor lumbar crónico con rigidez matutina.",
        conditions=["lumbalgia cronica", "sindrome miofascial lumbar"],
        goals=["Reducir dolor", "Mejorar movilidad lumbar", "Retomar caminata diaria"],
        therapies=["fisioterapia", "osteopatia", "hidroterapia"],
        medications=["ibuprofeno 400 mg"],
        age_range="40-50",
        sex_at_birth="F",
        baseline_pain=7,
        psychosocial_summary="Estrés laboral alto por postura prolongada.",
        prior_interventions=["fisioterapia convencional"],
    ),
    Archetype(
        id="nutri_ibs",
        label_es="SII con ansiedad (nutrición funcional)",
        clinician_role="nutritionist",
        chief_complaint="Distensión abdominal y dolor postprandial.",
        conditions=["sindrome de intestino irritable", "ansiedad"],
        goals=["Reducir dolor abdominal", "Mejorar tolerancia digestiva", "Disminuir ansiedad"],
        therapies=["nutricion funcional", "mindfulness", "acupuntura"],
        contraindications=["lactosa"],
        allergies=["mariscos"],
        medications=["probiotico diario"],
        age_range="30-40",
        sex_at_birth="M",
        baseline_pain=6,
        psychosocial_summary="Ansiedad relacionada al trabajo y comidas fuera de casa.",
        prior_interventions=["dieta baja en FODMAP parcial"],
        diet_avoid_hint="lactosa",
    ),
    Archetype(
        id="sleep_fatigue",
        label_es="Fatiga y sueño no reparador",
        clinician_role="holistic_coach",
        chief_complaint="Fatiga persistente y sueño no reparador.",
        conditions=["fatiga cronica no especificada", "insomnio"],
        goals=["Aumentar energia diaria", "Mejorar sueno", "Retomar actividad fisica"],
        therapies=["higiene del sueno", "yoga terapeutico", "coaching de habitos"],
        contraindications=["entrenamiento de alta intensidad"],
        allergies=["nueces"],
        age_range="50-60",
        sex_at_birth="F",
        baseline_pain=4,
        psychosocial_summary="Cansancio por carga de cuidados familiares.",
        prior_interventions=["suplementos de magnesio"],
    ),
    Archetype(
        id="acupuncture_cervical",
        label_es="Cervicalgia tensional (acupuntura)",
        clinician_role="acupuncturist",
        chief_complaint="Dolor cervical con cefalea tensional al final del día.",
        conditions=["cervicalgia", "cefalea tensional"],
        goals=["Reducir dolor cervical", "Disminuir cefaleas", "Mejorar postura"],
        therapies=["acupuntura", "fisioterapia", "relajacion"],
        medications=["paracetamol"],
        age_range="35-45",
        sex_at_birth="F",
        baseline_pain=6,
        psychosocial_summary="Trabajo de pantalla >8 h/día.",
        prior_interventions=["masaje ocasional"],
    ),
    Archetype(
        id="knee_osteo",
        label_es="Gonartrosis leve (rehabilitación)",
        clinician_role="physiotherapist",
        chief_complaint="Dolor de rodilla al subir escaleras y al caminar prolongado.",
        conditions=["gonartrosis leve", "sobrepeso"],
        goals=["Reducir dolor de rodilla", "Mejorar tolerancia a la marcha", "Fortalecer cuadriceps"],
        therapies=["fisioterapia", "hidroterapia", "nutricion"],
        contraindications=["impacto de alto volumen"],
        age_range="55-65",
        sex_at_birth="M",
        baseline_pain=5,
        psychosocial_summary="Motivación alta pero miedo a reinjurarse.",
        prior_interventions=["analgesicos ocasionales"],
    ),
    Archetype(
        id="anxiety_burnout",
        label_es="Ansiedad y burnout (mindfulness)",
        clinician_role="psychologist_mindfulness",
        chief_complaint="Ansiedad, irritabilidad y dificultad para desconectar del trabajo.",
        conditions=["ansiedad", "burnout"],
        goals=["Reducir ansiedad", "Mejorar calidad de sueño", "Recuperar hábitos de descanso"],
        therapies=["mindfulness", "coaching de habitos", "yoga terapeutico"],
        age_range="25-35",
        sex_at_birth="NB",
        baseline_pain=3,
        psychosocial_summary="Alta carga cognitiva y horarios irregulares.",
        prior_interventions=["apps de meditacion"],
    ),
    Archetype(
        id="shoulder_impingement",
        label_es="Pinzamiento de hombro (fisioterapia)",
        clinician_role="physiotherapist",
        chief_complaint="Dolor de hombro al elevar el brazo por encima de la cabeza.",
        conditions=["sindrome de pinzamiento subacromial"],
        goals=["Reducir dolor", "Recuperar rango de movimiento", "Retomar natacion"],
        therapies=["fisioterapia", "acupuntura", "hidroterapia"],
        medications=["antiinflamatorio topico"],
        age_range="40-50",
        sex_at_birth="M",
        baseline_pain=6,
        psychosocial_summary="Deportista recreativo frustrado por limitación.",
        prior_interventions=["reposo relativo"],
    ),
    Archetype(
        id="metabolic_nutrition",
        label_es="Resistencia a la insulina (nutrición)",
        clinician_role="nutritionist",
        chief_complaint="Cansancio postprandial y dificultad para bajar de peso.",
        conditions=["resistencia a la insulina", "sobrepeso"],
        goals=["Estabilizar energia", "Mejorar composicion corporal", "Regular horarios de comida"],
        therapies=["nutricion funcional", "coaching de habitos", "actividad fisica supervisada"],
        allergies=["gluten"],
        contraindications=["ayuno prolongado sin supervision"],
        age_range="45-55",
        sex_at_birth="F",
        baseline_pain=2,
        psychosocial_summary="Intentos previos de dietas restrictivas con rebote.",
        prior_interventions=["dietas milagro"],
        diet_avoid_hint="gluten",
    ),
)
