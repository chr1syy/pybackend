from pydantic import BaseModel, field_validator, Field
import re

def validate_password_strength(password: str) -> str:
    """
    Validate password strength with comprehensive checks.
    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - Not in common weak passwords list
    """
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters long")

    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password):
        raise ValueError("Password must contain at least one special character")

    # Extended list of weak passwords
    weak_passwords = {
        "password", "password123", "password1234", "123456", "12345678", "123456789",
        "qwerty", "qwerty123", "admin", "admin123", "letmein", "welcome", "monkey",
        "dragon", "master", "sunshine", "princess", "football", "shadow", "123123"
    }
    if password.lower() in weak_passwords:
        raise ValueError("Password is too common and easily guessable")

    return password

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=12)

    @field_validator("new_password")
    def validate_strength(cls, v):
        return validate_password_strength(v)

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str = Field(..., min_length=12)

    @field_validator("new_password")
    def validate_strength(cls, v):
        return validate_password_strength(v)