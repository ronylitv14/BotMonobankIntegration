import decimal
from datetime import datetime
from aiogram.enums import ChatType

from typing import List, Optional

from sqlalchemy import false, true, func
from sqlalchemy.orm import validates, Mapped
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import (
    Column,
    String,
    BIGINT,
    Enum,
    Integer,
    Boolean,
    TIMESTAMP,
    DATE,
    DECIMAL,
    ForeignKey,
    UniqueConstraint,
    LargeBinary
)
import enum

from utils.hashing_passwords import create_user_password, check_user_password, create_reset_token

Base = declarative_base()


class TaskStatus(enum.StrEnum):
    active: str = "active"
    executing: str = "executing"
    done: str = "done"


class TransactionStatus(enum.StrEnum):
    pending: str = 'Pending'
    completed: str = 'Completed'
    failed: str = 'Failed'


class TransactionType(enum.StrEnum):
    debit: str = 'Debit'
    transfer: str = 'Transfer'
    withdrawal: str = "Withdrawal"


class ProfileStatus(enum.StrEnum):
    created: str = "created"
    accepted: str = "accepted"
    rejected: str = "rejected"


class PropositionBy(enum.StrEnum):
    executor: str = "executor"
    client: str = "client"
    public: str = "public"


class FileType(enum.StrEnum):
    photo: str = "photo"
    document: str = "document"


class UserStatus(enum.StrEnum):
    default: str = "default_user"
    admin: str = "admin"
    superuser: str = "superuser"


class WithdrawalStatus(enum.StrEnum):
    pending: str = "pending"
    processed: str = "processed"
    rejected: str = "rejected"


class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BIGINT, primary_key=True, unique=True, index=True)
    telegram_username = Column(String, nullable=False)
    username = Column(String, nullable=False)
    chat_id = Column(BIGINT, nullable=False)
    user_status = Column(Enum(UserStatus), default=UserStatus.default)
    is_banned = Column(Boolean, nullable=False, default=False)
    warning_count = Column(Integer, default=0)
    salt = Column(String, nullable=False)
    hashed_password = Column(String)
    phone = Column(String, primary_key=True, unique=True)
    email = Column(String, nullable=True)
    date_added = Column(TIMESTAMP, nullable=False, server_default=func.now())

    def __init__(self, tg_id: int, username: str, phone: str, password: str, chat_id: int, tg_username: str,
                 user_status: UserStatus = UserStatus.default, email: str = "",
                 date_added: datetime = datetime.utcnow()):
        self.telegram_id = tg_id
        self.telegram_username = tg_username
        self.username = username
        self.hashed_password, self.salt = self.hash_password(password)
        self.phone = phone
        self.email = email
        self.chat_id = chat_id
        self.user_status = user_status
        self.date_added = date_added

    def __str__(self):
        return f"Ім'я в системі: {self.username}, статус: {self.user_status.value}"

    @hybrid_method
    def hash_password(self, password):
        return create_user_password(password)

    @hybrid_method
    def check_password(self, password: str):
        return check_user_password(
            password_attempt=password,
            stored_hash=self.hashed_password,
            stored_salt=self.salt
        )


class ResetToken(Base):
    __tablename__ = "reset_tokens"

    user_id = Column(BIGINT, ForeignKey("users.telegram_id"), primary_key=True)
    reset_password_token = Column(String, nullable=False)
    expire_date = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_used = Column(Boolean, default=False)

    def __init__(self, user_id, expire_date, is_used):
        self.user_id = user_id
        self.reset_password_token = self.create_reset_token()
        self.expire_date = expire_date
        self.is_used = is_used

    @hybrid_method
    def create_reset_token(self):
        pass


