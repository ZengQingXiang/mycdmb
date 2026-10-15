""rbac: replace is_admin with role enum + backfill"""

revision = '46fb6c0fef52'
down_revision = '280342303008'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # Step 1: add nullable role column
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(32), nullable=True))

    # Step 2: backfill
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE users SET role='ADMIN' WHERE is_admin=1"))
    conn.execute(sa.text("UPDATE users SET role='VIEWER' WHERE is_admin=0"))

    # Step 3: make role NOT NULL
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('role', existing_type=sa.String(32), nullable=False)

    # Step 4: drop old is_admin
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_admin')


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=True))
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE users SET is_admin=1 WHERE role='ADMIN'"))
    conn.execute(sa.text("UPDATE users SET is_admin=0 WHERE role!='ADMIN'"))
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('is_admin', existing_type=sa.Boolean(), nullable=False)
        batch_op.drop_column('role')
