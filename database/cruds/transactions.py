import decimal
from sqlite3 import IntegrityError
from typing import Optional

from sqlalchemy import update, select, or_

from database.database import async_session
from database.models import TransactionType, TransactionStatus, Transaction


async def add_transaction_data(
        invoice_id: str,
        amount: decimal.Decimal,
        transaction_type: TransactionType,
        transaction_status: TransactionStatus,
        sender_id: Optional[int] = None,
        receiver_id: Optional[int] = None,
        task_id: Optional[int] = None,
        commission: Optional[decimal.Decimal] = None
):
    try:
        async with async_session() as session:
            session.add(
                Transaction(
                    invoice_id=invoice_id,
                    amount=amount,
                    transaction_type=transaction_type,
                    transaction_status=transaction_status,
                    task_id=task_id,
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    commission=commission
                )
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        print("Transaction error")
        await session.rollback()
        raise


async def update_transaction_status(
        invoice_id: str,
        new_status: TransactionStatus
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Transaction).where(Transaction.invoice_id == invoice_id).values(transaction_status=new_status)
            )

            await session.commit()

    except IntegrityError:
        await session.rollback()
        raise


async def get_user_transactions(
        user_id: int
):
    try:
        async with async_session() as session:
            res = await session.execute(
                select(Transaction).where(or_(Transaction.receiver_id == user_id, Transaction.sender_id == user_id))
            )

            return res.scalars().all()

    except IntegrityError:
        print("Error")
        return []
