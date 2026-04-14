import mediapipe as mp
import numpy as np
from PIL import Image
from models.schemas import FeatureScore

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

def euclidean_distance(p1, p2):
    return np.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)

def clamp(val, lo=0, hi=100):
    return max(lo, min(hi, int(val)))

def classify_face_shape(landmarks) -> str:
    """Classify face shape using geometric ratios from key landmarks."""
    face_width = euclidean_distance(landmarks[234], landmarks[454])
    jaw_width  = euclidean_distance(landmarks[172], landmarks[397])
    cheek_width = euclidean_distance(landmarks[50], landmarks[280])
    face_height = euclidean_distance(landmarks[10], landmarks[152])
    forehead_width = euclidean_distance(landmarks[70], landmarks[300])

    if face_width == 0 or jaw_width == 0:
        return "Oval"

    fw_ratio       = face_height / face_width
    jaw_ratio      = jaw_width / face_width
    cheek_ratio    = cheek_width / face_width
    forehead_ratio = forehead_width / face_width

    if fw_ratio > 1.5 and jaw_ratio < 0.75:
        return "Oblong"
    elif cheek_ratio > 0.9 and jaw_ratio > 0.85 and abs(jaw_ratio - forehead_ratio) < 0.05:
        return "Square"
    elif cheek_ratio > 0.9 and jaw_ratio < 0.8:
        return "Round"
    elif forehead_ratio > 0.9 and jaw_ratio < 0.75:
        return "Heart"
    elif cheek_ratio > 0.92 and forehead_ratio < 0.8 and jaw_ratio < 0.8:
        return "Diamond"
    else:
        return "Oval"


# ── Gender-specific aesthetic norms ──────────────────────────────────────────
#
# Research-backed targets:
#  Males:   H/W golden ratio ≈ 1.618 (longer, narrower ideal)
#            jaw ratio ≈ 0.85 (stronger jaw preferred)
#            lip ratio ≈ 0.5  (thinner upper lip target)
#            eye ratio ≈ 0.46 (normal spacing)
#
#  Females: H/W golden ratio ≈ 1.47 (slightly wider/rounder ideal)
#            jaw ratio ≈ 0.72 (softer, narrower jaw preferred)
#            lip ratio ≈ 0.7  (fuller upper lip target)
#            eye ratio ≈ 0.50 (slightly wider spacing ideal)
#
NORMS = {
    "male": {
        "hw_ratio":          1.618,
        "hw_sensitivity":    80,
        "eye_spacing":       0.46,
        "eye_sensitivity":   200,
        "lip_ratio":         0.50,
        "lip_sensitivity":   130,
        "jaw_ratio":         0.85,
        "jaw_sensitivity":   90,
        "sym_sensitivity":   500,
        "jaw_potential":     20,
        "eye_potential":     15,
        "lip_potential":     12,
        "sym_potential":     8,
        "hw_potential":      5,
    },
    "female": {
        "hw_ratio":          1.47,
        "hw_sensitivity":    70,
        "eye_spacing":       0.50,
        "eye_sensitivity":   180,
        "lip_ratio":         0.70,
        "lip_sensitivity":   110,
        "jaw_ratio":         0.72,
        "jaw_sensitivity":   100,
        "sym_sensitivity":   500,
        "jaw_potential":     15,
        "eye_potential":     18,
        "lip_potential":     18,
        "sym_potential":     8,
        "hw_potential":      5,
    },
}


