from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

from db.database import get_db
from db.models import User
from services.auth import (
    hash_password, verify_password,
    create_access_token, decode_token,
    generate_otp, otp_expiry,
)
from services.email_service import send_otp_email

router = APIRouter(prefix="/auth", tags=["auth"])

# ── Schemas ───────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class VerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ResendRequest(BaseModel):
    email: EmailStr

class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    token_type: str = "bearer"
    user_name: str
    user_email: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    is_verified: bool

# ── Helpers ───────────────────────────────────────────────────────────────

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalid or expired")
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    return user

# ── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/signup", status_code=201)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        if existing.is_verified:
            raise HTTPException(status_code=409, detail="Email already registered. Please log in.")
        # Re-send OTP if duplicate unverified signup
        otp = generate_otp()
        existing.otp_code = otp
        existing.otp_expires_at = otp_expiry()
        existing.name = body.name
        existing.hashed_password = hash_password(body.password)
        db.commit()
        send_otp_email(body.email, body.name, otp)
        return {"message": "OTP resent. Check your email."}

    user = User(
        name=body.name,
        email=body.email,
        hashed_password=hash_password(body.password),
        is_verified=True,
    )
    db.add(user)
    db.commit()
    
    token = create_access_token({"sub": user.email})
    return TokenResponse(
        access_token=token,
        user_name=user.name,
        user_email=user.email,
    )


@router.post("/verify")
def verify_email(body: VerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    if user.otp_code != body.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    if user.otp_expires_at and datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP expired. Request a new one.")

    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()

    token = create_access_token({"sub": user.email})
    return TokenResponse(
        access_token=token,
        user_name=user.name,
        user_email=user.email,
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.email})
    return TokenResponse(
        access_token=token,
        user_name=user.name,
        user_email=user.email,
    )


@router.post("/resend-otp")
def resend_otp(body: ResendRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    otp = generate_otp()
    user.otp_code = otp
    user.otp_expires_at = otp_expiry()
    db.commit()
    send_otp_email(body.email, user.name, otp)
    return {"message": "New OTP sent. Check your email."}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
