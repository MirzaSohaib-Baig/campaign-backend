from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel

class Campaign(BaseModel):
    __tablename__ = "campaigns"
    
    name = Column(Text, nullable=False)
    client = Column(Text, nullable=False)
    channel = Column(String(length=50), nullable=False)
    status = Column(String(length=20), nullable=False)
    impressions = Column(Integer, nullable=False)
    clicks = Column(Integer, nullable=False)
    conversions = Column(Integer, nullable=False)
    spend = Column(Float, nullable=False)
    budget = Column(Float, nullable=False)
    revenue = Column(Float, nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="campaigns")

    def __str__(self):
        return self.name