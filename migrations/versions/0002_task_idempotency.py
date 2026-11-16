"""Add task submission idempotency keys.

Revision ID: 0002_task_idempotency
Revises: 0001_create_tasks
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_task_idempotency"
down_revision = "0001_create_tasks"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tasks", sa.Column("idempotency_key", sa.String(length=128), nullable=True))
    op.add_column("tasks", sa.Column("request_hash", sa.String(length=64), nullable=True))
    op.create_index("ix_tasks_idempotency_key", "tasks", ["idempotency_key"], unique=True)


def downgrade():
    op.drop_index("ix_tasks_idempotency_key", table_name="tasks")
    op.drop_column("tasks", "request_hash")
    op.drop_column("tasks", "idempotency_key")
