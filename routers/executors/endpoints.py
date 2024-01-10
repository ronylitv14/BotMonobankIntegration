from typing import List

from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from routers.users.schemes import UserResponseModel
from routers.executors.schemes import ExecutorProfileRequest, UpdateApplicationStatusRequest, TaskModel, \
    ExecutorResponse

from database.crud import get_executor_orders, get_executor, get_all_executors_profiles, create_executor_profile, \
    get_executor_applications, TaskStatus

executors_router = APIRouter(
    prefix="/executors",
    tags=["executors"]
)


# Retrieve executor orders by executor ID
@executors_router.get("/{executor_id}/{status}", response_model=list[TaskModel])
async def get_executor_tasks(executor_id: int, status: TaskStatus):
    orders = await get_executor_orders(executor_id, status)
    if not orders:
        raise HTTPException(status_code=404, detail="Executor orders not found.")
    return orders


from sqlalchemy.exc import IntegrityError


# Create an executor profile
@executors_router.post("/")
async def create_executor(profile_data: ExecutorProfileRequest):
    try:
        await create_executor_profile(**profile_data.model_dump())

    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something wrong with saving data!")
    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content={"message": "Executor profile created successfully."})


# Retrieve an executor by user ID
@executors_router.get("/{user_id}", response_model=ExecutorResponse)
async def get_executor_data(user_id: int):
    executor = await get_executor(user_id)
    if not executor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Executor not found.")
    return executor


# Retrieve all executors
@executors_router.get("/", response_model=List[UserResponseModel])
async def get_all_executors_data():
    executors = await get_all_executors_profiles()
    if not executors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Executor not found.")
    return executors


# Get executor applications
@executors_router.get("/applications/", response_model=List[ExecutorResponse])
async def get_applications():
    applications = await get_executor_applications()
    if not applications:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No applications found.")
    return applications
