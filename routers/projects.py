from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from sqlalchemy import func
from crud.database  import get_db
from crud.projects_db import create_projects, get_project, delete_projects, update_projects
from utils.security import get_current_user
from models.models_db import Projects, Users, ProjectRequests, RequestStatus, ProjectStage
from schemas.projects_schema import CreateProject, UpdateProject, ProjectResponse, ProjectDetailResponse, StageCreate

router = APIRouter(
    prefix="/projects",
    tags=["CRUD project"],
)


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)  # Додай response_model
def create_project(
        project: CreateProject,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)):
    # Перевірка на дублікат
    existing_project = db.query(Projects).filter(
        func.lower(Projects.title) == func.lower(project.title),
        Projects.owner_id == current_user.id
    ).first()

    if existing_project:
        raise HTTPException(
            status_code=400,
            detail="У вас вже є проєкт з такою назвою. Оберіть іншу"
        )

    new_project = create_projects(db, project, current_user.id)

    return new_project

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


@router.get("/{project_id}/details", response_model=ProjectDetailResponse)
def get_project_details(
        project_id: int,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
):
    # 1. Шукаємо проєкт
    project = db.query(Projects).filter(Projects.id_project == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проєкт не знайдено")

    # 2. Перевіряємо доступ (Власник АБО прийнятий учасник)
    is_member = db.query(ProjectRequests).filter(
        ProjectRequests.project_id == project_id,
        ProjectRequests.user_id == current_user.id,
        ProjectRequests.status == RequestStatus.accepted
    ).first()

    if project.owner_id != current_user.id and not is_member:
        raise HTTPException(status_code=403, detail="У вас немає доступу до цього проєкту")

    # 3. Дістаємо етапи
    stages = db.query(ProjectStage).filter(ProjectStage.project_id == project_id).order_by(ProjectStage.order).all()

    # Додаємо етапи в об'єкт проєкту перед поверненням
    project.stages = stages
    return project


@router.post("/{project_id}/stages", status_code=status.HTTP_201_CREATED)
def create_stage(
    project_id: int,
    stage_data: StageCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    # Перевірка на Тімліда
    project = db.query(Projects).filter(Projects.id_project == project_id).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Тільки Тімлід може створювати етапи")

    new_stage = ProjectStage(**stage_data.model_dump(), project_id=project_id)
    db.add(new_stage)
    db.commit()
    db.refresh(new_stage)
    return new_stage

@router.delete("/stages/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stage(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    stage = db.query(ProjectStage).filter(ProjectStage.id == stage_id).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Етап не знайдено")

    project = db.query(Projects).filter(Projects.id_project == stage.project_id).first()
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Тільки Тімлід може видаляти етапи")

    db.delete(stage)
    db.commit()
    return None