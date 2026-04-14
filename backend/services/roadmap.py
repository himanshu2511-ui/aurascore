from models.schemas import RoadmapWeek
from typing import List


def generate_roadmap(
    skin_tier: str,
    face_shape: str,
    grooming_potential: int,
    skin_score: int,
    gender: str = "male",
) -> List[RoadmapWeek]:
    gender = (gender or "male").lower()
    is_female = gender == "female"

    # ── Week 1-2: Skin Foundation ─────────────────────────────────────────────
    if skin_tier == "Clean":
        skin_goals = [
            "Maintain your existing CTM routine — your skin is in great shape!",
            "Add a weekly exfoliation (gentle AHA) to maintain your glow.",
            "Keep SPF 30+ sunscreen as a daily habit.",
            "Stay hydrated: 2-3L water daily.",
        ]
    else:
        if is_female:
            skin_goals = [
                "Start a consistent CTM routine: Gentle Cleanser → Toner → Moisturizer.",
                "Add Vitamin C serum (morning) + niacinamide (evening) for brightening & pore care.",
                "Apply SPF 50+ sunscreen every morning — non-negotiable for feminine glow.",
                "Introduce a weekly hydrating face mask. Prioritize sleep hygiene for skin repair.",
            ]
        else:
            skin_goals = [
                "Start a consistent CTM routine: Cleanser → Toner → Moisturizer.",
                "Introduce Vitamin C serum (morning) and retinol (night, if tolerated).",
                "Apply SPF 30+ sunscreen every morning regardless of weather.",
                "Drink 2-3L of water daily. Skin hydration starts from within.",
            ]

    # ── Week 3-4: Grooming & Style ────────────────────────────────────────────
    if is_female:
        groom_goals = [
            f"Get a professional haircut tailored for your {face_shape} face shape.",
            "Shape your eyebrows professionally — brow framing is the #1 instant glow-up.",
            "Build a simple makeup routine (BB cream, mascara, defined brows) for everyday confidence.",
            "Invest in glasses or sunglasses frames that complement your face shape.",
        ]
    else:
        groom_goals = [
            f"Book a haircut tailored for your {face_shape} face shape.",
            "Try a new beard style from your style recommendations.",
            "Invest in matching glasses or sunglasses frames.",
            "Trim and shape brows — clean brows dramatically improve symmetry perception.",
        ]

    # ── Week 5-6: Fitness & Jawline ───────────────────────────────────────────
    if is_female:
        fitness_goals = [
            "Face yoga and lymphatic drainage massage to define and sculpt your jawline.",
            "Reduce sodium and processed food to decrease facial puffiness and bloat.",
            "Start 3x/week cardio + yoga — improves skin glow and posture elegantly.",
            "Gua-sha facial massage routine: 10 min/day for contouring and circulation.",
        ]
    else:
        fitness_goals = [
            "Mewing (tongue posture): keep tongue flat on the roof of mouth all day.",
            "Jaw exercises: chew mastic gum 10 mins/day for jawline definition.",
            "Reduce sodium and processed food to decrease facial puffiness.",
            "Start 3x/week cardio to reduce face fat and improve skin glow.",
        ]

    # ── Week 7-8: Confidence & Presence ──────────────────────────────────────
    if is_female:
        confidence_goals = [
            "Practice eye contact and confident body language — presence multiplies beauty.",
            "Smile training: a genuine Duchenne smile is universally attractive.",
            "Posture check: stand tall, shoulders relaxed — posture shapes how your face is perceived.",
            "Before/after photo comparison: celebrate your 8-week transformation!",
        ]
    else:
        confidence_goals = [
            "Practice eye contact: 3-second rule in conversations.",
            "Smile training: practice genuine smiling (Duchenne smile) in the mirror.",
            "Posture check: stand tall, shoulders back — posture affects face shape perception.",
            "Before/after photo comparison: track your 8-week transformation!",
        ]

    return [
        RoadmapWeek(week="Week 1-2", focus="Skin Foundation",     icon="SKIN",  goals=skin_goals),
        RoadmapWeek(week="Week 3-4", focus="Grooming & Style",    icon="GROOM", goals=groom_goals),
        RoadmapWeek(week="Week 5-6", focus="Fitness & Jawline",   icon="FIT",   goals=fitness_goals),
        RoadmapWeek(week="Week 7-8", focus="Confidence & Presence",icon="STAR", goals=confidence_goals),
    ]
