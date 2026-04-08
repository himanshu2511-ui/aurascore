from models.schemas import RoadmapWeek
from typing import List

def generate_roadmap(skin_tier: str, face_shape: str, grooming_potential: int, skin_score: int) -> List[RoadmapWeek]:
    roadmap = [
        RoadmapWeek(
            week="Week 1–2",
            focus="Skin Foundation",
            icon="🔬",
            goals=[
                "Start a consistent CTM routine: Cleanser → Toner → Moisturizer.",
                "Introduce Vitamin C serum (morning) and retinol (night, if tolerated).",
                "Apply SPF 30+ sunscreen every morning regardless of weather.",
                "Drink 2–3L of water daily. Skin hydration starts from within.",
            ] if skin_tier != "Clean" else [
                "Maintain your existing CTM routine — your skin is in great shape!",
                "Add a weekly exfoliation (gentle AHA) to maintain glow.",
                "Keep SPF 30+ sunscreen as a daily habit.",
                "Stay hydrated: 2–3L water daily.",
            ]
        ),
        RoadmapWeek(
            week="Week 3–4",
            focus="Grooming & Style Reset",
            icon="💇",
            goals=[
                f"Book a haircut tailored for your {face_shape} face shape.",
                "Try a new beard style from your recommendations.",
                "Invest in a matching glasses or sunglasses frame.",
                "Trim and shape brows — clean brows dramatically improve symmetry perception.",
            ]
        ),
        RoadmapWeek(
            week="Week 5–6",
            focus="Fitness & Jawline",
            icon="🏋️",
            goals=[
                "Mewing (tongue posture): keep tongue flat on the roof of mouth all day.",
                "Jaw exercises: chew mastic gum 10 mins/day for jawline definition.",
                "Reduce sodium and processed food to decrease facial puffiness.",
                "Start 3x/week cardio to reduce face fat and improve skin glow.",
            ]
        ),
        RoadmapWeek(
            week="Week 7–8",
            focus="Confidence & Presence",
            icon="✨",
            goals=[
                "Practice eye contact: 3-second rule in conversations.",
                "Smile training: practice genuine smiling (Duchenne smile) in mirror.",
                "Posture check: stand tall, shoulders back — posture affects face shape perception.",
                "Before/after photo comparison: track your 8-week transformation!",
            ]
        ),
    ]
    return roadmap
