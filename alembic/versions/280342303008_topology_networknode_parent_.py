""topology: NetworkNode.parent + NodeConnection"""

revision = '280342303008'
down_revision = '2055e885da33'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    with op.batch_alter_table('network_nodes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_node_id', sa.Integer(), sa.ForeignKey('network_nodes.id', name='fk_network_nodes_parent_node_id')))
    op.create_table('node_connections',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('src_node_id', sa.Integer(), sa.ForeignKey('network_nodes.id', name='fk_node_connections_src'), nullable=False),
        sa.Column('dst_node_id', sa.Integer(), sa.ForeignKey('network_nodes.id', name='fk_node_connections_dst'), nullable=False),
        sa.Column('media_type', sa.String(32)),
        sa.Column('bandwidth', sa.String(64)),
        sa.Column('distance_km', sa.Float()),
        sa.Column('remark', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('src_node_id', 'dst_node_id', name='uq_node_connections_src_dst'),
    )


def downgrade() -> None:
    op.drop_table('node_connections')
    with op.batch_alter_table('network_nodes', schema=None) as batch_op:
        batch_op.drop_column('parent_node_id')
