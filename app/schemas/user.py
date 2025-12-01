from pydantic import BaseModel

class UserSchema(BaseModel):
    id: int
    username: str
    role: str
    class Config:
        orm_mode = True

class UserUpdateSchema(BaseModel):
    role: str | None = None
