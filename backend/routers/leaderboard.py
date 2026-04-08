from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import User
from routers.auth import get_current_user

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])

@router.get("/")
def get_leaderboard(db: Session = Depends(get_db)):
    # Get top 50 users ordered by aura_score descending
    top_users = db.query(User).filter(User.aura_score > 0)\
                  .order_by(User.aura_score.desc())\
                  .limit(50).all()
    
    return [
        {
            "id": user.id,
            "name": user.name,
            "aura_score": user.aura_score,
        }
        for user in top_users
    ]
