from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String(length=120), nullable=False)
    username = Column(String(length=20), nullable=False)
    password = Column(String(length=100), nullable=False)
    bio = Column(Text, nullable=True)
    country = Column(String(length=50), nullable=True)
    city = Column(String(length=50), nullable=True)
    facebook_link = Column(String(length=200), nullable=True)
    x_link = Column(String(length=200), nullable=True)
    linkedin_link = Column(String(length=200), nullable=True)
    instagram_link = Column(String(length=200), nullable=True)
    phone_number = Column(String(length=30), nullable=True)

    campaigns = relationship("Campaign", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")

    def __str__(self):
        return self.username
