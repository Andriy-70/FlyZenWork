from sqlalchemy.orm import Session
from models.models_db import Projects
from schemas import projects_schema as ps

""" crud для projects"""

def create_projects(db: Session, project)