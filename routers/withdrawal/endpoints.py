import datetime
from typing import Optional, List
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from routers.withdrawal.schemes import WithdrawalRequestModel, UpdateWithdrawalRequestModel, WithdrawalResponse
from database.crud import create_withdrawal_request, get_all_withdrawal_requests, update_withdrawal_request
from database.models import WithdrawalStatus
from sqlalchemy.exc import IntegrityError

withdrawal_router = APIRouter(
    prefix="/withdrawals",
    tags=["withdrawals"]
)


@withdrawal_router.post("/")
async def create_withdrawal(request: WithdrawalRequestModel):
    try:
        await create_withdrawal_request(**request.model_dump())

    except IntegrityError:
        raise HTTPException(status_code=500, detail="Error saving data!")
    return JSONResponse(status_code=201, content={"message": "Withdrawal request created successfully."})


# Get all withdrawal requests
@withdrawal_router.get("/{status}", response_model=List[WithdrawalResponse])
async def get_all_withdrawals(status: WithdrawalStatus):
    requests = await get_all_withdrawal_requests(status)
    return requests


# Update a withdrawal request
@withdrawal_router.patch("/")
async def update_withdrawal(request: UpdateWithdrawalRequestModel):
    try:
        await update_withdrawal_request(**request.model_dump(), processed_time=datetime.datetime.utcnow())
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Error with updating data!")
    return JSONResponse(status_code=200, content={"message": "Withdrawal request updated successfully."})