class Executor(Base):
    __tablename__ = "executors"

    executor_id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey("users.telegram_id", ondelete="CASCADE"), unique=True)
    tags = Column(ARRAY(String), nullable=True)
    description = Column(String, nullable=True)
    profile_state = Column(Enum(ProfileStatus), nullable=False, default=ProfileStatus.created)
    work_examples = Column(ARRAY(String), nullable=False)
    work_files_type = Column(ARRAY(Enum(FileType)), nullable=False)

    def __init__(self, user_id: int, tags: List[str], work_examples: List[str], work_files_type: List[FileType],
                 description: str = "", ):
        self.user_id = user_id
        self.tags = tags
        self.description = description
        self.work_examples = work_examples
        self.work_files_type = work_files_type

    def __str__(self):
        return f"Номер заявки: {self.executor_id}"


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, unique=True, autoincrement=True, )
    executor_id = Column(BIGINT, ForeignKey("executors.user_id"), nullable=True)
    client_id = Column(BIGINT, ForeignKey("users.telegram_id", ondelete="SET NULL"))
    status = Column(Enum(TaskStatus), nullable=False)
    price = Column(String, nullable=False)
    date_added = Column(TIMESTAMP, default=datetime.utcnow)
    deadline = Column(DATE)
    proposed_by = Column(Enum(PropositionBy), nullable=False, default=PropositionBy.public)
    files = Column(ARRAY(String), nullable=True)
    files_type = Column(ARRAY(Enum(FileType)), nullable=True)
    description = Column(String, nullable=True)
    subjects = Column(ARRAY(String), nullable=False)
    work_type = Column(ARRAY(String), nullable=False)

    def __init__(self,
                 client_id: int,
                 status: TaskStatus,
                 price: str,
                 deadline: datetime.date,
                 subjects: List[str],
                 work_type: List[str],
                 description: str = "",
                 proposed_by=PropositionBy.public,
                 executor_id: int = None,
                 files: List[str] = None,
                 files_type: List[FileType] = None,
                 ):
        self.client_id = client_id
        self.status = status
        self.price = price
        self.deadline = deadline
        self.files = files
        self.files_type = files_type
        self.subjects = subjects
        self.description = description
        self.work_type = work_type
        self.proposed_by = proposed_by
        self.executor_id = executor_id

    def __repr__(self):
        type_str = "#" + " #".join([t.replace(" ", "_") for t in self.work_type])
        subj_str = "#" + " #".join([t.replace(" ", "_") for t in self.subjects])

        return f"Номер замовлення: {self.task_id}, Вид роботи: {type_str}, Предмети: {subj_str}"


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    chat_id = Column(BIGINT, unique=False, primary_key=True)
    supergroup_id = Column(BIGINT, unique=False, nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.task_id"))
    executor_id = Column(BIGINT, ForeignKey("executors.user_id"), nullable=False)
    client_id = Column(BIGINT, ForeignKey("users.telegram_id"), nullable=False)
    active = Column(Boolean, server_default=true(), default=true(), nullable=False)
    group_name = Column(String, nullable=False)
    chat_type = Column(Enum(ChatType), nullable=False, default=ChatType.GROUP)
    chat_admin = Column(String, nullable=False)
    date_created = Column(TIMESTAMP, default=datetime.utcnow)
    participants_count = Column(Integer, nullable=True)
    invite_link = Column(String, nullable=True)
    is_payed = Column(Boolean, server_default=false(), nullable=False)
    in_use = Column(Boolean, server_default=false(), nullable=False)
    payment_date = Column(TIMESTAMP, nullable=True)

    __table_args__ = (
        UniqueConstraint('chat_id', 'task_id', 'executor_id', 'client_id', name='unique_combination_chat'),
    )

    def __init__(self, chat_id: int, task_id: int, group_name: str, participants_count: int,
                 invite_link: str, executor_id: int, client_id: int, chat_admin: str,
                 supergroup_id: Optional[int] = None, chat_type: ChatType = ChatType.GROUP,
                 is_payed: bool = False, active: bool = True, in_use: bool = False):
        self.chat_id = chat_id
        self.task_id = task_id
        self.group_name = group_name
        self.participants_count = participants_count
        self.invite_link = invite_link
        self.executor_id = executor_id
        self.client_id = client_id
        self.chat_admin = chat_admin
        self.chat_type = chat_type
        self.is_payed = is_payed
        self.active = active
        self.supergroup_id = supergroup_id
        self.in_use = in_use

    def __repr__(self):
        return f"<Chat {self.group_name} (ID: {self.chat_id})>"


class GroupMessage(Base):
    __tablename__ = "group_messages"
    __table_args__ = {'extend_existing': True}

    group_message_id = Column(Integer, primary_key=True, unique=True)
    task_id = Column(Integer, ForeignKey("tasks.task_id"), nullable=False)
    message_text = Column(String, nullable=False)
    has_files = Column(Boolean, nullable=False, default=False)
    date_added = Column(TIMESTAMP, default=datetime.utcnow)

    def __init__(self, group_message_id: int, task_id: int, message_text: str, has_files: bool = False):
        self.group_message_id = group_message_id
        self.has_files = has_files
        self.task_id = task_id
        self.message_text = message_text


class Balance(Base):
    __tablename__ = "balance"
    user_id = Column(BIGINT, ForeignKey("users.telegram_id", ondelete="CASCADE"), primary_key=True, unique=True)
    user_cards = Column(ARRAY(LargeBinary), nullable=True)
    balance_money = Column(DECIMAL(10, 2), nullable=False, default=0.00)

    def __init__(self, user_id: int, user_cards: List = None, balance_money: float = 0.00):
        self.user_id = user_id
        self.user_cards = user_cards
        self.balance_money = balance_money


class Transaction(Base):
    __tablename__ = 'transactions'

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(String, primary_key=True)
    sender_id = Column(BIGINT, ForeignKey('users.telegram_id', ondelete="SET NULL"), nullable=True)
    receiver_id = Column(BIGINT, ForeignKey('users.telegram_id', ondelete="SET NULL"), nullable=True)
    task_id = Column(Integer, ForeignKey('tasks.task_id'), nullable=True)
    amount = Column(DECIMAL(10, 2))
    commission = Column(DECIMAL(precision=10, scale=2), nullable=True, default=decimal.Decimal(0.00))
    transaction_type = Column(Enum(TransactionType), nullable=False)
    transaction_status = Column(Enum(TransactionStatus), nullable=False)
    transaction_date = Column(TIMESTAMP, default=datetime.utcnow)

    def __init__(
            self,
            invoice_id: str,
            amount: decimal.Decimal,
            transaction_type: TransactionType,
            transaction_status: TransactionStatus,
            commission: Optional[decimal.Decimal] = None,
            sender_id: Optional[int] = None,
            receiver_id: Optional[int] = None,
            task_id: Optional[int] = None
    ):
        self.transaction_type = transaction_type
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.task_id = task_id
        self.transaction_status = transaction_status
        self.invoice_id = invoice_id
        self.amount = amount
        self.commission = commission


class WithdrawalRequest(Base):
    __tablename__ = 'withdrawal_requests'

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey('users.telegram_id', ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    commission = Column(DECIMAL(10, 2), nullable=False)
    request_date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    status = Column(Enum(WithdrawalStatus), default=WithdrawalStatus.pending, nullable=False)
    payment_method = Column(String, nullable=False)
    payment_details = Column(String, nullable=True)
    processed_date = Column(TIMESTAMP, nullable=True)
    admin_id = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)

    def __init__(
            self,
            user_id: int,
            amount: decimal.Decimal,
            commission: decimal.Decimal,
            payment_method: str,
            status: WithdrawalStatus,
            payment_details: str = None,
            admin_id: int = None,
            notes: str = None
    ):
        self.user_id = user_id
        self.commission = commission
        self.amount = amount
        self.status = status
        self.payment_method = payment_method
        self.payment_details = payment_details
        self.admin_id = admin_id
        self.notes = notes

    def __str__(self):
        return f"Номер заявки №{self.request_id}, сума - {self.amount}"


class Warning(Base):
    __tablename__ = "warnings"

    warning_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey("users.telegram_id"))
    reason = Column(String, nullable=False)
    issued_by = Column(BIGINT)
    issued_at = Column(TIMESTAMP, default=datetime.utcnow)

    def __init__(
            self,
            user_id,
            reason,
            issued_by
    ):
        self.user_id = user_id
        self.reason = reason
        self.issued_by = issued_by

    def __repr__(self):
        return f"<Warning {self.warning_id} issued to user {self.user_id}>"


