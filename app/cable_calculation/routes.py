from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.cable_calculation import CableCalculationCreate, CableCalculationRead
from app.cable_calculation.functions import (
    create_cable_calculation,
    get_cable_calculation,
    get_all_versions,
    update_cable_calculation,
    delete_cable_calculation,  
    )

from app.models import User
from app.utils.auth import get_current_user
from app.utils.db import get_db

router = APIRouter()


@router.post("/", response_model=CableCalculationRead)
def create_calc(project_id: int, calc: CableCalculationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_cable_calculation(db, project_id, calc, current_user.id)

@router.get("/{version}", response_model=CableCalculationRead)
def read_calc(project_id: int, version: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    calc = get_cable_calculation(db, project_id, version)
    if not calc:
        raise HTTPException(status_code=404, detail="Version not found")
    return calc

@router.get("/versions/list", response_model=list[int])
def list_versions(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    versions = get_all_versions(db, project_id)
    return [v[0] for v in versions]

@router.put("/{calc_id}", response_model=CableCalculationRead)
def update_calc(project_id: int, calc_id: int, calc: CableCalculationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = update_cable_calculation(db, calc_id, calc)
    if not updated:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return updated

@router.delete("/{calc_id}")
def delete_calc(project_id: int, calc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted = delete_cable_calculation(db, calc_id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return {"detail": "Calculation deleted"}