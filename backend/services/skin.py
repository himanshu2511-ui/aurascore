import numpy as np
from PIL import Image
from models.schemas import SkinAnalysis

def analyze_skin(image: Image.Image, face_landmarks, img_width: int, img_height: int) -> SkinAnalysis:
    """
    Analyzes skin quality from the face region using image statistics.
    Extracts forehead/cheek region and computes tone, texture, and dark circles.
    """
    image_np = np.array(image)

    # --- SKIN TONE ---
    # Sample from forehead region (landmark 10 = top of face)
    if face_landmarks:
        lm = face_landmarks
        # Forehead patch
        fx = int(lm[10].x * img_width)
        fy = int(lm[10].y * img_height)
        patch_size = 20
        x1, y1 = max(0, fx - patch_size), max(0, fy)
        x2, y2 = min(img_width, fx + patch_size), min(img_height, fy + patch_size * 3)
        forehead_patch = image_np[y1:y2, x1:x2]

        if forehead_patch.size > 0:
            r_mean = np.mean(forehead_patch[:, :, 0])
            g_mean = np.mean(forehead_patch[:, :, 1])
            b_mean = np.mean(forehead_patch[:, :, 2])
            luminance = 0.299 * r_mean + 0.587 * g_mean + 0.114 * b_mean
        else:
            luminance = 128.0

        # Skin tone classification
        if luminance > 180:
            skin_tone = "Fair"
        elif luminance > 130:
            skin_tone = "Medium"
        elif luminance > 90:
            skin_tone = "Tan"
        else:
            skin_tone = "Deep"

        # --- TEXTURE (Acne/Oiliness Proxy) ---
        # Use Laplacian variance on face region as texture roughness indicator
        lm_left = int(lm[234].x * img_width)
        lm_right = int(lm[454].x * img_width)
        lm_top = int(lm[10].y * img_height)
        lm_bottom = int(lm[152].y * img_height)
        face_crop = image_np[max(0,lm_top):lm_bottom, max(0,lm_left):lm_right]
        
        if face_crop.size > 0:
            gray = np.mean(face_crop, axis=2)
            # Laplacian approximation
            laplacian_var = np.var(np.diff(np.diff(gray, axis=0), axis=1))
            # Normalize: lower variance = smoother skin
            texture_score = max(0, min(100, int(100 - laplacian_var * 0.3)))
        else:
            texture_score = 70

        # --- DARK CIRCLES ---
        # Under-eye region brightness (landmarks 33, 133, 362, 263 = eye corners)
        left_eye_x = int(lm[33].x * img_width)
        left_eye_y = int(lm[33].y * img_height)
        under_eye_patch = image_np[left_eye_y:left_eye_y+15, max(0,left_eye_x-15):left_eye_x+25]
        
        if under_eye_patch.size > 0:
            eye_lum = np.mean(under_eye_patch)
            diff = luminance - eye_lum
            if diff < 10:
                dark_circle_severity = "None"
            elif diff < 25:
                dark_circle_severity = "Mild"
            elif diff < 45:
                dark_circle_severity = "Moderate"
            else:
                dark_circle_severity = "Severe"
        else:
            dark_circle_severity = "Mild"

    else:
        skin_tone = "Medium"
        texture_score = 60
        dark_circle_severity = "Mild"

    # Skin Tier
    if texture_score >= 80 and dark_circle_severity in ["None", "Mild"]:
        skin_tier = "Clean"
    elif texture_score >= 60:
        skin_tier = "Needs Attention"
    else:
        skin_tier = "Intensive Care"

    # Skincare Tips
    tips = []
    if dark_circle_severity in ["Moderate", "Severe"]:
        tips.append("Apply Vitamin C serum under eyes daily to reduce dark circles.")
        tips.append("Get 7–9 hours of sleep and use cold compresses in the morning.")
    if texture_score < 70:
        tips.append("Use a gentle salicylic acid cleanser to improve skin texture.")
        tips.append("Follow up with a non-comedogenic moisturizer to balance oil.")
    if skin_tone == "Fair":
        tips.append("Apply SPF 30+ sunscreen daily to prevent hyperpigmentation.")
    if skin_tone in ["Tan", "Deep"]:
        tips.append("Niacinamide serum can help even out skin tone and reduce dark spots.")
    if not tips:
        tips.append("Your skin looks clean! Maintain a consistent CTM (Cleanse-Tone-Moisturize) routine.")

    return SkinAnalysis(
        skin_tone=skin_tone,
        texture_score=texture_score,
        dark_circle_severity=dark_circle_severity,
        skin_tier=skin_tier,
        skincare_tips=tips
    )
