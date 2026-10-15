""add users table for JWT auth"""

revision = '2055e885da33'
down_revision = '0170efb2a570'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_admin', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('users')
