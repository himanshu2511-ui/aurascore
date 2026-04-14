from fastapi import FastAPI, File, UploadFile, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
import io
from PIL import Image

from sqlalchemy.orm import Session
from db.database import engine, get_db
from db import models
from routers.auth import router as auth_router, get_current_user
from routers.leaderboard import router as leaderboard_router
from db.models import User

from models.schemas import GlowUpScorecard
from services.vision import analyze_face
from services.skin import analyze_skin
from services.grooming import get_grooming_recommendations
from services.roadmap import generate_roadmap

# Create all DB tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AuraScore API v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(leaderboard_router)

# ── Health ────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.1"}

# ── Analysis (protected) ──────────────────────────────────────────────────
@app.post("/api/analyze", response_model=GlowUpScorecard)
async def analyze_face_endpoint(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contents = await image.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")

    gender = (current_user.gender or "male").lower()
    vision_result = analyze_face(img, gender=gender)

    if not vision_result:
        return GlowUpScorecard(
            baseline_score=0,
            potential_score=0,
            face_shape="Unknown",
            features=[],
            skin=analyze_skin(img, None, img.width, img.height),
            grooming=get_grooming_recommendations("Oval", gender=gender),
            roadmap=generate_roadmap("Needs Attention", "Oval", 70, 60, gender=gender),
            disclaimer="No face detected. Please center your face clearly in the frame.",
        )

    skin = analyze_skin(img, vision_result["raw_landmarks"], vision_result["img_width"], vision_result["img_height"])
    grooming = get_grooming_recommendations(vision_result["face_shape"], gender=gender)
    skin_bonus = (100 - skin.texture_score) // 15
    potential_boosted = min(100, vision_result["potential_score"] + skin_bonus)
    roadmap = generate_roadmap(
        skin_tier=skin.skin_tier,
        face_shape=vision_result["face_shape"],
        grooming_potential=potential_boosted,
        skin_score=skin.texture_score,
        gender=gender,
    )

    if current_user.aura_score is None or potential_boosted > current_user.aura_score:
        current_user.aura_score = potential_boosted
        db.add(current_user)
        db.commit()

    return GlowUpScorecard(
        baseline_score=vision_result["baseline_score"],
        potential_score=potential_boosted,
        face_shape=vision_result["face_shape"],
        features=vision_result["features"],
        skin=skin,
        grooming=grooming,
        roadmap=roadmap,
        disclaimer="🤖 AI estimates based on geometry & image statistics — not absolute truths. Scores reflect improvement potential, not your worth.",
        landmarks=vision_result["landmarks"],
    )
