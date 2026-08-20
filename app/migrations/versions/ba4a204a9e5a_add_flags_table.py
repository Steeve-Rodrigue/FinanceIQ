"""add flags table

Revision ID: ba4a204a9e5a
Revises: c6a8c264126e
Create Date: 2026-08-20 08:00:04.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "ba4a204a9e5a"
down_revision: str | Sequence[str] | None = "c6a8c264126e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    sa.Enum("open", "resolved", "dismissed", name="flag_status").create(
        op.get_bind(), checkfirst=True
    )

    op.create_table(
        "flags",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("bill_id", sa.Uuid(), nullable=False),
        sa.Column("flag_type", sa.String(100), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM("open", "resolved", "dismissed", name="flag_status", create_type=False),
            server_default="open",
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["bill_id"], ["bills.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_flags_user_id"), "flags", ["user_id"], unique=False)
    op.create_index(op.f("ix_flags_bill_id"), "flags", ["bill_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_flags_bill_id"), table_name="flags")
    op.drop_index(op.f("ix_flags_user_id"), table_name="flags")
    op.drop_table("flags")

    sa.Enum(name="flag_status").drop(op.get_bind(), checkfirst=True)
