from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import CableCalculation, User
from app.schemas.cable_calculation import CableCalculationCreate

def create_cable_calculation(
    db: Session,
    project_id: int,
    calc: CableCalculationCreate,
    owner_id: int,
    new_version: bool = False
):
    """
    Create a cable calculation.
    
    Args:
        new_version: If True, creates a new version. If False, adds to latest version.
    """
    if new_version:
        # Create a new version by incrementing
        latest_version = db.query(func.max(CableCalculation.version)).filter_by(
            project_id=project_id
        ).scalar() or 0
        version = latest_version + 1
    else:
        # Add to existing (latest) version
        latest_version = db.query(func.max(CableCalculation.version)).filter_by(
            project_id=project_id
        ).scalar()
        
        if latest_version is None:
            # No versions exist yet, create version 1
            version = 1
        else:
            # Add to the latest existing version
            version = latest_version

    db_calc = CableCalculation(
        project_id=project_id,
        version=version,
        owner_id=owner_id,
        **calc.dict()
    )
    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc

def get_cable_calculation(db: Session, project_id: int, version: int):
    """
    DEPRECATED: Use get_cable_calculations_by_version instead.
    Returns a single calculation for backwards compatibility.
    """
    calc = db.query(CableCalculation).filter(
        CableCalculation.project_id == project_id,
        CableCalculation.version == version
    ).first()
    return calc

def get_cable_calculations_by_version(db: Session, project_id: int, version: int):
    """
    Get ALL cable calculations for a specific project and version.
    
    Returns:
        List of CableCalculation objects
    """
    calcs = db.query(CableCalculation).filter(
        CableCalculation.project_id == project_id,
        CableCalculation.version == version
    ).order_by(CableCalculation.created_at).all()
    
    return calcs

def get_all_versions(db: Session, project_id: int):
    """Get all unique version numbers for a project."""
    versions = db.query(CableCalculation.version).filter(
        CableCalculation.project_id == project_id
    ).distinct().order_by(CableCalculation.version.desc()).all()
    
    return versions

def update_cable_calculation(db: Session, calc_id: int, calc: CableCalculationCreate):
    """Update a specific cable calculation."""
    db_calc = db.query(CableCalculation).filter(CableCalculation.id == calc_id).first()
    if not db_calc:
        return None
    
    for key, value in calc.dict().items():
        setattr(db_calc, key, value)
    
    db.commit()
    db.refresh(db_calc)
    return db_calc

def delete_cable_calculation(db: Session, calc_id: int, current_user):
    """Delete a specific cable calculation."""
    db_calc = db.query(CableCalculation).filter(CableCalculation.id == calc_id).first()
    if not db_calc:
        return False
    
    # Optional: Add ownership check
    # if db_calc.owner_id != current_user.id and current_user.role != "admin":
    #     return False
    
    db.delete(db_calc)
    db.commit()
    return True
