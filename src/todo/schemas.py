from pydantic import BaseModel

from src.todo.utils import StatusEnum


class TaskScheme(BaseModel):
    title: str
    description: str
    status: StatusEnum = StatusEnum.not_started
