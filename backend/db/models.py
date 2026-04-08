from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified   = Column(Boolean, default=False)
    otp_code      = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    aura_score    = Column(Integer, default=0, index=True)
