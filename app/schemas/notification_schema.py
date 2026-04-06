from pydantic import BaseModel
from typing import Optional
from app.models.notification_models import AlertType


class NotificationSchema(BaseModel):
    user_id: str
    campaign_id: str
    alert_type: AlertType
    message: str
    is_read: Optional[bool] = False

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True

class AlertRuleSchema(BaseModel):
    user_id: str
    campaign_id: str
    alert_type: str
    threshold: float
    is_active: Optional[bool] = True

class UpdateAlertRuleSchema(BaseModel):
    rule_id: str
    user_id: Optional[str] = None
    campaign_id: Optional[str] = None
    alert_type: Optional[str] = None
    threshold: Optional[float] = 0.0
    is_active: Optional[bool] = False