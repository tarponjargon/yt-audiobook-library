"""Fix sort_order column in categories table

Revision ID: 043b3173d654
Revises: 4f6b69ce1459
Create Date: 2025-05-11 02:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '043b3173d654'
down_revision = '4f6b69ce1459'
branch_labels = None
depends_on = None


def upgrade():
    # First add the column as nullable
    op.add_column('categories', sa.Column('sort_order', sa.Integer(), nullable=True))
    
    # Then update all existing records with a default value (0)
    op.execute("UPDATE categories SET sort_order = 0 WHERE sort_order IS NULL")
    
    # Finally, set the column to not nullable if desired
    # op.alter_column('categories', 'sort_order', nullable=False)


def downgrade():
    op.drop_column('categories', 'sort_order')
