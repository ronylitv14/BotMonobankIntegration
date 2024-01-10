from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from database.models import FileType, PropositionBy, TaskStatus


class TaskCreateRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    client_id: int
    status: TaskStatus
    price: str
    subjects: List[str]
    work_type: List[str]
    deadline: Optional[date] = None
    files: Optional[List[str]] = None
    files_type: Optional[List[FileType]] = None
    description: Optional[str] = None
    proposed_by: Optional[PropositionBy] = None
    executor_id: Optional[int] = None


class TaskResponse(TaskCreateRequest):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    task_id: int


class TaskUpdateFilesRequest(BaseModel):
    files: List[str]


class TaskUpdateStatusRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    status: TaskStatus


class ProposedDealsRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    proposed_by: PropositionBy  # Assuming PropositionBy can be represented as a string
    user_id: int
