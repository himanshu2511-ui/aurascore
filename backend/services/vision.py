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
    jaw_width = euclidean_distance(landmarks[172], landmarks[397])
    cheek_width = euclidean_distance(landmarks[50], landmarks[280])
    face_height = euclidean_distance(landmarks[10], landmarks[152])
    forehead_width = euclidean_distance(landmarks[70], landmarks[300])

    if face_width == 0 or jaw_width == 0:
        return "Oval"

    fw_ratio = face_height / face_width       # height/width
    jaw_ratio = jaw_width / face_width         # jaw vs face width
    cheek_ratio = cheek_width / face_width     # cheek vs face width
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

def analyze_face(image: Image.Image):
    """Run full geometry analysis on face. Returns feature scores + face shape."""
    image_np = np.array(image)
    results = face_mesh.process(image_np)

    if not results.multi_face_landmarks:
        return None

    lm = results.multi_face_landmarks[0].landmark

    # ---- FACE SHAPE ----
    face_shape = classify_face_shape(lm)

    # ---- SYMMETRY ----
    left = euclidean_distance(lm[1], lm[33])
    right = euclidean_distance(lm[1], lm[263])
    symmetry_raw = max(0, 100 - abs(left - right) * 500)
    symmetry_score = clamp(symmetry_raw)

    # ---- GOLDEN RATIO (Face HW) ----
    face_width = euclidean_distance(lm[234], lm[454])
    face_height = euclidean_distance(lm[10], lm[152])
    hw_ratio = face_height / face_width if face_width > 0 else 1.618
    proportions_score = clamp(100 - abs(1.618 - hw_ratio) * 80)

    # ---- EYE SPACING ----
    interocular = euclidean_distance(lm[133], lm[362])
    eye_ratio = interocular / face_width if face_width > 0 else 0.46
    eyes_score = clamp(100 - abs(0.46 - eye_ratio) * 200)

    # ---- LIPS ----
    upper = euclidean_distance(lm[0], lm[13])
    lower = euclidean_distance(lm[14], lm[17])
    lip_ratio = upper / lower if lower > 0 else 0.5
    lips_score = clamp(100 - abs(0.5 - lip_ratio) * 130)

    # ---- JAWLINE ----
    jaw_width = euclidean_distance(lm[172], lm[397])
    jaw_ratio = jaw_width / face_width if face_width > 0 else 0.85
    jawline_score = clamp(100 - abs(0.85 - jaw_ratio) * 90)

    # ---- BUILD FeatureScore objects ----
    features = [
        FeatureScore(
            name="Facial Symmetry",
            baseline=symmetry_score,
            potential=clamp(symmetry_score + 8),
            category="genetics",
            tip="Symmetry is largely genetic, but sleeping on your back and chewing evenly can improve it over time."
        ),
        FeatureScore(
            name="Golden Ratio",
            baseline=proportions_score,
            potential=clamp(proportions_score + 5),
            category="genetics",
            tip="Facial proportions are structural. Hair and beard styling can optically balance them."
        ),
        FeatureScore(
            name="Eye Presentation",
            baseline=eyes_score,
            potential=clamp(eyes_score + 15),
            category="grooming",
            tip="Dark circles and brow shaping can significantly improve eye presentation score."
        ),
        FeatureScore(
            name="Lip Harmony",
            baseline=lips_score,
            potential=clamp(lips_score + 12),
            category="grooming",
            tip="Hydrated, well-defined lips score higher. Lip balm and edge definition help a lot."
        ),
        FeatureScore(
            name="Jawline Definition",
            baseline=jawline_score,
            potential=clamp(jawline_score + 20),
            category="fitness",
            tip="Mewing, jaw exercises, and reducing face fat can improve jawline definition significantly."
        ),
    ]

    baseline_score = clamp(
        symmetry_score * 0.25 + proportions_score * 0.20 +
        eyes_score * 0.15 + lips_score * 0.15 + jawline_score * 0.25
    )
    potential_score = clamp(
        sum(f.potential for f in features) / len(features)
    )

    landmarks_out = [{"x": l.x, "y": l.y, "z": l.z} for l in lm]

    return {
        "face_shape": face_shape,
        "features": features,
        "baseline_score": baseline_score,
        "potential_score": potential_score,
        "landmarks": landmarks_out,
        "raw_landmarks": lm,
        "img_width": image.width,
        "img_height": image.height,
    }
