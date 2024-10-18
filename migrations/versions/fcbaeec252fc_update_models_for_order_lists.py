"""Update models for order lists

Revision ID: fcbaeec252fc
Revises: 1e11628f3378
Create Date: 2024-10-04 20:58:05.289746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fcbaeec252fc'
down_revision = '1e11628f3378'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_list',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('wholesaler_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['wholesaler_id'], ['wholesaler.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_list_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_list_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['order_list_id'], ['order_list.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('order')
    op.drop_table('order_item')
    with op.batch_alter_table('wholesaler', schema=None) as batch_op:
        batch_op.drop_column('type')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('wholesaler', schema=None) as batch_op:
        batch_op.add_column(sa.Column('type', sa.VARCHAR(length=20), nullable=True))

    op.create_table('order_item',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('order_id', sa.INTEGER(), nullable=False),
    sa.Column('product_id', sa.INTEGER(), nullable=False),
    sa.Column('quantity', sa.INTEGER(), nullable=False),
    sa.Column('price', sa.FLOAT(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('date', sa.DATE(), nullable=False),
    sa.Column('wholesaler_id', sa.INTEGER(), nullable=False),
    sa.Column('status', sa.VARCHAR(length=20), nullable=True),
    sa.Column('total_amount', sa.FLOAT(), nullable=True),
    sa.ForeignKeyConstraint(['wholesaler_id'], ['wholesaler.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('order_list_item')
    op.drop_table('order_list')
    # ### end Alembic commands ###