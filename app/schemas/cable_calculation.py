from pydantic import BaseModel
from datetime import datetime

class CableCalculationBase(BaseModel):
    origin: str
    destination: str
    cable_type: str
    cable_length_m: float
    number_of_cables: int
    total_cores: int
    loaded_cores: int
    cross_section_l: float
    cross_section_pe: float
    laying_type: str
    fuse_rating_a: float
    nominal_current_a: float


class CableCalculationCreate(CableCalculationBase):
    pass


class CableCalculationRead(CableCalculationBase):
    id: int
    project_id: int
    version: int
    created_at: datetime

    class Config:
        from_attributes = True  # For Pydantic v2, use orm_mode = True for v1

    
