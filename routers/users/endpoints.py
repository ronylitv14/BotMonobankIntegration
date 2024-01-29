from typing import List
from fastapi import Security
from config import verify_token
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException
from fastapi import status
from fastapi.responses import JSONResponse

from routers.users.schemes import UserCreateRequest, UserUpdateRequest, BanStatusRequest, GetSimilarityUsersRequest, \
    UserResponseModel

from database.cruds.users import get_user_auth, delete_user_from_db, save_user_to_db, update_user_email, \
    update_user_phone, update_user_nickname, get_default_users, update_ban_status, get_similarity_users

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Security(verify_token)]
)


# Get a user by Telegram ID
@users_router.get("/{telegram_id}", response_model=UserResponseModel)
async def get_user(telegram_id: int):
    user = await get_user_auth(telegram_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


# Delete a user
@users_router.delete("/{telegram_id}")
async def delete_user(telegram_id: int):
    try:
        await delete_user_from_db(telegram_id)
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="User hasn`t been deleted! Error acquired!")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "User deleted successfully."})


# Create a new user
@users_router.post("/")
async def create_user(user_data: UserCreateRequest):
    result = await save_user_to_db(**user_data.model_dump())
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User could not be created.")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User created successfully"})


# Update user details
@users_router.patch("/{telegram_id}")
async def update_user(telegram_id: int, user_data: UserUpdateRequest):
    try:
        if user_data.email:
            await update_user_email(telegram_id, user_data.email)
        if user_data.nickname:
            await update_user_nickname(telegram_id, user_data.nickname)
        if user_data.phone:
            await update_user_phone(telegram_id, user_data.phone)
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="User details can not been updated!")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "User updated successfully."})


# Retrieve regular users
@users_router.get("/default-users/", response_model=List[UserResponseModel])
async def get_my_users_except_admins():
    users = await get_default_users()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found!")
    return users


# Endpoint to update a user's ban status
@users_router.patch("/ban/")
async def ban_user(request: BanStatusRequest):
    try:
        await update_ban_status(request.user_id, request.is_banned)
    except Exception as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User can not be updated!")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Ban status updated successfully."})


# Get users similar to a given name
@users_router.get("/similarity/{name:str}/{is_executor}", response_model=List[UserResponseModel])
async def get_similar_users(name: str, is_executor: bool = False):
    similar_users = await get_similarity_users(name, is_executor)
    if not similar_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No similar users found")
    return similar_users
