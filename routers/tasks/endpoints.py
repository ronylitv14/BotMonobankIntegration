from typing import List

from fastapi import status, Query
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from database.models import TaskStatus, PropositionBy
from routers.tasks.schemes import TaskCreateRequest, TaskUpdateFilesRequest, TaskUpdateStatusRequest, \
    ProposedDealsRequest, TaskResponse
from database.crud import UserType
from database.crud import save_task_to_db, update_task_files, update_task_status, get_all_tasks, get_user_by_task_id, \
    get_proposed_deals, get_task
from sqlalchemy.exc import IntegrityError
from routers.users.schemes import UserResponseModel

task_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


# Save a task to the database
@task_router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreateRequest):
    try:
        task = await save_task_to_db(**task_data.model_dump())
    except (IntegrityError, AttributeError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error with saving task data!")
    return task

# Update task status
@task_router.patch("/status/{task_id}")
async def update_status(task_id: int, update_data: TaskUpdateStatusRequest):
    result = await update_task_status(task_id, update_data.status)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or update failed.")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Task status updated successfully."})


# Retrieve a task by its ID
@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task_data(task_id: int):
    task = await get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return task


@task_router.get("/", response_model=List[TaskResponse])
async def get_all_tasks_db(
        user_id: int,
        user_type: UserType,
        task_id: int = None,
        task_status: List[TaskStatus] = Query(),  # Modify this line
):
    try:
        tasks = await get_all_tasks(user_id, user_type, *task_status, task_id=task_id)
    except IntegrityError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error with retrieving data!")
    return tasks


@task_router.get("/client-by-task/{task_id}", response_model=UserResponseModel)
async def get_user_by_task(task_id: int):
    user = await get_user_by_task_id(task_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@task_router.get("/proposed-deals/{user_id}/{proposed_by}", response_model=List[TaskResponse])
async def get_deals(user_id: int, proposed_by: PropositionBy):
    deals = await get_proposed_deals(user_id=user_id, proposed_by=proposed_by)
    if not deals:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No proposed deals found.")
    return deals
