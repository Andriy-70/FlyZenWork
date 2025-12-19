from sqlalchemy.orm import Session
from models.models_db import Projects
from schemas import projects_schema as ps

""" crud для projects"""

def create_projects(db: Session, project: ps.CreateProject, owner_id: int) -> Projects:
    """ ств проєкт"""

    new_project = Projects(
        title = project.title,
        description = project.description,
        status = project.status,
        owner_id = owner_id
    )

    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project) # оновлюємо об'єк щоб отримати id...
        return new_project
    except Exception as e:
        db.rollback()
        raise e


def get_project(db: Session, id_project: int, owner_id: int):
    return db.query(Projects).filter(Projects.id_project == id_project,
                                      Projects.owner_id == owner_id).first()


def delete_projects(db: Session, id_project: int, owner_id: int):

    try:
        project = get_project(db, id_project, owner_id)
        if not project:
            return False

        db.delete(project)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


def update_projects(db: Session, id_project: int, owner_id: int, update_data: ps.UpdateProject):

    try:
        project = get_project(db, id_project, owner_id)
        if not project:
            return False

        # беремо тільки ті поля які поміняли
        update_project = update_data.model_dump(exclude_unset=True)

        # оновлюємо проєкт
        for key,value in update_project.items():
            setattr(project, key, value)

        db.commit()
        db.refresh(project) # оновили в бд

        return project
    except Exception as e:
        db.rollback()
        raise e