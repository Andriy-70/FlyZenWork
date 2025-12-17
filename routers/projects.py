from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from sqlalchemy import func
from crud.database  import get_db
from crud.projects_db import create_projects, get_project, delete_projects
from models.models_db import Projects
from schemas.projects_schema import CreateProject

router = APIRouter(
    prefix="/projects",
    tags=["CRUD project"],
)

@router.post("/project", status_code=status.HTTP_201_CREATED)
def create_project(project: CreateProject, db: Session = Depends(get_db)):

    # чи існує вже такий проект у данного користувача
    existing_project = db.query(Projects).filter(
        func.lower(Projects.title) == func.lower(project.title),
        Projects.owner_id == project.owner_id
    ).first()

    if existing_project:
        raise HTTPException(
            status_code = 400,
            detail="У вас вже є проєкт з такою назвою. Оберіть іншу"
        )

    return create_projects(db, project)