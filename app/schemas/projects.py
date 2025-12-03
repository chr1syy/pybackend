from pydantic import BaseModel

class ProjectBase(BaseModel):
    project_number: str
    name: str
    description: str | None = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class ProjectOut(ProjectBase):
    id: int

    class Config:
        orm_mode = True
