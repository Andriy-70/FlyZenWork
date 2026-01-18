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

class StageCreate(BaseModel):
    title: str
    description: Optional[str] = None
    order: int = 0

class StageResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    is_completed: bool
    order: int

    class Config:
        from_attributes = True

# Оновлюємо відповідь по проєкту, щоб вона включала етапи
class ProjectDetailResponse(ProjectResponse):
    stages: list[StageResponse] = []