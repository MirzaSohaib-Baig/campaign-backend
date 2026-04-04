import re
from pydantic import BaseModel, field_validator, model_validator
from app.config.settings import settings
from typing import Optional

class SignUp(BaseModel):
    name: str
    username: str
    password: str
    confirm_password: str

    @field_validator("password")
    def validate_password(cls, value):
        if not re.match(settings.PASSWORD_REGEX, value):
            raise ValueError(
                "Password must contain at least one uppercase, one lowercase, one digit and one special character"
            )
        return value
    
    @field_validator("username")
    def validate_username(cls, value):
        if not re.match(settings.EMAIL_REGEX, value):
            raise ValueError(
                "Username must be a valid email address"
            )
        return value

    @model_validator(mode="after")
    def validate_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class Login(BaseModel):
    username: str
    password: str
    keepSignedIn: Optional[bool] = False

class ChangePassword(BaseModel):
    current_password: str
    new_password: str

class UpdateUser(BaseModel):
    user_id: str
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    bio: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    facebook_link: Optional[str] = None
    x_link: Optional[str] = None
    linkedin_link: Optional[str] = None
    instagram_link: Optional[str] = None
    phone_number: Optional[str] = None

    @field_validator("password")
    def validate_password(cls, value):
        if value is None or value == '':
            return value
        if not re.match(settings.PASSWORD_REGEX, value):
            raise ValueError(
                "Password must contain at least one uppercase, one lowercase, one digit and one special character"
            )
        return value

    @field_validator("username")
    def validate_username(cls, value):
        if value is None or value == '':
            return value
        if not re.match(settings.EMAIL_REGEX, value):
            raise ValueError(
                "Username must be a valid email address"
            )
        return value