"""Add type column to OrderList

Revision ID: d928b5d616f2
Revises: fcbaeec252fc
Create Date: 2024-10-04 21:45:46.309273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd928b5d616f2'
down_revision = 'fcbaeec252fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_list', schema=None) as batch_op:
        batch_op.add_column(sa.Column('type', sa.String(length=10), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_list', schema=None) as batch_op:
        batch_op.drop_column('type')

    # ### end Alembic commands ###