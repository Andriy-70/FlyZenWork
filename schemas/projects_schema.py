from pydantic import BaseModel
from models.models_db import ProjectStatus
from typing import Optional
from datetime import datetime

class CreateProject(BaseModel):
    title: str
    description: str
    status: ProjectStatus = ProjectStatus.active  # за замовчуванням

#робим поля не обов'язковими
class UpdateProject(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None

class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    owner_id: int
    created_at: datetime