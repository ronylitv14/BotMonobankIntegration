from fastapi import FastAPI, Request, status

from fastapi.responses import JSONResponse
from fastapi.background import BackgroundTasks

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

from database.cruds.transactions import save_monobank_transaction_data


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
async def monobank_webhook_receiver(request: Request, user_id: int, background_tasks: BackgroundTasks):
    payload = await request.json()
    transaction_status = payload.get('status')

    background_tasks.add_task(
        save_monobank_transaction_data,
        transaction_status=transaction_status,
        payload=payload,
        user_id=user_id
    )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Received"})
