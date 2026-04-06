# app/models/notification_models.py
from sqlalchemy import Column, String, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base_model import BaseModel

class AlertType(str, enum.Enum):
    CTR_LOW         = "ctr_low"
    SPEND_HIGH      = "spend_high"
    ROAS_LOW        = "roas_low"
    BUDGET_EXCEEDED = "budget_exceeded"
    CONVERSIONS_LOW = "conversions_low"

class AlertRule(BaseModel):
    __tablename__ = "alert_rules"

    user_id     = Column(ForeignKey("users.id"), nullable=False)
    campaign_id = Column(ForeignKey("campaigns.id"), nullable=False)
    alert_type  = Column(Enum(AlertType), nullable=False)
    threshold   = Column(Float, nullable=False)   # e.g. 1.0 for CTR < 1%
    is_active   = Column(Boolean, default=True)

    user = relationship("User", back_populates="alert_rules")
    campaigns = relationship("Campaign", back_populates="alert_rules")

class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id     = Column(ForeignKey("users.id"), nullable=False)
    campaign_id = Column(ForeignKey("campaigns.id"), nullable=False)
    alert_type  = Column(Enum(AlertType), nullable=False)
    message     = Column(String, nullable=False)
    is_read     = Column(Boolean, default=False)

    user = relationship("User", back_populates="notifications")
    campaigns = relationship("Campaign", back_populates="notifications")