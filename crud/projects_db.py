from sqlalchemy.orm import Session
from models.models_db import Projects
from schemas import projects_schema as ps

""" crud для projects"""

def create_projects(db: Session, project: ps.CreateProject) -> Projects:
    """ ств проєкт"""

    new_project = Projects(
        title = project.title,
        description = project.description,
        status = project.status,
        owner_id = project.owner_id
    )

    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project) # оновлюємо об'єк щоб отримати id...
        return new_project
    except Exception as e:
        db.rollback()
        raise e


def get_project(db: Session, id_project: int):
    return db.query(Projects).filter(Projects.id_project == id_project).first()

def delete_projects(db: Session, project):

    try:
        db.delete(project)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


