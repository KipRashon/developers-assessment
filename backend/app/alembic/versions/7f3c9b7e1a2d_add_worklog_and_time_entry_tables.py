"""Add worklog and time entry tables

Revision ID: 7f3c9b7e1a2d
Revises: 1a31ce608336
Create Date: 2026-03-18 11:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7f3c9b7e1a2d"
down_revision = "1a31ce608336"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "worklog",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("task_name", sa.String(length=255), nullable=False),
        sa.Column("freelancer_id", sa.UUID(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("remittance_status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["freelancer_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_worklog_freelancer_id", "worklog", ["freelancer_id"], unique=False
    )
    op.create_index(
        "ix_worklog_period_start", "worklog", ["period_start"], unique=False
    )
    op.create_index("ix_worklog_period_end", "worklog", ["period_end"], unique=False)
    op.create_index(
        "ix_worklog_remittance_status", "worklog", ["remittance_status"], unique=False
    )

    op.create_table(
        "timeentry",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("worklog_id", sa.UUID(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("hours", sa.Float(), nullable=False),
        sa.Column("hourly_rate", sa.Float(), nullable=False),
        sa.Column("is_excluded", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["worklog_id"], ["worklog.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_timeentry_worklog_id", "timeentry", ["worklog_id"], unique=False
    )
    op.create_index(
        "ix_timeentry_started_at", "timeentry", ["started_at"], unique=False
    )
    op.create_index("ix_timeentry_ended_at", "timeentry", ["ended_at"], unique=False)
    op.create_index(
        "ix_timeentry_is_excluded", "timeentry", ["is_excluded"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_timeentry_is_excluded", table_name="timeentry")
    op.drop_index("ix_timeentry_ended_at", table_name="timeentry")
    op.drop_index("ix_timeentry_started_at", table_name="timeentry")
    op.drop_index("ix_timeentry_worklog_id", table_name="timeentry")
    op.drop_table("timeentry")

    op.drop_index("ix_worklog_remittance_status", table_name="worklog")
    op.drop_index("ix_worklog_period_end", table_name="worklog")
    op.drop_index("ix_worklog_period_start", table_name="worklog")
    op.drop_index("ix_worklog_freelancer_id", table_name="worklog")
    op.drop_table("worklog")
