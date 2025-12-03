from pydantic import BaseModel

class CompleteRegistrationRequest(BaseModel):
    email: str
    username: str
    code: str
    password: str