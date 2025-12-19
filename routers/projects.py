from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from sqlalchemy import func
from crud.database  import get_db
from crud.projects_db import create_projects, get_project, delete_projects
from utils.security import get_current_user
from models.models_db import Projects, Users
from schemas.projects_schema import CreateProject

router = APIRouter(
    prefix="/projects",
    tags=["CRUD project"],
)

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_project(
        project: CreateProject,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)):

    # чи існує вже такий проект у данного користувача
    existing_project = db.query(Projects).filter(
        func.lower(Projects.title) == func.lower(project.title),
        Projects.owner_id == current_user.id
    ).first()

    if existing_project:
        raise HTTPException(
            status_code = 400,
            detail="У вас вже є проєкт з такою назвою. Оберіть іншу"
        )

    return create_projects(db, project, current_user.id)

@router.get("/{project_id}", status_code=status.HTTP_200_OK)
def read_project(project_id: int,
                 db: Session = Depends(get_db),
                 current_user: Users = Depends(get_current_user)):

    project = get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Проєкт не найдено")

    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int,
                   db: Session = Depends(get_db),
                   current_user: Users = Depends(get_current_user)):

    delete_status = delete_projects(db, project_id, current_user.id)
    if not delete_status:
        raise HTTPException(status_code=404, detail="Проєкт не вдалось видалити")

    return None