def analyze_face(image: Image.Image, gender: str = "male"):
    """
    Run full geometry analysis on a face with gender-aware scoring norms.
    Returns feature scores, face shape, and landmark data.
    gender: "male" | "female"
    """
    gender = gender.lower() if gender else "male"
    if gender not in NORMS:
        gender = "male"
    n = NORMS[gender]

    image_np = np.array(image)
    results = face_mesh.process(image_np)

    if not results.multi_face_landmarks:
        return None

    lm = results.multi_face_landmarks[0].landmark

    # ── Face Shape ──────────────────────────────────────────────────────────
    face_shape = classify_face_shape(lm)

    # ── Symmetry ─────────────────────────────────────────────────────────────
    left  = euclidean_distance(lm[1], lm[33])
    right = euclidean_distance(lm[1], lm[263])
    symmetry_raw   = max(0, 100 - abs(left - right) * n["sym_sensitivity"])
    symmetry_score = clamp(symmetry_raw)

    # ── Golden Ratio (H/W) ───────────────────────────────────────────────────
    face_width  = euclidean_distance(lm[234], lm[454])
    face_height = euclidean_distance(lm[10],  lm[152])
    hw_ratio    = face_height / face_width if face_width > 0 else n["hw_ratio"]
    proportions_score = clamp(100 - abs(n["hw_ratio"] - hw_ratio) * n["hw_sensitivity"])

    # ── Eye Spacing ──────────────────────────────────────────────────────────
    interocular = euclidean_distance(lm[133], lm[362])
    eye_ratio   = interocular / face_width if face_width > 0 else n["eye_spacing"]
    eyes_score  = clamp(100 - abs(n["eye_spacing"] - eye_ratio) * n["eye_sensitivity"])

    # ── Lips ─────────────────────────────────────────────────────────────────
    upper     = euclidean_distance(lm[0],  lm[13])
    lower     = euclidean_distance(lm[14], lm[17])
    lip_ratio = upper / lower if lower > 0 else n["lip_ratio"]
    lips_score = clamp(100 - abs(n["lip_ratio"] - lip_ratio) * n["lip_sensitivity"])

    # ── Jawline ───────────────────────────────────────────────────────────────
    jaw_width   = euclidean_distance(lm[172], lm[397])
    jaw_ratio   = jaw_width / face_width if face_width > 0 else n["jaw_ratio"]
    jawline_score = clamp(100 - abs(n["jaw_ratio"] - jaw_ratio) * n["jaw_sensitivity"])

    # ── Assemble gender-specific tip variants ─────────────────────────────────
    if gender == "female":
        jaw_tip   = "A softer, tapered jaw is feminine gold. Contouring and face yoga can sculpt it further."
        eye_tip   = "Bright, expressive eyes score highest. Brow shaping and reducing dark circles help massively."
        lip_tip   = "Fuller, well-defined lips score higher. Hydration, lip liner and exfoliation boost this score."
        sym_tip   = "Facial symmetry is genetics, but posture, hairstyle, and makeup can visually balance it."
        prop_tip  = "Balanced facial proportions are an ideal. Hairstyle framing can optically perfect them."
        jaw_focus = "grooming"
    else:
        jaw_tip   = "Mewing, jaw exercises, and reducing face fat can improve jawline definition significantly."
        eye_tip   = "Dark circles and brow shaping can significantly improve eye presentation score."
        lip_tip   = "Hydrated, well-defined lips score higher. Lip balm and edge definition help a lot."
        sym_tip   = "Symmetry is largely genetic, but sleeping on your back and chewing evenly can improve it."
        prop_tip  = "Facial proportions are structural. Hair and beard styling can optically balance them."
        jaw_focus = "fitness"

    # ── Build FeatureScore objects ────────────────────────────────────────────
    features = [
        FeatureScore(
            name="Facial Symmetry",
            baseline=symmetry_score,
            potential=clamp(symmetry_score + n["sym_potential"]),
            category="genetics",
            tip=sym_tip
        ),
        FeatureScore(
            name="Golden Ratio",
            baseline=proportions_score,
            potential=clamp(proportions_score + n["hw_potential"]),
            category="genetics",
            tip=prop_tip
        ),
        FeatureScore(
            name="Eye Presentation",
            baseline=eyes_score,
            potential=clamp(eyes_score + n["eye_potential"]),
            category="grooming",
            tip=eye_tip
        ),
        FeatureScore(
            name="Lip Harmony",
            baseline=lips_score,
            potential=clamp(lips_score + n["lip_potential"]),
            category="grooming",
            tip=lip_tip
        ),
        FeatureScore(
            name="Jawline Definition",
            baseline=jawline_score,
            potential=clamp(jawline_score + n["jaw_potential"]),
            category=jaw_focus,
            tip=jaw_tip
        ),
    ]

    baseline_score = clamp(
        symmetry_score   * 0.25 +
        proportions_score * 0.20 +
        eyes_score       * 0.15 +
        lips_score       * 0.15 +
        jawline_score    * 0.25
    )
    potential_score = clamp(sum(f.potential for f in features) / len(features))

    landmarks_out = [{"x": l.x, "y": l.y, "z": l.z} for l in lm]

    return {
        "face_shape":      face_shape,
        "features":        features,
        "baseline_score":  baseline_score,
        "potential_score": potential_score,
        "landmarks":       landmarks_out,
        "raw_landmarks":   lm,
        "img_width":       image.width,
        "img_height":      image.height,
    }
