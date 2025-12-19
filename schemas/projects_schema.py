from pydantic import BaseModel
from models.models_db import ProjectStatus
from typing import Optional

class CreateProject(BaseModel):
    title: str
    description: str
    status: ProjectStatus = ProjectStatus.active  # за замовчуванням

#робим поля не обов'язковими
class UpdateProject(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
