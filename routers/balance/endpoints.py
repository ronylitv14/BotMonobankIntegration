from fastapi import status
from fastapi import Security
from config import verify_token
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from routers.balance.schemes import UpdateUserCardsRequest, NewBalanceRequest, UpdateBalanceRequest, BalanceResponse
from database.cruds.balance import update_balance, get_user_balance, create_user_balance, update_user_cards, \
    set_new_balance

balance_router = APIRouter(
    prefix="/balance",
    tags=["balance"],
    dependencies=[Security(verify_token)]
)


# Retrieve a user's balance
@balance_router.get("/{user_id}", response_model=BalanceResponse)
async def get_balance(user_id: int):
    balance = await get_user_balance(user_id)
    if not balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Balance not found.")
    return balance


# Create a user's balance
@balance_router.post("/{user_id}", response_description="Message about successful creation! No data retrieved!")
async def create_balance(user_id: int):
    try:
        await create_user_balance(user_id)
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create balance!")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Balance created successfully."})


# Update a user's cards
@balance_router.patch("/user-cards/", response_description="Message about successful update! No data retrieved!")
async def update_cards_list(update_data: UpdateUserCardsRequest):
    result = await update_user_cards(update_data.user_id, update_data.card)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update user cards.")
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User cards updated successfully."})


# Create a new balance for a user
@balance_router.patch("/new/", response_description="Message about successful update! No data retrieved!")
async def reset_user_balance(request: NewBalanceRequest):
    try:
        await set_new_balance(request.user_id, request.new_amount)
    except IntegrityError as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something wrong with saving! Call Admin!")

    except InvalidRequestError as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Balance account does not exsist!")

    return {"message": "New balance created successfully."}


# Perform balance replenishment or withdrawal
@balance_router.patch("/fund-transfer/", response_description="Message about successful update! No data retrieved!")
async def update_balance_request(balance: UpdateBalanceRequest):
    try:
        await update_balance(balance.user_id, balance.amount, balance.action)
    except InvalidRequestError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Balance account does not exsist!")
    return {"message": "Balance updated successfully."}
