from fastapi import FastAPI, Request, status

from fastapi.responses import JSONResponse

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
from routers.warnings.endpoints import warnings_router
from routers.reviews.endpoints import reviews_router

from database.cruds.transactions import update_transaction_status
from database.cruds.balance import update_balance, BalanceAction
from database.models import TransactionStatus

import decimal

load_dotenv()

app = FastAPI()

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
app.include_router(warnings_router)
app.include_router(reviews_router)


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
