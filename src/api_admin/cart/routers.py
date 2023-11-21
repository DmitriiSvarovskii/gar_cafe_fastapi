from datetime import datetime, timedelta
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, types
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Dict, List, Union
from aiogram.types import Message

from sqlalchemy import insert, select, label, join, update, delete
from .models import Cart
from ..models import Product, Order, OrderDetail
from .schemas import *
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from typing import List, Dict, Optional
from src.api_admin.product.schemas import *
from src.api_admin.product.crud import *
from src.api_admin.category.schemas import *
from src.api_admin.category.crud import *
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.config import BOT_TOKEN


router = APIRouter(
    prefix="/api/v1/store_bot",
    tags=["Store (bot)"])


@router.get("/product/", response_model=List[ProductListStore])
async def get_all_product(schema: str, store_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Product).where(
        Product.deleted_flag != True).where(Product.store_id == store_id).order_by(Product.id.desc()).execution_options(schema_translate_map={None: schema})
    result = await session.execute(query)
    products = result.scalars().all()
    return products


@router.get("/product/{product_id}/", response_model=Optional[ProductOne])
async def get_all_product(schema: str, store_id: int, product_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Product).options(selectinload(Product.unit)).where(
        Product.deleted_flag != True).where(Product.store_id == store_id).where(Product.id == product_id).execution_options(schema_translate_map={None: schema})
    result = await session.execute(query)
    products = result.scalar()
    return products


