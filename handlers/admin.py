import os
import logging
import pandas as pd

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.filters import Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from database.engine import async_session
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


# Словник для красивого відображення адрес в Excel
ADDRESS_NAMES = {
    '1': 'вул. Вишняківська 2',
    '2': 'вул. Олени Пчілки 6А',
    '3': 'пр. Миколи Бажана 1-О',
    '4': 'вул. Кирила Осьмака 1-Б',
    '5': 'вул. Зарічна, 1-В',
    '6': 'вул. Трускавецька, 6-А',
    '7': 'проспект Голосіївський 132'
}


# Команда /export (доступна тільки власникам з .env)
@admin_router.message(Command("export"), F.from_user.id.in_(config.get_admin_list()))
async def export_database(message: Message):
    wait_msg = await message.answer("⏳ Збираю дані з бази, формую звіт...")

    async with async_session() as session:
        # Отримуємо всі заявки, найновіші зверху
        result = await session.execute(select(Client).order_by(Client.req_id.desc()))
        clients = result.scalars().all()

    if not clients:
        await wait_msg.edit_text("📭 База даних наразі порожня.")
        return

    data = []
    for c in clients:
        # Форматуємо дату
        date_str = c.created_at.strftime('%d.%m.%Y %H:%M') if c.created_at else "—"
        real_address = ADDRESS_NAMES.get(c.address, c.address)

        data.append({
            "Номер": c.req_id,
            "Дата і час": date_str,
            "Ім'я клієнта": c.user_name,
            "Телефон": f"+{c.user_phone}",
            "Операція": c.operation,
            "Валюта": c.currency,
            "Сума": c.amount,
            "Відділення": real_address
        })

    # Створюємо Excel файл
    df = pd.DataFrame(data)
    filepath = "moneta_export.xlsx"
    df.to_excel(filepath, index=False)

    # Надсилаємо файл
    document = FSInputFile(filepath)
    await message.answer_document(
        document,
        caption=f"📊 <b>Звіт вивантажено!</b>\nВсього заявок: {len(clients)}"
    )

    # Зачищаємо сліди
    await wait_msg.delete()
    os.remove(filepath)
