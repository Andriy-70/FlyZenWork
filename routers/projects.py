from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from sqlalchemy import func
from crud.database  import get_db
from crud.projects_db import create_projects, get_project, delete_projects, update_projects
from utils.security import get_current_user
from models.models_db import Projects, Users, ProjectRequests, RequestStatus
from schemas.projects_schema import CreateProject, UpdateProject, ProjectResponse, ProjectStatus

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
        raise HTTPException(
            status_code=404,
            detail="Проєкт не найдено"
        )

    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int,
                   db: Session = Depends(get_db),
                   current_user: Users = Depends(get_current_user)):

    delete_status = delete_projects(db, project_id, current_user.id)
    if not delete_status:
        raise HTTPException(
            status_code=404,
            detail="Проєкт не вдалось видалити"
        )

    return None

@router.patch("/{project_id}", status_code=status.HTTP_200_OK)
def update_project(project_id: int,
                    update_prj: UpdateProject,
                    db: Session = Depends(get_db),
                    current_user: Users = Depends(get_current_user)):

    project = update_projects(db, project_id, current_user.id, update_prj)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Проєкт не вдалось змінити"
        )

    return project


@router.get("/all", response_model=list[ProjectResponse], status_code=status.HTTP_200_OK)
def read_all_my_projects(
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    """ Отримати список усіх проектів, які належать поточному користувачу """

    # Шукаємо всі проекти, де власник — наш залогінений юзер
    projects = db.query(Projects).filter(Projects.owner_id == current_user.id).all()

    return projects


@router.post("/{project_id}/join", status_code=status.HTTP_201_CREATED)
def request_to_join(
        project_id: int,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    # Перевіряємо проект по правильному полю: id_project
    project = db.query(Projects).filter(Projects.id_project == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проєкт не знайдено")

    if project.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Ви є власником цього проєкту")

    existing_request = db.query(ProjectRequests).filter(
        ProjectRequests.project_id == project_id,
        ProjectRequests.user_id == current_user.id
    ).first()

    if existing_request:
        raise HTTPException(status_code=400, detail="Запит уже надіслано")

    new_request = ProjectRequests(
        project_id=project_id,
        user_id=current_user.id,
        status=RequestStatus.pending
    )
    db.add(new_request)
    db.commit()
    return {"message": "Запит надіслано власнику проєкту"}


# 2. Метод для власника: Підтвердити або Відхилити
@router.patch("/requests/{request_id}/decision", status_code=status.HTTP_200_OK)
def handle_join_request(
        request_id: int,
        approve: bool,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    # Шукаємо запит
    join_request = db.query(ProjectRequests).filter(ProjectRequests.id == request_id).first()
    if not join_request:
        raise HTTPException(status_code=404, detail="Запит не знайдено")

    # Перевіряємо власника через правильне поле id_project
    project = db.query(Projects).filter(Projects.id_project == join_request.project_id).first()
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Ви не є власником цього проєкту")

    if join_request.status != RequestStatus.pending:
        raise HTTPException(status_code=400, detail="Рішення по цьому запиту вже прийнято")

    join_request.status = RequestStatus.accepted if approve else RequestStatus.rejected
    db.commit()

    return {"message": f"Запит {'підтверджено' if approve else 'відхилено'}"}