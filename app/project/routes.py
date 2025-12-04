from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.db import get_db
from app.utils.auth import get_current_user
from app.models import Project, User
from app.schemas.projects import ProjectCreate, ProjectUpdate, ProjectOut

router = APIRouter()

# Create
@router.post("/", response_model=ProjectOut)
def create_project(request: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if db.query(Project).filter(Project.project_number == request.project_number).first():
        raise HTTPException(status_code=400, detail="Project number already exists")
    project = Project(**request.dict())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

# Read all
@router.get("/", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # All authenticated users can see all projects (collaborative environment)
    return db.query(Project).all()

# Read one
@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# Update
@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, request: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in request.dict(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project

# Delete
@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Check ownership
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    db.delete(project)
    db.commit()
    return {"msg": f"Project {project_id} deleted"}
