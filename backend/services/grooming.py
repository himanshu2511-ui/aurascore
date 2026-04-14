from models.schemas import GroomingRecommendation

# ── Male grooming database ────────────────────────────────────────────────────
MALE_GROOMING_DB = {
    "Oval": {
        "hairstyles": ["Textured Crop", "Side Part", "Quiff", "Slicked Back", "Any length works!"],
        "beard_styles": ["Light Stubble", "Short Boxed Beard", "Clean Shaven", "Full Beard"],
        "glasses_frames": ["Wayfarer", "Aviator", "Round frames", "Almost any frame suits you"],
        "style_tips": [
            "Oval is the most versatile face shape — you can rock nearly any hairstyle.",
            "Keep volume balanced on all sides; avoid styles that make the face appear longer.",
        ]
    },
    "Round": {
        "hairstyles": ["High Fade + Volume on Top", "Pompadour", "Angular Fringe", "Undercut"],
        "beard_styles": ["Goatee", "Chin Strap", "Extended Chin Beard"],
        "glasses_frames": ["Rectangular frames", "Square frames", "Geometric frames"],
        "style_tips": [
            "Add height on top to elongate the face visually.",
            "Avoid round or bowl-cut styles that add width.",
        ]
    },
    "Square": {
        "hairstyles": ["Textured Layers", "Side Swept", "Loose Waves", "Tapered sides"],
        "beard_styles": ["Rounded Beard", "Circle Beard", "Full Beard"],
        "glasses_frames": ["Oval frames", "Round frames", "Rimless glasses"],
        "style_tips": [
            "Soften angular jawline with layered, textured styles.",
            "Avoid blunt cuts that emphasize the jaw's squareness.",
        ]
    },
    "Heart": {
        "hairstyles": ["Side Part", "Curtain Bangs", "Medium Length", "Bro Flow"],
        "beard_styles": ["Full Beard (adds jaw width)", "Mutton Chops", "Stubble"],
        "glasses_frames": ["Bottom-heavy frames", "Light-colored frames", "Oval"],
        "style_tips": [
            "Add width at the jaw and chin to balance a wider forehead.",
            "Avoid voluminous styles at the top.",
        ]
    },
    "Diamond": {
        "hairstyles": ["Side-Swept Bangs", "Textured Top", "Volume at Forehead"],
        "beard_styles": ["Light Stubble", "Circle Beard"],
        "glasses_frames": ["Oval frames", "Cat-eye frames", "Rimless"],
        "style_tips": [
            "Add width at the forehead and chin to soften cheekbones.",
            "Avoid styles that add width only to the cheeks.",
        ]
    },
    "Oblong": {
        "hairstyles": ["Side Parts", "Waves", "Curls", "Layers", "Curtain Bangs"],
        "beard_styles": ["Full Beard", "Mutton Chops", "Wide Mustache"],
        "glasses_frames": ["Deep frames", "Decorative temples", "Square", "Wayfarer"],
        "style_tips": [
            "Add width to the sides to shorten the appearance of the face.",
            "Avoid very high, tall styles that elongate the face further.",
        ]
    },
}

# ── Female grooming database ──────────────────────────────────────────────────
FEMALE_GROOMING_DB = {
    "Oval": {
        "hairstyles": ["Beach Waves", "Long Layers", "Blunt Bob", "Half-Up Half-Down", "Any style works!"],
        "beard_styles": [],  # N/A
        "glasses_frames": ["Cat-eye", "Wayfarer", "Aviator", "Almost any frame suits you"],
        "style_tips": [
            "Oval is the ideal feminine face shape — most hairstyles flatter you naturally.",
            "Soft curls and layers enhance balanced proportions beautifully.",
        ]
    },
    "Round": {
        "hairstyles": ["Long Straight Layers", "Side-Swept Bangs", "Lob (Long Bob)", "High Ponytail", "Loose Bun"],
        "beard_styles": [],
        "glasses_frames": ["Angular frames", "Rectangle", "Cat-eye"],
        "style_tips": [
            "Elongating styles like long straight layers slim the face visually.",
            "Avoid blunt bobs that end at the chin — they emphasize width.",
        ]
    },
    "Square": {
        "hairstyles": ["Soft Waves", "Side Part with Volume", "Wispy Bangs", "Long Layers", "Cascading Curls"],
        "beard_styles": [],
        "glasses_frames": ["Oval frames", "Round frames", "Rimless"],
        "style_tips": [
            "Soft, romantic styles with movement and volume flatter square faces beautifully.",
            "Avoid blunt, jaw-length cuts — they emphasize angularity.",
        ]
    },
    "Heart": {
        "hairstyles": ["Chin-Length Bob", "Lob with Waves", "Curtain Bangs", "Side-Swept Bangs"],
        "beard_styles": [],
        "glasses_frames": ["Bottom-heavy frames", "Round frames", "Oval"],
        "style_tips": [
            "Add volume at the jawline to balance a wider forehead.",
            "Curtain bangs add softness to a prominent forehead beautifully.",
        ]
    },
    "Diamond": {
        "hairstyles": ["Side-Swept Bangs", "Volume at Crown", "Chin-Length Bob", "Wispy Layers"],
        "beard_styles": [],
        "glasses_frames": ["Oval frames", "Cat-eye", "Rimless"],
        "style_tips": [
            "Add width at the forehead and chin to soften prominent cheekbones.",
            "Avoid sleek, center-parted styles that draw attention to the cheeks.",
        ]
    },
    "Oblong": {
        "hairstyles": ["Beachy Waves", "Blunt Bob", "Curtain Bangs", "Curly Styles", "Short Layers"],
        "beard_styles": [],
        "glasses_frames": ["Oversized square", "Wayfarer", "Geometric"],
        "style_tips": [
            "Width-adding styles like beach waves and full bobs create beautiful balance.",
            "Avoid long, sleek styles that elongate the face further.",
        ]
    },
}


def get_grooming_recommendations(face_shape: str, gender: str = "male") -> GroomingRecommendation:
    gender = (gender or "male").lower()
    db = FEMALE_GROOMING_DB if gender == "female" else MALE_GROOMING_DB
    data = db.get(face_shape, db["Oval"])
    return GroomingRecommendation(
        face_shape=face_shape,
        hairstyles=data["hairstyles"],
        beard_styles=data["beard_styles"],
        glasses_frames=data["glasses_frames"],
        style_tips=data["style_tips"]
    )
