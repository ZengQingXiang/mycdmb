""initial schema"""

revision = '0170efb2a570'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_table('customers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('contact_person', sa.String(255)),
        sa.Column('contact_phone', sa.String(64)),
        sa.Column('address', sa.String(500)),
        sa.Column('business_type', sa.String(32), nullable=False, default='OTHER'),
        sa.Column('remark', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table('network_nodes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('network_type', sa.String(32), nullable=False),
        sa.Column('node_role', sa.String(32), nullable=False),
        sa.Column('node_name', sa.String(255), nullable=False),
        sa.Column('location', sa.String(500)),
        sa.Column('management_ip', sa.String(64)),
        sa.Column('remark', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('network_type', 'node_name', name='uq_network_nodes_type_name'),
    )
    op.create_table('cpe_devices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id', name='fk_cpe_devices_customer_id')),
        sa.Column('device_type', sa.String(32), nullable=False),
        sa.Column('vendor', sa.String(128)),
        sa.Column('model', sa.String(128)),
        sa.Column('serial_number', sa.String(255)),
        sa.Column('mac_address', sa.String(64)),
        sa.Column('management_ip', sa.String(64)),
        sa.Column('location', sa.String(500)),
        sa.Column('remark', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('serial_number', 'mac_address', name='uq_cpe_serial_mac'),
    )
    op.create_table('access_links',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id', name='fk_access_links_customer_id'), nullable=False),
        sa.Column('cpe_device_id', sa.Integer(), sa.ForeignKey('cpe_devices.id', name='fk_access_links_cpe_device_id'), nullable=False),
        sa.Column('network_node_id', sa.Integer(), sa.ForeignKey('network_nodes.id', name='fk_access_links_network_node_id'), nullable=False),
        sa.Column('network_type', sa.String(32), nullable=False),
        sa.Column('media_type', sa.String(32), nullable=False, default='FIBER'),
        sa.Column('fiber_core_count', sa.Integer()),
        sa.Column('install_date', sa.Date()),
        sa.Column('remark', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('customer_id', 'cpe_device_id', 'network_node_id', 'network_type', name='uq_access_links_cpe_node_net'),
    )


def downgrade() -> None:
    op.drop_table('access_links')
    op.drop_table('cpe_devices')
    op.drop_table('network_nodes')
    op.drop_table('customers')
