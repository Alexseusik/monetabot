import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline import OrderCallback
from database.models import Client

logger = logging.getLogger(__name__)
admin_router = Router()

@admin_router.callback_query(OrderCallback.filter(F.action == "accept"))
async def process_accept_order(
    callback: CallbackQuery,
    callback_data: OrderCallback,
    bot: Bot,
    session: AsyncSession  # <--- Отримуємо сесію з Middleware
):
    req_id = callback_data.req_id
    order_number = callback_data.order_number
    manager_name = callback.from_user.first_name

    # Працюємо напряму з переданою сесією
    result = await session.execute(select(Client).where(Client.req_id == req_id))
    client = result.scalar_one_or_none()

    if not client:
        await callback.answer("Помилка: заявку не знайдено в базі!", show_alert=True)
        return

    try:
        await bot.send_message(
            chat_id=client.user_id,
            text=f"✅ <b>Ваша заявка №{order_number} прийнята в роботу!</b>\n\nОчікуйте повідомлення від менеджера."
        )
    except Exception as e:
        logger.error(f"Не вдалося надіслати підтвердження клієнту {client.user_id}: {e}")

    new_text = callback.message.html_text + f"\n\n🟢 <b>Взято в роботу:</b> {manager_name}"
    await callback.message.edit_text(text=new_text, reply_markup=None)
    await callback.answer("Ви прийняли заявку!")


@admin_router.callback_query(OrderCallback.filter(F.action == "reject"))
async def process_reject_order(
    callback: CallbackQuery,
    callback_data: OrderCallback,
    bot: Bot,
    session: AsyncSession  # <--- Отримуємо сесію з Middleware
):
    req_id = callback_data.req_id
    order_number = callback_data.order_number
    manager_name = callback.from_user.first_name

    # Працюємо напряму з переданою сесією
    result = await session.execute(select(Client).where(Client.req_id == req_id))
    client = result.scalar_one_or_none()

    if client:
        try:
            await bot.send_message(
                chat_id=client.user_id,
                text=f"❌ <b>Вашу заявку №{order_number} було скасовано.</b>\n\nОчікуйте повідомлення від менеджера."
            )
        except Exception as e:
            logger.error(f"Не вдалося надіслати відмову клієнту {client.user_id}: {e}")

    new_text = callback.message.html_text + f"\n\n🔴 <b>Скасовано:</b> {manager_name}"
    await callback.message.edit_text(text=new_text, reply_markup=None)
    await callback.answer("Заявку скасовано!")