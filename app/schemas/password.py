from pydantic import BaseModel, field_validator, Field

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=12)

    @field_validator("new_password")
    def validate_strength(cls, v):
        weak = {"password", "123456", "qwerty", "admin", "letmein"}
        if v.lower() in weak:
            raise ValueError("Weak password")
        return v

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str