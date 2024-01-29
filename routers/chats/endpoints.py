from typing import List, Optional
from fastapi import Security
from config import verify_token
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from database.cruds.chats import save_chat_data, get_chats_by_taskid, get_recent_clients, get_chat_object, \
    update_chat_type, get_all_user_chats, update_group_title, get_unused_chats, check_chat_existence, update_chat_fields
from routers.chats.schemes import ChatDataRequest, UpdateChatStatusRequest, UpdateGroupTitleRequest, \
    ChatResponse, UpdateChatField
from routers.users.schemes import UserResponseModel
from sqlalchemy.exc import IntegrityError, DBAPIError

chats_router = APIRouter(
    prefix="/chats",
    tags=["chats"],
    dependencies=[Security(verify_token)]
)


# Save chat data
@chats_router.post("/", response_model=ChatResponse)
async def save_chat(chat_data: ChatDataRequest):
    try:
        chat = await save_chat_data(**chat_data.model_dump())
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving chat")

    return chat


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


@chats_router.patch("/{db_chat_id}")
async def update_chat_field(db_chat_id: int, chat_data: UpdateChatField):
    try:

        if not any(
                [
                    chat_data.participants_count,
                    chat_data.active is not None,
                    chat_data.participants_count,
                    chat_data.in_use is not None
                ]
        ):
            raise AttributeError("One of the PATCH params has to be specified!!!")

        fields = {key: value for key, value in chat_data.model_dump().items() if value is not None}

        await update_chat_fields(
            db_chat_id=db_chat_id,
            fields=fields
        )

    except AttributeError as err:
        raise HTTPException(status_code=400, detail=str(err))

    except (IntegrityError, DBAPIError) as err:
        raise HTTPException(status_code=500, detail=str(err))


# Get all unused chats
@chats_router.get("/unused/", response_model=List[ChatResponse])
async def get_all_unused_chats():
    chats = await get_unused_chats()
    return chats


@chats_router.get("/exists/")
async def chat_exists(
        task_id: int,
        executor_id: int,
        client_id: int
):
    try:
        chat = await check_chat_existence(
            task_id=task_id,
            client_id=client_id,
            executor_id=executor_id
        )
        if not chat:
            return JSONResponse(content={"exists": False}, status_code=status.HTTP_404_NOT_FOUND)
        return JSONResponse(content={"exists": True}, status_code=status.HTTP_200_OK)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Specify at least one parameter!")
