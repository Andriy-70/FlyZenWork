from pydantic import BaseModel

class CreateProject(BaseModel):
    title: str
    description: str
    owner_id: int