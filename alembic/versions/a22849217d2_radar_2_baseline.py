"""radar 2 baseline (placeholder for the pre-existing radar 2 schema)

Revision ID: a22849217d2
Revises:
Create Date: 2026-10-30

This revision exists so the migration chain has a root that matches
databases already stamped with a22849217d2. It makes no changes.
"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "a22849217d2c"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Radar 2 schema already exists; nothing to do."""
    pass


def downgrade() -> None:
    """Nothing to undo."""
    pass
