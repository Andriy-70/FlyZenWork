from pydantic import BaseModel
from models.models_db import ProjectStatus

class CreateProject(BaseModel):
    title: str
    description: str
    status: ProjectStatus = ProjectStatus.active  # Додай це
    owner_id: int
