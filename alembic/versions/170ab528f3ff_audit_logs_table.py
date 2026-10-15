""audit logs table"""

revision = '170ab528f3ff'
down_revision = '46fb6c0fef52'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer()),
        sa.Column('username', sa.String(255)),
        sa.Column('entity_type', sa.String(128), nullable=False),
        sa.Column('entity_id', sa.String(255)),
        sa.Column('action', sa.String(16), nullable=False),
        sa.Column('old_values', sa.JSON),
        sa.Column('new_values', sa.JSON),
        sa.Column('url', sa.String(1024)),
        sa.Column('method', sa.String(16)),
        sa.Column('remote_ip', sa.String(64)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Index('ix_audit_logs_entity', 'entity_type', 'entity_id'),
        sa.Index('ix_audit_logs_user', 'user_id'),
        sa.Index('ix_audit_logs_created', 'created_at'),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
