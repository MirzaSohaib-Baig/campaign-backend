from pydantic import BaseModel
from typing import Optional

class CampaignSchema(BaseModel):
    name: str
    client: str
    channel: str
    status: str
    impressions: int
    clicks: int
    conversions: int
    spend: float
    budget: float
    revenue: float
    user_id: str

class UpdateCampaignSchema(BaseModel):
    campaign_id: str
    name: Optional[str] = None
    client: Optional[str] = None
    channel: Optional[str] = None
    status: Optional[str] = None
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    conversions: Optional[int] = None
    spend: Optional[float] = None
    budget: Optional[float] = None
    revenue: Optional[float] = None
    user_id: Optional[str] = None