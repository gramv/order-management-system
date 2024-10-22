"""Add status to CustomerOrder and CustomerOrderItem

Revision ID: 9a2183258bab
Revises: 355f6f200fd7
Create Date: 2024-10-18 01:03:47.955441

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9a2183258bab'
down_revision = '355f6f200fd7'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the temporary table if it exists
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_customer_order_item")

    # CustomerOrder changes
    with op.batch_alter_table('customer_order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True))
    
    # Set default status for existing orders
    op.execute("UPDATE customer_order SET status = 'pending' WHERE status IS NULL")
    
    # Make status non-nullable after setting default
    with op.batch_alter_table('customer_order', schema=None) as batch_op:
        batch_op.alter_column('status', nullable=False, server_default='pending')

    # CustomerOrderItem changes
    with op.batch_alter_table('customer_order_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('custom_product_name', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('price', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True))
        batch_op.alter_column('product_id', existing_type=sa.INTEGER(), nullable=True)
    
    # Set default price and status for existing items
    op.execute("UPDATE customer_order_item SET price = 0.0 WHERE price IS NULL")
    op.execute("UPDATE customer_order_item SET status = 'pending' WHERE status IS NULL")
    
    # Make price and status non-nullable after setting defaults
    with op.batch_alter_table('customer_order_item', schema=None) as batch_op:
        batch_op.alter_column('price', nullable=False, server_default='0.0')
        batch_op.alter_column('status', nullable=False, server_default='pending')

def downgrade():
    with op.batch_alter_table('customer_order_item', schema=None) as batch_op:
        batch_op.drop_column('status')
        batch_op.drop_column('price')
        batch_op.drop_column('custom_product_name')
        batch_op.alter_column('product_id', existing_type=sa.INTEGER(), nullable=False)

    with op.batch_alter_table('customer_order', schema=None) as batch_op:
        batch_op.drop_column('status')