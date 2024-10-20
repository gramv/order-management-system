"""Update order models

Revision ID: 1e11628f3378
Revises: a0e384198092
Create Date: 2024-10-04 17:10:53.506624

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e11628f3378'
down_revision = 'a0e384198092'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_amount', sa.Float(), nullable=True))

    with op.batch_alter_table('order_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price', sa.Float(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_item', schema=None) as batch_op:
        batch_op.drop_column('price')

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('total_amount')

    # ### end Alembic commands ###
