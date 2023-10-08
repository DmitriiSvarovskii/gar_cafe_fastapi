"""1 migrations

Revision ID: f12d507c5c6d
Revises: 
Create Date: 2023-10-06 15:26:38.353994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f12d507c5c6d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('employees',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('phone', sa.BIGINT(), nullable=True),
    sa.Column('tg_user_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employees_id'), 'employees', ['id'], unique=False)
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_table('units',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_units_id'), 'units', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('availability', sa.Boolean(), nullable=True),
    sa.Column('token_bot', sa.String(), nullable=True),
    sa.Column('tg_group_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('employee_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name_rus', sa.String(), nullable=True),
    sa.Column('name_en', sa.String(), nullable=True),
    sa.Column('availability', sa.Boolean(), nullable=True),
    sa.Column('shop_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['shop_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_table('customers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('shop_id', sa.Integer(), nullable=True),
    sa.Column('tg_user_id', sa.Integer(), nullable=True),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('is_premium', sa.Boolean(), nullable=True),
    sa.Column('query_id', sa.String(), nullable=True),
    sa.Column('hash', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['shop_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tg_user_id')
    )
    op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('shop_id', sa.Integer(), nullable=True),
    sa.Column('tg_user_id', sa.Integer(), nullable=True),
    sa.Column('order_date', sa.TIMESTAMP(), nullable=True),
    sa.Column('delivery_city', sa.String(), nullable=True),
    sa.Column('delivery_address', sa.String(), nullable=True),
    sa.Column('customer_name', sa.String(), nullable=True),
    sa.Column('customer_phone', sa.String(), nullable=True),
    sa.Column('customer_comment', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['shop_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['tg_user_id'], ['customers.tg_user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('shop_id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('name_rus', sa.String(), nullable=True),
    sa.Column('name_en', sa.String(), nullable=True),
    sa.Column('description_rus', sa.String(), nullable=True),
    sa.Column('description_en', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('wt', sa.Integer(), nullable=True),
    sa.Column('unit', sa.Integer(), nullable=True),
    sa.Column('kilocalories', sa.Integer(), nullable=True),
    sa.Column('proteins', sa.Integer(), nullable=True),
    sa.Column('fats', sa.Integer(), nullable=True),
    sa.Column('carbohydrates', sa.Integer(), nullable=True),
    sa.Column('availability', sa.Boolean(), nullable=True),
    sa.Column('popular', sa.Boolean(), nullable=True),
    sa.Column('type_delivery', sa.Boolean(), nullable=True),
    sa.Column('type_takeaway', sa.Boolean(), nullable=True),
    sa.Column('type_inside', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['shop_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['unit'], ['units.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_table('cart',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('shop_id', sa.Integer(), nullable=True),
    sa.Column('tg_user_id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['shop_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['tg_user_id'], ['customers.tg_user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cart_id'), 'cart', ['id'], unique=False)
    op.create_table('order_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('unit_price', sa.Float(), nullable=True),
    sa.Column('order_date', sa.TIMESTAMP(), nullable=True),
    sa.Column('shop_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['shop_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_details_id'), 'order_details', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_order_details_id'), table_name='order_details')
    op.drop_table('order_details')
    op.drop_index(op.f('ix_cart_id'), table_name='cart')
    op.drop_table('cart')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_customers_id'), table_name='customers')
    op.drop_table('customers')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_units_id'), table_name='units')
    op.drop_table('units')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_employees_id'), table_name='employees')
    op.drop_table('employees')
    # ### end Alembic commands ###
