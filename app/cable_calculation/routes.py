from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from typing import List

from app.schemas.cable_calculation import CableCalculationCreate, CableCalculationRead
from app.cable_calculation.functions import (
    create_cable_calculation,
    get_cable_calculation,
    get_cable_calculations_by_version,
    get_all_versions,
    update_cable_calculation,
    delete_cable_calculation,  
    )

from app.models import User
from app.utils.auth import get_current_user
from app.utils.db import get_db

router = APIRouter()


@router.post("/", response_model=CableCalculationRead)
def create_calc(
    project_id: int = Query(..., description="Project ID"),
    new_version: bool = Query(False, description="Create new version if True, add to latest if False"),
    calc: CableCalculationCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a cable calculation.
    
    - **new_version=True**: Creates a new version (increments version number)
    - **new_version=False**: Adds to the latest existing version
    """
    return create_cable_calculation(db, project_id, calc, current_user.id, new_version)

@router.get("/{version}", response_model=List[CableCalculationRead])
def read_calcs_by_version(
    version: int,
    project_id: int = Query(..., description="Project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get ALL cable calculations for a specific version.
    
    Returns a list of all cables in this version.
    """
    calcs = get_cable_calculations_by_version(db, project_id, version)
    
    if not calcs:
        # Return empty list instead of 404 for better UX
        return []
    
    return calcs

@router.get("/versions/list", response_model=List[int])
def list_versions(
    project_id: int = Query(..., description="Project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all version numbers for a project."""
    versions = get_all_versions(db, project_id)
    return [v[0] for v in versions]

@router.put("/{calc_id}", response_model=CableCalculationRead)
def update_calc(
    calc_id: int,
    calc: CableCalculationCreate,
    project_id: int = Query(..., description="Project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a specific cable calculation."""
    updated = update_cable_calculation(db, calc_id, calc)
    if not updated:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return updated

@router.delete("/{calc_id}")
def delete_calc(
    calc_id: int,
    project_id: int = Query(..., description="Project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific cable calculation."""
    deleted = delete_cable_calculation(db, calc_id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return {"detail": "Calculation deleted"}