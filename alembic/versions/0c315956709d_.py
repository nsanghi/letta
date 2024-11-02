from typing import Sequence, Union

import sqlalchemy as sa

import letta.metadata
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0c315956709d"
down_revision: Union[str, None] = "9a505cc7eca9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename tables first
    op.rename_table("organizations", "organization")
    op.rename_table("tools", "tool")
    op.rename_table("users", "user")

    # Step 1: Add new `_id` columns without setting them as primary keys yet
    op.add_column("organization", sa.Column("_id", sa.String(), nullable=False, default=sa.func.uuid_generate_v4()))
    op.add_column("tool", sa.Column("_id", sa.String(), nullable=False, default=sa.func.uuid_generate_v4()))
    op.add_column("user", sa.Column("_id", sa.String(), nullable=False, default=sa.func.uuid_generate_v4()))

    # Step 2: Drop old `id` columns
    op.drop_column("organization", "id")
    op.drop_column("tool", "id")
    op.drop_column("user", "id")

    # Step 3: Set `_id` as primary keys explicitly
    op.create_primary_key("pk_organization", "organization", ["_id"])
    op.create_primary_key("pk_tool", "tool", ["_id"])
    op.create_primary_key("pk_user", "user", ["_id"])

    # Step 4: Add remaining columns for `organization`, `tool`, and `user` tables
    op.add_column("organization", sa.Column("deleted", sa.Boolean(), nullable=False))
    op.add_column("organization", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True))
    op.add_column("organization", sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False))
    op.add_column("organization", sa.Column("_created_by_id", sa.String(), nullable=True))
    op.add_column("organization", sa.Column("_last_updated_by_id", sa.String(), nullable=True))

    op.add_column("tool", sa.Column("deleted", sa.Boolean(), nullable=False))
    op.add_column("tool", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True))
    op.add_column("tool", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True))
    op.add_column("tool", sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False))
    op.add_column("tool", sa.Column("_created_by_id", sa.String(), nullable=True))
    op.add_column("tool", sa.Column("_last_updated_by_id", sa.String(), nullable=True))
    op.add_column("tool", sa.Column("_organization_id", sa.String(), nullable=False))

    op.add_column("user", sa.Column("deleted", sa.Boolean(), nullable=False))
    op.add_column("user", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True))
    op.add_column("user", sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False))
    op.add_column("user", sa.Column("_created_by_id", sa.String(), nullable=True))
    op.add_column("user", sa.Column("_last_updated_by_id", sa.String(), nullable=True))
    op.add_column("user", sa.Column("_organization_id", sa.String(), nullable=False))

    # Step 5: Modify nullable constraints on tool columns
    op.alter_column("tool", "tags", nullable=True)
    op.alter_column("tool", "source_type", nullable=True)
    op.alter_column("tool", "json_schema", nullable=True)

    # Step 6: Add foreign key constraints after primary keys are established
    op.create_foreign_key("tool_organization", "tool", "organization", ["_organization_id"], ["_id"])
    op.create_foreign_key("user_organization", "user", "organization", ["_organization_id"], ["_id"])

    # Add tool_rules column to agents
    op.add_column("agents", sa.Column("tool_rules", letta.metadata.ToolRulesColumn(), nullable=True))

    # Modify block column constraints
    op.alter_column("block", "name", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("block", "label", existing_type=sa.VARCHAR(), nullable=False)

    # Remove unneeded columns
    op.drop_column("tool", "user_id")
    op.drop_column("user", "policies_accepted")
    op.drop_column("user", "org_id")


def downgrade() -> None:
    # Revert the above operations in reverse order
    op.alter_column("block", "label", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("block", "name", existing_type=sa.VARCHAR(), nullable=False)
    op.drop_column("agents", "tool_rules")
    op.drop_constraint("user_organization", "user", type_="foreignkey")
    op.drop_constraint("tool_organization", "tool", type_="foreignkey")

    # Drop additional columns in reverse order
    op.drop_column("user", "_organization_id")
    op.drop_column("user", "_last_updated_by_id")
    op.drop_column("user", "_created_by_id")
    op.drop_column("user", "is_deleted")
    op.drop_column("user", "updated_at")
    op.drop_column("user", "created_at")
    op.drop_column("user", "deleted")

    op.drop_column("tool", "_organization_id")
    op.drop_column("tool", "_last_updated_by_id")
    op.drop_column("tool", "_created_by_id")
    op.drop_column("tool", "is_deleted")
    op.drop_column("tool", "updated_at")
    op.drop_column("tool", "created_at")
    op.drop_column("tool", "deleted")

    op.drop_column("organization", "_last_updated_by_id")
    op.drop_column("organization", "_created_by_id")
    op.drop_column("organization", "is_deleted")
    op.drop_column("organization", "updated_at")
    op.drop_column("organization", "created_at")
    op.drop_column("organization", "deleted")

    # Revert primary key changes
    op.drop_constraint("pk_user", "user", type_="primary")
    op.drop_constraint("pk_tool", "tool", type_="primary")
    op.drop_constraint("pk_organization", "organization", type_="primary")

    op.add_column("organization", sa.Column("id", sa.String(), primary_key=True))
    op.add_column("tool", sa.Column("id", sa.String(), primary_key=True))
    op.add_column("user", sa.Column("id", sa.String(), primary_key=True))

    op.drop_column("organization", "_id")
    op.drop_column("tool", "_id")
    op.drop_column("user", "_id")

    op.rename_table("user", "users")
    op.rename_table("tool", "tools")
    op.rename_table("organization", "organizations")
