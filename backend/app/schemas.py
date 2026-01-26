from pydantic import BaseModel
from typing import Optional, List
from pydantic import BaseModel, Field

# -------------------------
# Session schemas
# -------------------------
class SessionStartRequest(BaseModel):
    anonymous_id: str
    device_type: Optional[str] = None
    app_version: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None


class SessionStartResponse(BaseModel):
    session_id: str


# -------------------------
# Recommendation schemas
# -------------------------
class RecommendationRequest(BaseModel):
    session_id: str
    user_id: Optional[int] = None
    anonymous_id: Optional[str] = None
    surface: str = "home"
    page_size: int = 10
    locale: Optional[str] = None


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

# -------------------------
# Click schemas
# -------------------------
class ClickRequest(BaseModel):
    impression_id: str
    item_id: str
    position: int
    dwell_ms: Optional[int] = None
    open_type: Optional[str] = None


class ClickResponse(BaseModel):
    status: str