class TicketStatus(enum.StrEnum):
    open = "Open"
    in_progress = "In Progress"
    closed = "Closed"


class UserTicket(Base):
    __tablename__ = "user_tickets"

    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey("users.telegram_id"))
    subject = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.open)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, onupdate=datetime.utcnow)
    response = Column(String)  # Admin's response to the ticket
    responded_by = Column(BIGINT)  # Admin's ID or username

    def __init__(
            self,
            user_id: int,
            subject: str,
            description: str
    ):
        self.user_id = user_id
        self.subject = subject
        self.description = description

    def __repr__(self):
        return f"Тікет номер №{self.ticket_id} - категорія: {self.subject}"


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    reviewer_id = Column(BIGINT, ForeignKey("users.telegram_id"), nullable=False)
    reviewed_id = Column(BIGINT, ForeignKey("users.telegram_id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.task_id"), nullable=False)
    rating = Column(Integer, nullable=False)
    positive_sights = Column(ARRAY(String), nullable=True)
    negative_sights = Column(ARRAY(String), nullable=True)
    comment = Column(String, nullable=True)
    review_date = Column(TIMESTAMP, default=datetime.utcnow)

    def __init__(self, reviewer_id: int, reviewed_id: int, task_id: int, rating: int, comment: str = None,
                 positive_sights: List[str] = None, negative_sights: List[str] = None):
        self.reviewer_id = reviewer_id
        self.reviewed_id = reviewed_id
        self.task_id = task_id
        self.rating = rating
        self.comment = comment
        self.positive_sights = positive_sights
        self.negative_sights = negative_sights

    def __repr__(self):
        return f"<Review {self.review_id} by {self.reviewer_id} for {self.reviewed_id}>"
