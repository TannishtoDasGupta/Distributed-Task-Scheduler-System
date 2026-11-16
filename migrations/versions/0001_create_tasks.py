"""Create the tasks table.

Revision ID: 0001_create_tasks
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_create_tasks"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("payload", sa.Text(), nullable=True),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("retries", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("task_id", name="uq_tasks_task_id"),
    )
    op.create_index("ix_tasks_id", "tasks", ["id"])
    op.create_index("ix_tasks_task_id", "tasks", ["task_id"])

def downgrade():
    op.drop_index("ix_tasks_task_id", table_name="tasks")
    op.drop_index("ix_tasks_id", table_name="tasks")
    op.drop_table("tasks")
