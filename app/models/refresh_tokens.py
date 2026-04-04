from app.models.base_model import BaseModel
from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship

class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"
    
    user_id = Column(ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    is_revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_tokens")

    def __str__(self):
        return f"RefreshToken(user_id={self.user_id}, expires_at={self.expires_at}, is_revoked={self.is_revoked})"
    