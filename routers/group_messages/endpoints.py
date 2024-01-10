from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from routers.group_messages.schemes import GroupMessageRequest, GroupMessageResponse
from database.crud import add_group_message, get_group_message

group_router = APIRouter(
    prefix="/group-messages",
    tags=["group-messages"]
)


@group_router.post("/")
async def save_group_message(message_data: GroupMessageRequest):
    result = await add_group_message(**message_data.model_dump())
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group message could not be added.")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Group message added successfully."})


# Retrieve a group message by task ID
@group_router.get("/{task_id}", response_model=GroupMessageResponse)
async def get_group_msg_by_task(task_id: int):
    message = await get_group_message(task_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group message not found.")
    return message
