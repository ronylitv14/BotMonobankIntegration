import os
from typing import Annotated

from fastapi import FastAPI, Request, status, Security, Depends, Header
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
import ngrok
import uvicorn
from dotenv import load_dotenv

from routers.chats.endpoints import chats_router
from routers.users.endpoints import users_router
from routers.payments_transactions.endpoints import payments_router, transactions_router
from routers.balance.endpoints import balance_router
from routers.executors.endpoints import executors_router
from routers.group_messages.endpoints import group_router
from routers.tasks.endpoints import task_router
from routers.tickets.endpoints import tickets_router
from routers.withdrawal.endpoints import withdrawal_router

from database.crud import update_transaction_status, update_balance, BalanceAction
from database.models import TransactionStatus

import decimal

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "token"
api_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def verify_token(token:  Annotated[str | None, Header()]):
    if token == API_KEY:
        return True
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No token provided or it is incorrect!")


app = FastAPI(dependencies=[Security(verify_token)])

app.include_router(chats_router)
app.include_router(users_router)
app.include_router(payments_router)
app.include_router(transactions_router)
app.include_router(balance_router)
app.include_router(executors_router)
app.include_router(group_router)
app.include_router(task_router)
app.include_router(tickets_router)
app.include_router(withdrawal_router)


@app.post("/webhook/monobank/{user_id}")
async def webhook_receiver(request: Request, user_id: int):
    payload = await request.json()

    transaction_status = payload.get('status')

    print(transaction_status)
    print(payload)

    if transaction_status == 'success':
        await update_transaction_status(
            invoice_id=payload.get('invoiceId'),
            new_status=TransactionStatus.completed
        )

        amount = decimal.Decimal(payload.get('amount')) / 100

        await update_balance(
            user_id=user_id,
            amount=amount,
            action=BalanceAction.replenishment
        )

    elif transaction_status == 'failure':
        await update_transaction_status(
            invoice_id=payload.get("invoiceId"),
            new_status=TransactionStatus.failed
        )
        print("no success")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Received"})