@router.get("/category/", response_model=List[CategoryBaseStore], status_code=200)
async def get_all_category(schema: str, store_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        categories = await crud_get_all_categories(schema=schema, store_id=store_id, session=session)
        return categories
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/cart/", response_model=Dict[str, Union[List[CartItem], int]])
async def read_cart_items_and_totals(schema: str, store_id: int, tg_user_id: int, session: AsyncSession = Depends(get_async_session)):
    query = (
        select(
            Product.id,
            Product.name,
            Cart.quantity,
            (Cart.quantity * Product.price).label("unit_price"),
            func.sum(Cart.quantity * Product.price).over().label("total_price")
        )
        .join(Cart, Cart.product_id == Product.id)
        .where(
            (Cart.tg_user_id == tg_user_id) & (Cart.store_id == store_id)
        )
        .group_by(Product.id, Cart.quantity, Product.name, Cart.tg_user_id)
        .execution_options(schema_translate_map={None: schema})
    )
    result = await session.execute(query)
    cart_items = []
    total_price = 0
    for row in result:
        cart_items.append({
            "id": row[0],
            "name": row[1],
            "quantity": row[2],
            "unit_price": row[3],
        })
        total_price = row[4]
    response_data = {
        "cart_items": cart_items,
        "total_price": total_price
    }
    return response_data


# @router.get("/cart/", response_model=List[CartResponse])
# async def read_cart_items_and_totals(schema: str, store_id: int, tg_user_id: int, session: AsyncSession = Depends(get_async_session)):
#     query = (
#         select(
#             Product.id,
#             Product.name,
#             Cart.quantity,
#             (Cart.quantity * Product.price).label("unit_price"),
#             func.sum(Cart.quantity * Product.price).over().label("total_price")
#         )
#         .join(Cart, Cart.product_id == Product.id)
#         .where(
#             (Cart.tg_user_id == tg_user_id) & (Cart.store_id == store_id)
#         )
#         .group_by(Product.id, Cart.quantity, Product.name, Cart.tg_user_id)
#         .execution_options(schema_translate_map={None: schema})
#     )
#     result = await session.execute(query)
#     user_data = {}
#     for row in result:
#         tg_user_id = row[4]
#         if tg_user_id not in user_data:
#             user_data[tg_user_id] = {
#                 "cart_items": [],
#                 "total_price": 0
#             }
#         user_data[tg_user_id]["cart_items"].append({
#             "id": row[0],
#             "name": row[1],
#             "quantity": row[2],
#             "unit_price": row[3],
#         })
#         user_data[tg_user_id]["total_price"] = row[4]
#     response_data = [
#         {
#             "cart_items": user_info["cart_items"],
#             "total_price": user_info["total_price"]
#         }
#         for user_info in user_data.values()
#     ]
#     return response_data

# Укажите токен своего бота

bot = Bot(token=BOT_TOKEN)
dp: Dispatcher = Dispatcher()


web_app = WebAppInfo(url='https://store.envelope-app.ru/schema=10/store_id=1/')


button_store: InlineKeyboardButton = InlineKeyboardButton(
    text='Оплата наличными',
    web_app=web_app)
button_store2: InlineKeyboardButton = InlineKeyboardButton(
    text='Оплата картой',
    web_app=web_app)


keyboard_store_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

keyboard_store_builder.row(button_store, button_store2, width=1)
keyboard_store = keyboard_store_builder


@router.post("/cart/add/")
async def add_to_cart(schema: str, data: CartCreate, session: AsyncSession = Depends(get_async_session)):
    query = select(Cart).where(Cart.tg_user_id == data.tg_user_id, Cart.product_id ==
                               data.product_id).execution_options(schema_translate_map={None: schema})
    result = await session.execute(query)
    cart_item = result.scalars().all()
    if cart_item:
        stmt = update(Cart).where(Cart.tg_user_id == data.tg_user_id, Cart.product_id == data.product_id).values(
            quantity=func.coalesce(Cart.quantity, 0) + 1).execution_options(schema_translate_map={None: schema})
        await session.execute(stmt)
    else:
        stmt = insert(Cart).values(
            **data.dict(), quantity=1).execution_options(schema_translate_map={None: schema})
        await session.execute(stmt)
    await session.commit()
    return {"status": 201, 'data': data}


@router.delete("/cart/decrease/")
async def decrease_cart_item(schema: str, data: CartCreate,  session: AsyncSession = Depends(get_async_session)):
    query = select(Cart).where(Cart.tg_user_id == data.tg_user_id, Cart.product_id ==
                               data.product_id).execution_options(schema_translate_map={None: schema})
    result = await session.execute(query)
    cart_item = result.scalar()
    if cart_item:
        if cart_item.quantity > 0:
            stmt = update(Cart).where(Cart.tg_user_id == data.tg_user_id, Cart.product_id == data.product_id).values(
                quantity=func.coalesce(Cart.quantity, 0) - 1).execution_options(schema_translate_map={None: schema})
        else:
            stmt = delete(Cart).where(Cart.tg_user_id == data.tg_user_id, Cart.product_id == data.product_id).execution_options(
                schema_translate_map={None: schema})
        await session.execute(stmt)
    else:
        return {"status": "error", "message": "Товар не найден в корзине"}
    await session.commit()
    return {"status": 201, 'data': data}


@router.delete("/cart/clear/")
async def delete_cart_items_by_tg_user_id(schema: str, store_id: int, tg_user_id: int, session: Session = Depends(get_async_session)):
    try:
        stmt = delete(Cart).where(Cart.tg_user_id == tg_user_id, Cart.store_id == store_id).execution_options(
            schema_translate_map={None: schema})
        await session.execute(stmt)
        await session.commit()
        return {"status": "success", "message": f"Корзина для пользователя №{tg_user_id} очищена."}
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/create_order/")
async def create_order(schema: str, data: CreateOrder, session: AsyncSession = Depends(get_async_session)):
    cart_query = (select(Cart.product_id,
                         Cart.quantity,
                         Product.name.label("product_name"),
                         (Product.price * Cart.quantity).label("unit_price"),
                         func.sum(Cart.quantity * Product.price).over().label("total_price")).
                  join(Cart, Cart.product_id == Product.id).
                  filter(
        Cart.tg_user_id == data.tg_user_id,
        Cart.store_id == data.store_id
    ).execution_options(
        schema_translate_map={None: schema}))
    cart_items = await session.execute(cart_query)
    cart_items = cart_items.all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    stmt_order = insert(Order).values(
        store_id=data.store_id,
        tg_user_id=data.tg_user_id,
        delivery_city=data.delivery_city,
        delivery_address=data.delivery_address,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        customer_comment=data.customer_comment
    ).returning(Order.id).execution_options(schema_translate_map={None: schema})

    result = await session.execute(stmt_order)
    order_id = result.scalar()

    # values_list = [
    #     {
    #         "store_id": data.store_id,
    #         "order_id": order_id,
    #         "product_id": cart_item.product_id,
    #         "quantity": cart_item.quantity,
    #         "unit_price": cart_item.unit_price
    #     }
    #     for cart_item in cart_items
    # ]
    values_list = []
    order_text = ""
    order_sum = cart_items[0][4]
    for cart_item in cart_items:
        values_list.append({
            "store_id": data.store_id,
            "order_id": order_id,
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity,
            "unit_price": cart_item.unit_price
        })
        product_name = cart_item[2]
        quantity = cart_item[1]
        order_text += f"{product_name} x {quantity}\n"

    new_datetime = datetime.now() + timedelta(minutes=45)
    order_text = f"Дата и время выдачи: {new_datetime.strftime('%d.%m.%Y %H:%M')}\n"
    text = order_text = f"Заказ №{order_id} от {datetime.now().strftime('%d.%m.%Y')} в {datetime.now().strftime('%H:%M')}\n" \
        f"Код клиента: {data.tg_user_id}\n" \
        "--------------------\n" \
        f"Адрес заведения: г. Томск, ул. Вадима Саратова 69\n" \
        f"Телефон заведения: +7969-069-69-69\n" \
        "--------------------\n" \
        "Ваш выбор:\n\n" \
        f"{order_text}" \
        f"\nСумма: {order_sum} руб.\n" \
        "--------------------\n" \
        f"Статус: Новый\n" \
        f"Дата и время выдачи: {new_datetime}\n"

    await send_message(chat_id=data.tg_user_id, text=text)

    stmt_order_detail = insert(OrderDetail).values(
        values_list).execution_options(schema_translate_map={None: schema})
    await session.execute(stmt_order_detail)
    stmt = delete(Cart).where(Cart.tg_user_id == data.tg_user_id, Cart.store_id == data.store_id).execution_options(
        schema_translate_map={None: schema})
    await session.execute(stmt)
    await session.commit()
    return {"status": "Order created successfully"}


@router.post("/send_message/{chat_id}")
async def send_message(chat_id: int, text: str):
    try:
        # Отправка сообщения с использованием aiogram
        await bot.send_message(chat_id, f"{text}", reply_markup=keyboard_store.as_markup(), parse_mode=ParseMode.MARKDOWN)
        return {"status": "success", "message": "Сообщение успешно отправлено"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при отправке сообщения: {str(e)}")
