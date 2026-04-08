from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional

class SkinAnalysis(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skin_tone: str  # e.g., "Fair", "Medium", "Deep"
    texture_score: int  # 0-100 (100 = very smooth)
    dark_circle_severity: str  # "None", "Mild", "Moderate", "Severe"
    skin_tier: str  # "Clean", "Needs Attention", "Intensive Care"
    skincare_tips: List[str]

class GroomingRecommendation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    face_shape: str
    hairstyles: List[str]
    beard_styles: List[str]
    glasses_frames: List[str]
    style_tips: List[str]

class FeatureScore(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    baseline: int
    potential: int
    category: str  # "genetics", "grooming", "skin", "style"
    tip: str

class RoadmapWeek(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    week: str
    focus: str
    goals: List[str]
    icon: str

class GlowUpScorecard(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    baseline_score: int
    potential_score: int
    face_shape: str
    features: List[FeatureScore]
    skin: SkinAnalysis
    grooming: GroomingRecommendation
    roadmap: List[RoadmapWeek]
    disclaimer: str
    landmarks: Optional[List[Dict]] = None
