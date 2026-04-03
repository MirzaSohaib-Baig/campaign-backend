import re
from pydantic import BaseModel, field_validator
from app.config.settings import settings
from typing import Optional

class SignUp(BaseModel):
    name: str
    username: str
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        if not re.match(settings.PASSWORD_REGEX, value):
            raise ValueError(
                "Password must contain at least one uppercase, one lowercase, one digit and one special character"
            )
        return value


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

    @field_validator("password")
    def validate_password(cls, value):
        if value is None or value == '':
            return value
        if not re.match(settings.PASSWORD_REGEX, value):
            raise ValueError(
                "Password must contain at least one uppercase, one lowercase, one digit and one special character"
            )
        return value