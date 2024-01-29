from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from database.models import FileType, ProfileStatus, TaskStatus, PropositionBy


class ExecutorProfileRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    user_id: int
    tags: List[str]
    description: str
    work_examples: List[str]
    work_files_type: List[FileType]


class ExecutorResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
    user_id: int
    profile_state: ProfileStatus
    executor_id: int
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    work_examples: List[str]
    work_files_type: List[FileType]


class UpdateApplicationStatusRequest(BaseModel):
    executor_id: int
    new_profile_state: ProfileStatus


class TaskModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True, arbitrary_types_allowed=True)
    task_id: int
    executor_id: Optional[int] = None
    client_id: Optional[int] = None
    status: TaskStatus
    price: str
    date_added: datetime
    deadline: Optional[datetime] = None
    proposed_by: PropositionBy = PropositionBy.public
    files: Optional[List[str]] = None
    files_type: Optional[List[FileType]] = None
    description: Optional[str] = None
    subjects: List[str]
    work_type: List[str]
