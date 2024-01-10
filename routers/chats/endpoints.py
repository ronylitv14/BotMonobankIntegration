from typing import List, Optional

from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from database.crud import save_chat_data, get_chats_by_taskid, get_recent_clients, get_chat_object, update_chat_type, \
    get_all_user_chats, update_group_title
from routers.chats.schemes import ChatDataRequest, ChatObjectRequest, UpdateChatStatusRequest, UpdateGroupTitleRequest, \
    ChatResponse
from routers.users.schemes import UserResponseModel
from sqlalchemy.exc import IntegrityError, DBAPIError

chats_router = APIRouter(
    prefix="/chats",
    tags=["chats"]
)


# Save chat data
@chats_router.post("/", response_model=ChatResponse)
async def save_chat(chat_data: ChatDataRequest):
    try:
        chat = await save_chat_data(**chat_data.model_dump())
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving chat")

    return JSONResponse(content=ChatResponse.model_validate(chat).model_dump(), status_code=status.HTTP_201_CREATED)


# Get recent clients for an executor
@chats_router.get("/recent-clients/{executor_id}", response_model=List[UserResponseModel])
async def get_recent_clients_data(executor_id: int):
    clients = await get_recent_clients(executor_id)
    if not clients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clients not found.")
    return clients


# Get chats by task ID
@chats_router.get("/chats-by-task/{task_id}", response_model=List[ChatResponse])
async def get_chats(task_id: int):
    chats = await get_chats_by_taskid(task_id)
    if not chats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chats not found.")
    return chats


@chats_router.get("/", response_model=ChatResponse)
async def get_chat(
        chat_id: Optional[int] = None,
        db_chat_id: Optional[int] = None,
        supergroup_id: Optional[int] = None
):
    try:
        chat = await get_chat_object(chat_id=chat_id, db_chat_id=db_chat_id, supergroup_id=supergroup_id)
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat object not found.")
        return chat
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Specify one of params!")


@chats_router.patch("/type/", response_description="No data retrieved! Only message")
async def update_chat(chat_data: UpdateChatStatusRequest):
    try:
        await update_chat_type(
            db_chat_id=chat_data.db_chat_id,
            supergroup_id=chat_data.supergroup_id,
            chat_type=chat_data.chat_type
        )
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save data!")
    except DBAPIError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to use DBAPi")

    return JSONResponse(content={"message": "Chat status updated successfully."}, status_code=status.HTTP_200_OK)


# Get all chats for a user
@chats_router.get("/user/{client_id}", response_model=List[ChatResponse])
async def get_all_users(client_id: int):
    chats = await get_all_user_chats(client_id)
    return chats


# Update the title of a chat group
@chats_router.patch("/group-title/", response_description="Only message retrieved!")
async def update_title(request: UpdateGroupTitleRequest):
    try:
        await update_group_title(request.db_chat_id, request.group_name)
        return JSONResponse(content={"message": "Group title updated successfully."}, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
