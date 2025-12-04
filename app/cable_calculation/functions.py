from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import CableCalculation, User
from app.schemas.cable_calculation import CableCalculationCreate

def create_cable_calculation(db: Session, project_id: int, calc: CableCalculationCreate, owner_id: int):
    latest_version = db.query(func.max(CableCalculation.version)).filter_by(project_id=project_id).scalar() or 0
    new_version = latest_version + 1

    db_calc = CableCalculation(
        project_id=project_id,
        version=new_version,
        owner_id=owner_id,
        **calc.dict()
    )
    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc

def get_cable_calculation(db: Session, project_id: int, version: int):
    return db.query(CableCalculation).filter_by(project_id=project_id, version=version).first()

def get_all_versions(db: Session, project_id: int):
    return db.query(CableCalculation.version).filter_by(project_id=project_id).distinct().order_by(CableCalculation.version).all()

def update_cable_calculation(db: Session, calc_id: int, calc_update: CableCalculationCreate):
    db_calc = db.query(CableCalculation).filter_by(id=calc_id).first()
    if not db_calc:
        return None
    for key, value in calc_update.dict().items():
        setattr(db_calc, key, value)
    db.commit()
    db.refresh(db_calc)
    return db_calc

def delete_cable_calculation(db: Session, calc_id: int, current_user: User):
    db_calc = db.query(CableCalculation).filter_by(id=calc_id).first()
    if not db_calc:
        return None
    # Check ownership: only owner or admin can delete
    if db_calc.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this calculation")
    db.delete(db_calc)
    db.commit()
    return True
