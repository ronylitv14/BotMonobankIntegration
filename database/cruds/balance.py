import decimal
import enum

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.dialects.postgresql import array, insert

from database.database import async_session
from database.models import Balance
from utils.card_tokenization import encrypt_card_number, decrypt_card_number


class BalanceAction(enum.StrEnum):
    replenishment: str = "replenishment"
    withdrawal: str = "withdrawal"


async def update_balance(
        user_id: int,
        amount: decimal.Decimal,
        action: BalanceAction
):
    try:
        async with async_session() as session:
            balance = await session.execute(
                select(Balance).where(Balance.user_id == user_id)
            )

            balance = balance.scalars().first()

            if not balance:
                raise InvalidRequestError

            if action == BalanceAction.replenishment:
                balance.balance_money += amount
            elif action == BalanceAction.withdrawal:
                balance.balance_money -= amount

            await session.commit()

    except IntegrityError:
        await session.rollback()


async def get_user_balance(user_id: int) -> Balance:
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Balance).where(
                    Balance.user_id == user_id
                )
            )

            balance_data = result.scalars().first()

            balance_data.user_cards = [decrypt_card_number(card) for card in balance_data.user_cards]

            return balance_data
    except IntegrityError:
        await session.rollback()


async def create_user_balance(user_id: int):
    try:
        async with async_session() as session:
            session.add(
                Balance(
                    user_id=user_id,
                    balance_money=0.00,
                    user_cards=[]
                )
            )
            await session.commit()
    except IntegrityError:
        print("Error with adding user")
        raise


async def update_user_cards(user_id: int, card: str):
    try:
        async with async_session() as session:

            card = encrypt_card_number(card)

            stmt = insert(Balance).values(user_id=user_id, user_cards=[card])

            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=['user_id'],
                set_={
                    'user_cards': Balance.user_cards.op('||')(array([card], type_="BLOB"))
                },
                where=(~Balance.user_cards.contains(array([card], type_="BLOB")))
            )

            await session.execute(do_update_stmt)
            await session.commit()

            return True
    except IntegrityError:
        await session.rollback()

    return False


async def set_new_balance(
        user_id: int,
        new_amount: decimal.Decimal
):
    try:
        async with async_session() as session:

            balance = await session.execute(select(Balance).where(Balance.user_id == user_id))

            if not balance.scalars().first():
                raise InvalidRequestError

            await session.execute(
                update(Balance).where(Balance.user_id == user_id).values(balance_money=new_amount)
            )

            await session.commit()

    except IntegrityError:
        print("Unsuccessfully updated balance")
        raise
