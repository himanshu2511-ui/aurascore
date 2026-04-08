from models.schemas import GroomingRecommendation

GROOMING_DB = {
    "Oval": {
        "hairstyles": ["Textured Crop", "Side Part", "Quiff", "Any length works!"],
        "beard_styles": ["Light Stubble", "Short Boxed Beard", "Clean Shaven"],
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
        "hairstyles": ["Side Part", "Curtain Bangs", "Medium Length", "Chin-length Bob"],
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

def get_grooming_recommendations(face_shape: str) -> GroomingRecommendation:
    data = GROOMING_DB.get(face_shape, GROOMING_DB["Oval"])
    return GroomingRecommendation(
        face_shape=face_shape,
        hairstyles=data["hairstyles"],
        beard_styles=data["beard_styles"],
        glasses_frames=data["glasses_frames"],
        style_tips=data["style_tips"]
    )
