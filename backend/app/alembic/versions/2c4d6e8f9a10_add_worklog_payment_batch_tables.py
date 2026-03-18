"""Add payment batch workflow tables

Revision ID: 2c4d6e8f9a10
Revises: 7f3c9b7e1a2d
Create Date: 2026-03-18 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2c4d6e8f9a10"
down_revision = "7f3c9b7e1a2d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payment_batch",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=True),
        sa.Column("confirmed_by_id", sa.UUID(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.String(length=255), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_amount_snapshot", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["confirmed_by_id"], ["user.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_payment_batch_period_start", "payment_batch", ["period_start"], unique=False
    )
    op.create_index(
        "ix_payment_batch_period_end", "payment_batch", ["period_end"], unique=False
    )
    op.create_index(
        "ix_payment_batch_status", "payment_batch", ["status"], unique=False
    )
    op.create_index(
        "ix_payment_batch_created_by_id",
        "payment_batch",
        ["created_by_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_batch_confirmed_by_id",
        "payment_batch",
        ["confirmed_by_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_batch_idempotency_key",
        "payment_batch",
        ["idempotency_key"],
        unique=False,
    )
    op.create_index(
        "ix_payment_batch_created_at", "payment_batch", ["created_at"], unique=False
    )

    op.create_table(
        "remittance",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("payment_batch_id", sa.UUID(), nullable=False),
        sa.Column("freelancer_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("external_reference", sa.String(length=128), nullable=True),
        sa.Column("failure_reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["payment_batch_id"], ["payment_batch.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["freelancer_id"], ["user.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_batch_id", "freelancer_id"),
    )
    op.create_index(
        "ix_remittance_payment_batch_id",
        "remittance",
        ["payment_batch_id"],
        unique=False,
    )
    op.create_index(
        "ix_remittance_freelancer_id", "remittance", ["freelancer_id"], unique=False
    )
    op.create_index("ix_remittance_status", "remittance", ["status"], unique=False)
    op.create_index(
        "ix_remittance_created_at", "remittance", ["created_at"], unique=False
    )

    op.create_table(
        "payment_batch_worklog",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("payment_batch_id", sa.UUID(), nullable=False),
        sa.Column("worklog_id", sa.UUID(), nullable=False),
        sa.Column("freelancer_id", sa.UUID(), nullable=False),
        sa.Column("inclusion_status", sa.String(length=32), nullable=False),
        sa.Column("exclusion_reason", sa.String(length=255), nullable=True),
        sa.Column("excluded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("excluded_by_id", sa.UUID(), nullable=True),
        sa.Column("amount_snapshot", sa.Float(), nullable=False),
        sa.Column("total_minutes_snapshot", sa.Integer(), nullable=False),
        sa.Column("remittance_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "total_minutes_snapshot >= 0",
            name="ck_payment_batch_worklog_total_minutes_non_negative",
        ),
        sa.ForeignKeyConstraint(["excluded_by_id"], ["user.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["freelancer_id"], ["user.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["payment_batch_id"], ["payment_batch.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["remittance_id"], ["remittance.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["worklog_id"], ["worklog.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_batch_id", "worklog_id"),
    )
    op.create_index(
        "ix_payment_batch_worklog_payment_batch_id",
        "payment_batch_worklog",
        ["payment_batch_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_batch_worklog_worklog_id",
        "payment_batch_worklog",
        ["worklog_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_batch_worklog_freelancer_id",
        "payment_batch_worklog",
        ["freelancer_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_batch_worklog_inclusion_status",
        "payment_batch_worklog",
        ["inclusion_status"],
        unique=False,
    )
    op.create_index(
        "ix_payment_batch_worklog_excluded_by_id",
        "payment_batch_worklog",
        ["excluded_by_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_batch_worklog_remittance_id",
        "payment_batch_worklog",
        ["remittance_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_batch_worklog_created_at",
        "payment_batch_worklog",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_payment_batch_worklog_created_at", table_name="payment_batch_worklog"
    )
    op.drop_index(
        "ix_payment_batch_worklog_remittance_id", table_name="payment_batch_worklog"
    )
    op.drop_index(
        "ix_payment_batch_worklog_excluded_by_id", table_name="payment_batch_worklog"
    )
    op.drop_index(
        "ix_payment_batch_worklog_inclusion_status", table_name="payment_batch_worklog"
    )
    op.drop_index(
        "ix_payment_batch_worklog_freelancer_id", table_name="payment_batch_worklog"
    )
    op.drop_index(
        "ix_payment_batch_worklog_worklog_id", table_name="payment_batch_worklog"
    )
    op.drop_index(
        "ix_payment_batch_worklog_payment_batch_id", table_name="payment_batch_worklog"
    )
    op.drop_table("payment_batch_worklog")

    op.drop_index("ix_remittance_created_at", table_name="remittance")
    op.drop_index("ix_remittance_status", table_name="remittance")
    op.drop_index("ix_remittance_freelancer_id", table_name="remittance")
    op.drop_index("ix_remittance_payment_batch_id", table_name="remittance")
    op.drop_table("remittance")

    op.drop_index("ix_payment_batch_created_at", table_name="payment_batch")
    op.drop_index("ix_payment_batch_idempotency_key", table_name="payment_batch")
    op.drop_index("ix_payment_batch_confirmed_by_id", table_name="payment_batch")
    op.drop_index("ix_payment_batch_created_by_id", table_name="payment_batch")
    op.drop_index("ix_payment_batch_status", table_name="payment_batch")
    op.drop_index("ix_payment_batch_period_end", table_name="payment_batch")
    op.drop_index("ix_payment_batch_period_start", table_name="payment_batch")
    op.drop_table("payment_batch")
