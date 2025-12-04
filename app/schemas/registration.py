from pydantic import BaseModel, EmailStr, Field, field_validator
from app.schemas.password import validate_password_strength

class CompleteRegistrationRequest(BaseModel):
    email: EmailStr  # Validates email format
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    code: str = Field(..., max_length=64)
    password: str = Field(..., min_length=12, max_length=128)

    @field_validator("password")
    def validate_password(cls, v):
        return validate_password_strength(v)