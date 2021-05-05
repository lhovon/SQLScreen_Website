"""renamed delisted to suspended

Revision ID: c7303dfc228f
Revises: 1e6940cca952
Create Date: 2021-05-05 16:08:17.728249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7303dfc228f'
down_revision = '1e6940cca952'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('quote', sa.Column('suspended', sa.Boolean(), nullable=True))
    op.drop_column('quote', 'delisted')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('quote', sa.Column('delisted', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('quote', 'suspended')
    # ### end Alembic commands ###
