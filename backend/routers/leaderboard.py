from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import User

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])

@router.get("")
def get_leaderboard(db: Session = Depends(get_db)):
    """Get top 50 users by aura_score, with rank, gender, and score label."""
    top_users = (
        db.query(User)
        .filter(User.aura_score > 0, User.is_verified == True)
        .order_by(User.aura_score.desc())
        .limit(50)
        .all()
    )

    def score_label(score: int) -> str:
        if score >= 90: return "Legendary"
        if score >= 80: return "Elite"
        if score >= 70: return "High"
        if score >= 60: return "Good"
        if score >= 50: return "Average"
        return "Developing"

    return [
        {
            "rank":        idx + 1,
            "id":          user.id,
            "name":        user.name,
            "aura_score":  user.aura_score,
            "gender":      user.gender or "male",
            "score_label": score_label(user.aura_score),
        }
        for idx, user in enumerate(top_users)
    ]
