"""Create db data

Revision ID: 8b73cc297802
Revises: 
Create Date: 2024-01-20 15:20:46.696142

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8b73cc297802'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
                    sa.Column('telegram_id', sa.BIGINT(), nullable=False),
                    sa.Column('telegram_username', sa.String(), nullable=False),
                    sa.Column('username', sa.String(), nullable=False),
                    sa.Column('chat_id', sa.BIGINT(), nullable=False),
                    sa.Column('user_status', sa.Enum('default', 'admin', 'superuser', name='userstatus'),
                              nullable=True),
                    sa.Column('is_banned', sa.Boolean(), nullable=False),
                    sa.Column('warning_count', sa.Integer(), nullable=True),
                    sa.Column('salt', sa.String(), nullable=False),
                    sa.Column('hashed_password', sa.String(), nullable=True),
                    sa.Column('phone', sa.String(), nullable=False),
                    sa.Column('email', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('telegram_id', 'phone'),
                    sa.UniqueConstraint('phone')
                    )
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)
    op.create_table('balance',
                    sa.Column('user_id', sa.BIGINT(), nullable=False),
                    sa.Column('user_cards', postgresql.ARRAY(sa.String()), nullable=True),
                    sa.Column('balance_money', sa.DECIMAL(precision=10, scale=2), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('user_id'),
                    sa.UniqueConstraint('user_id')
                    )
    op.create_table('executors',
                    sa.Column('executor_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.BIGINT(), nullable=True),
                    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('profile_state', sa.Enum('created', 'accepted', 'rejected', name='profilestatus'),
                              nullable=False),
                    sa.Column('work_examples', postgresql.ARRAY(sa.String()), nullable=False),
                    sa.Column('work_files_type', postgresql.ARRAY(sa.Enum('photo', 'document', name='filetype')),
                              nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('executor_id'),
                    sa.UniqueConstraint('executor_id'),
                    sa.UniqueConstraint('user_id')
                    )
    op.create_table('reset_tokens',
                    sa.Column('user_id', sa.BIGINT(), nullable=False),
                    sa.Column('reset_password_token', sa.String(), nullable=False),
                    sa.Column('expire_date', sa.TIMESTAMP(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
                    sa.Column('is_used', sa.Boolean(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
                    sa.PrimaryKeyConstraint('user_id')
                    )
    op.create_table('user_tickets',
                    sa.Column('ticket_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.BIGINT(), nullable=True),
                    sa.Column('subject', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=False),
                    sa.Column('status', sa.Enum('open', 'in_progress', 'closed', name='ticketstatus'), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
                    sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
                    sa.Column('response', sa.String(), nullable=True),
                    sa.Column('responded_by', sa.BIGINT(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
                    sa.PrimaryKeyConstraint('ticket_id')
                    )
    op.create_table('warnings',
                    sa.Column('warning_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.BIGINT(), nullable=True),
                    sa.Column('reason', sa.String(), nullable=False),
                    sa.Column('issued_by', sa.BIGINT(), nullable=True),
                    sa.Column('issued_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
                    sa.PrimaryKeyConstraint('warning_id')
                    )
    op.create_table('withdrawal_requests',
                    sa.Column('request_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.BIGINT(), nullable=False),
                    sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
                    sa.Column('commission', sa.DECIMAL(precision=10, scale=2), nullable=False),
                    sa.Column('request_date', sa.TIMESTAMP(), nullable=False),
                    sa.Column('status', sa.Enum('pending', 'processed', 'rejected', name='withdrawalstatus'),
                              nullable=False),
                    sa.Column('payment_method', sa.String(), nullable=False),
                    sa.Column('payment_details', sa.String(), nullable=True),
                    sa.Column('processed_date', sa.TIMESTAMP(), nullable=True),
                    sa.Column('admin_id', sa.Integer(), nullable=True),
                    sa.Column('notes', sa.String(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('request_id')
                    )
    op.create_table('tasks',
                    sa.Column('task_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('executor_id', sa.BIGINT(), nullable=True),
                    sa.Column('client_id', sa.BIGINT(), nullable=True),
                    sa.Column('status', sa.Enum('active', 'executing', 'done', name='taskstatus'), nullable=False),
                    sa.Column('price', sa.String(), nullable=False),
                    sa.Column('date_added', sa.TIMESTAMP(), nullable=True),
                    sa.Column('deadline', sa.DATE(), nullable=True),
                    sa.Column('proposed_by', sa.Enum('executor', 'client', 'public', name='propositionby'),
                              nullable=False),
                    sa.Column('files', postgresql.ARRAY(sa.String()), nullable=True),
                    sa.Column('files_type', postgresql.ARRAY(sa.Enum('photo', 'document', name='filetype')),
                              nullable=True),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('subjects', postgresql.ARRAY(sa.String()), nullable=False),
                    sa.Column('work_type', postgresql.ARRAY(sa.String()), nullable=False),
                    sa.ForeignKeyConstraint(['client_id'], ['users.telegram_id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['executor_id'], ['executors.user_id'], ),
                    sa.PrimaryKeyConstraint('task_id'),
                    sa.UniqueConstraint('task_id')
                    )
    op.create_table('chats',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('chat_id', sa.BIGINT(), nullable=False),
                    sa.Column('supergroup_id', sa.BIGINT(), nullable=True),
                    sa.Column('task_id', sa.Integer(), nullable=True),
                    sa.Column('executor_id', sa.BIGINT(), nullable=False),
                    sa.Column('client_id', sa.BIGINT(), nullable=False),
                    sa.Column('group_name', sa.String(), nullable=False),
                    sa.Column('chat_type',
                              sa.Enum('SENDER', 'PRIVATE', 'GROUP', 'SUPERGROUP', 'CHANNEL', name='chattype'),
                              nullable=False),
                    sa.Column('chat_admin', sa.String(), nullable=False),
                    sa.Column('date_created', sa.TIMESTAMP(), nullable=True),
                    sa.Column('participants_count', sa.Integer(), nullable=True),
                    sa.Column('invite_link', sa.String(), nullable=True),
                    sa.Column('is_payed', sa.Boolean(), nullable=False, server_default=sa.false()),
                    sa.Column('payment_date', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['client_id'], ['users.telegram_id'], ),
                    sa.ForeignKeyConstraint(['executor_id'], ['executors.user_id'], ),
                    sa.ForeignKeyConstraint(['task_id'], ['tasks.task_id'], ),
                    sa.PrimaryKeyConstraint('id', 'chat_id'),
                    sa.UniqueConstraint('chat_id'),
                    sa.UniqueConstraint('chat_id', 'task_id', 'executor_id', 'client_id',
                                        name='unique_combination_chat'),
                    sa.UniqueConstraint('id'),
                    sa.UniqueConstraint('supergroup_id')
                    )
    op.create_table('group_messages',
                    sa.Column('group_message_id', sa.Integer(), nullable=False),
                    sa.Column('task_id', sa.Integer(), nullable=False),
                    sa.Column('message_text', sa.String(), nullable=False),
                    sa.Column('has_files', sa.Boolean(), nullable=False),
                    sa.Column('date_added', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['task_id'], ['tasks.task_id'], ),
                    sa.PrimaryKeyConstraint('group_message_id'),
                    sa.UniqueConstraint('group_message_id')
                    )
    op.create_table('transactions',
                    sa.Column('transaction_id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('invoice_id', sa.String(), nullable=False),
                    sa.Column('sender_id', sa.BIGINT(), nullable=True),
                    sa.Column('receiver_id', sa.BIGINT(), nullable=True),
                    sa.Column('task_id', sa.Integer(), nullable=True),
                    sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=True),
                    sa.Column('commission', sa.DECIMAL(precision=10, scale=2), nullable=True),
                    sa.Column('transaction_type', sa.Enum('debit', 'transfer', 'withdrawal', name='transactiontype'),
                              nullable=False),
                    sa.Column('transaction_status', sa.Enum('pending', 'completed', 'failed', name='transactionstatus'),
                              nullable=False),
                    sa.Column('transaction_date', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['receiver_id'], ['users.telegram_id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['sender_id'], ['users.telegram_id'], ondelete='SET NULL'),
                    sa.ForeignKeyConstraint(['task_id'], ['tasks.task_id'], ),
                    sa.PrimaryKeyConstraint('transaction_id', 'invoice_id')
                    )
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_table('group_messages')
    op.drop_table('chats')
    op.drop_table('tasks')
    op.drop_table('withdrawal_requests')
    op.drop_table('warnings')
    op.drop_table('user_tickets')
    op.drop_table('reset_tokens')
    op.drop_table('executors')
    op.drop_table('balance')
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
