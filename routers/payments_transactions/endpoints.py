from typing import List, Optional

from fastapi import HTTPException, status, Query
from fastapi import Security
from config import verify_token
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from database.cruds.transactions import add_transaction_data, update_transaction_status, get_user_transactions, \
    get_transaction_data
from database.cruds.payments import check_successful_payment, accept_done_offer, create_money_transfer
from database.models import TransactionType, TransactionStatus

from routers.payments_transactions.schemes import TransactionDataRequest, UpdateTransactionStatusRequest, \
    AcceptDoneOfferRequest, CreateTransfer, TransactionResponse, SuccessPayment

from sqlalchemy.exc import IntegrityError

payments_router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    dependencies=[Security(verify_token)]

)

transactions_router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Security(verify_token)]

)


# Add transaction data
@transactions_router.post("/")
async def add_transaction(transaction_data: TransactionDataRequest):
    try:
        await add_transaction_data(**transaction_data.model_dump())
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error with creating transaction!")
    return JSONResponse(content={"message": "Transaction data added successfully."},
                        status_code=status.HTTP_201_CREATED)


# Update transaction status
@transactions_router.patch("/")
async def update_transaction(transaction_data: UpdateTransactionStatusRequest):
    try:
        await update_transaction_status(transaction_data.invoice_id, transaction_data.new_status)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error with updating transaction!")
    return JSONResponse(content={"message": "Transaction status updated successfully."}, status_code=status.HTTP_200_OK)


# Get transactions for a user
@transactions_router.get("/{user_id}", response_model=List[TransactionResponse])
async def get_transactions(user_id: int):
    transactions = await get_user_transactions(user_id)
    if not transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No transactions found!")
    return transactions


@transactions_router.get("/", response_model=List[TransactionResponse])
async def get_transaction_transfer(
        sender_id: int,
        receiver_id: int,
        task_id: Optional[int] = None,
        transaction_type: Optional[TransactionType] = None,
        transaction_status: Optional[TransactionStatus] = None
):
    transactions = await get_transaction_data(
        sender_id=sender_id,
        receiver_id=receiver_id,
        task_id=task_id,
        transaction_type=transaction_type,
        transaction_status=transaction_status
    )

    if not transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No transactions found!")

    return transactions


# Create transaction data
@payments_router.post("/transfer", response_model=TransactionResponse)
async def perform_money_transfer(transfer_data: CreateTransfer):
    try:
        transaction = await create_money_transfer(**transfer_data.model_dump())
    except ValueError as err:
        print(err)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect balance amount of sender!")
    except IntegrityError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Unprocessable data for transfer!")

    return transaction


# Check for successful payment
@payments_router.get("/{task_id:int}/{receiver_id:int}/{sender_id:int}", response_model=SuccessPayment)
async def check_payment(task_id: int, receiver_id: int, sender_id: int):
    success = await check_successful_payment(task_id, receiver_id, sender_id)
    return JSONResponse(content={"status": success}, status_code=status.HTTP_200_OK)


# Accept a done offer
@payments_router.post("/accept-offer", response_description="Only message about success!")
async def accept_offer(payment_data: AcceptDoneOfferRequest):
    try:
        await accept_done_offer(**payment_data.model_dump())
        return {"message": "Offer accepted and task marked as done."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
