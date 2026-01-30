from pydantic import BaseModel
from typing import Optional, List

# =====================================================
# Session Schemas
# =====================================================

class SessionStartRequest(BaseModel):
    anonymous_id: str
    device_type: Optional[str] = None
    app_version: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None


class SessionStartResponse(BaseModel):
    session_id: str


# =====================================================
# Recommendation Schemas
# =====================================================

class RecommendationRequest(BaseModel):
    session_id: str
    user_id: Optional[int] = None
    anonymous_id: str              # 🔒 REQUIRED
    surface: str = "home"
    page_size: int = 10
    locale: Optional[str] = None

    # Category filter
    category: Optional[str] = None


class RecommendedItem(BaseModel):
    item_id: str
    position: int
    retrieval_score: Optional[float] = None
    rank_score: Optional[float] = None
    final_score: Optional[float] = None
    title: Optional[str] = None


class RecommendationResponse(BaseModel):
    impression_id: str
    items: List[RecommendedItem]


# =====================================================
# Click Schemas
# =====================================================

class ClickRequest(BaseModel):
    impression_id: str
    item_id: str
    position: int
    anonymous_id: str
    dwell_ms: int = 0
    open_type: str = "ui"


class ClickResponse(BaseModel):
    status: str
