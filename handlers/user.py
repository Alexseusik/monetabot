import logging
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from database.models import Client
from keyboards.inline import get_admin_order_keyboard
from keyboards.reply import (
    get_main_menu, get_currency_menu,
    get_address_menu, get_cancel_menu, get_phone_menu
)
from utils.data_loader import NETWORK_DATA
from utils.states import ExchangeForm

logger = logging.getLogger(__name__)

# Створюємо роутер
user_router = Router()


# --- ОБРОБНИК СКАСУВАННЯ (КНОПКА НАЗАД) ---
@user_router.message(F.text == "До головного меню")
async def cancel_handler(message: Message, state: FSMContext):
    """Скидає стан FSM та повертає до головного меню."""
    await state.clear()
    await message.answer(
        "Ви повернулись до головного меню. Оберіть дію:",
        reply_markup=get_main_menu()
    )


# --- ГОЛОВНЕ МЕНЮ ТА ІНФО ---
@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    company_name = NETWORK_DATA.get("company_name", "Мережа обміну валют")

    text = (
        f"Я чат-бот мережі ліцензованих пунктів обміну валют «{company_name}».\n"
        "З моєю допомогою можна:\n\n"
        "🔸 вигідно купувати та продавати валюту;\n"
        "🔸 ознайомитися з процедурою обміну, графіком роботи;\n"
        "🔸 дізнатися адреси наших пунктів у Києві.\n"
        "❕ гарантуємо конфіденційність\n\n"
        "Оберіть потрібну дію:"
    )
    await message.answer(text, reply_markup=get_main_menu())


@user_router.message(F.text == "📌Процедура обміну")
async def process_info(message: Message):
    currencies_list = "\n".join([f"🔸 {c}" for c in NETWORK_DATA["currencies"]])

    text = (
        f"🕐 Час роботи: {NETWORK_DATA['work_hours']}\n\n"
        f"Працюємо з валютами:\n{currencies_list}\n\n"
        f"{NETWORK_DATA['limits_and_rules']}\n\n"
        f"📱 <a href='{NETWORK_DATA['support_link']}'>Відділ продажів</a>"
    )

    await message.answer(text, reply_markup=get_main_menu(), disable_web_page_preview=True)


@user_router.message(F.text == "🌐Адреси обмінників")
async def addresses_info(message: Message):
    text = "🏦 <b>Наші відділення:</b>\n\n"
    for branch_id, data in NETWORK_DATA["branches"].items():
        text += f"📍 <b>{branch_id}.</b> {data['address']}\n"
    await message.answer(text, reply_markup=get_main_menu())


# --- ВОРОНКА ЗАЯВКИ (FSM) ---

# 1. Початок: Вибір Купити/Продати
@user_router.message(F.text.in_({"📈Купити валюту", "📉Продати валюту"}))
async def start_exchange(message: Message, state: FSMContext):
    operation = "Купівля" if message.text == "📈Купити валюту" else "Продаж"
    await state.update_data(exchange_type=operation)
    await state.set_state(ExchangeForm.currency)

    await message.answer(f"Яку валюту ви хочете {operation.lower()}?", reply_markup=get_currency_menu())


# 2. Вибір валюти
@user_router.message(ExchangeForm.currency)
async def process_currency(message: Message, state: FSMContext):
    if message.text not in NETWORK_DATA["currencies"]:
        await message.answer("Будь ласка, оберіть валюту з клавіатури нижче.")
        return

    await state.update_data(currency=message.text)
    await state.set_state(ExchangeForm.address)

    text = "Оберіть пункт обміну:\n\n"
    for branch_id, data in NETWORK_DATA["branches"].items():
        text += f"<b>{branch_id}️⃣</b> {data['address']}\n"

    await message.answer(text, reply_markup=get_address_menu())


# 3. Вибір адреси
@user_router.message(ExchangeForm.address)
async def process_address(message: Message, state: FSMContext):
    if message.text not in NETWORK_DATA["branches"]:
        await message.answer("Будь ласка, оберіть адресу цифрами з клавіатури.")
        return

    await state.update_data(address=message.text)
    await state.set_state(ExchangeForm.amount)
    await message.answer("Введіть суму, яку Ви хочете обміняти (тільки цифри):", reply_markup=get_cancel_menu())


# 4. Введення суми
@user_router.message(ExchangeForm.amount)
async def process_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Будь ласка, введіть суму без символів та пробілів (наприклад: 1000).")
        return

    await state.update_data(amount=message.text)
    await state.set_state(ExchangeForm.phone)
    await message.answer(
        "Натисніть кнопку «Поділитись номером», щоб менеджер міг зв'язатися з Вами.",
        reply_markup=get_phone_menu()
    )


# 5. Отримання контакту та збереження в БД
@user_router.message(ExchangeForm.phone, F.contact)
async def process_phone(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    """
    Зверніть увагу: ми автоматично отримуємо session: AsyncSession з Middleware.
    Ручне підключення більше не потрібне!
    """
    data = await state.get_data()
    phone = message.contact.phone_number

    # Працюємо напряму з переданою сесією
    new_client = Client(
        user_id=message.from_user.id,
        user_phone=phone,
        user_name=message.from_user.first_name or "Без імені",
        currency=data['currency'],
        amount=int(data['amount']),
        operation=data['exchange_type'],
        address=data['address']
    )
    session.add(new_client)
    await session.flush()  # Зберігаємо в БД, щоб отримати req_id, але ще не фіксуємо остаточно
    req_id = new_client.req_id
    await session.commit()  # Фіксуємо зміни (Middleware міг би зробити це сам, але краще явно для FSM)

    # --- ФОРМАТУВАННЯ НОМЕРА ---
    current_date = datetime.now()
    order_number = f"{current_date.strftime('%Y%m')}{req_id}"

    process_verb = "купити" if data['exchange_type'] == "Купівля" else "продати"
    branch_info = NETWORK_DATA["branches"][data['address']]
    branch_code = branch_info["code"]

    text_for_workers = (
        f"🔴 <b>Нова заявка №{order_number}</b>\n\n"
        f"Валюта: {data['currency']}\n"
        f"Операційна каса: {branch_code}\n"
        f"Сума: {data['amount']}\n"
        f"Клієнт хоче {process_verb}\n\n"
        f"Ім'я клієнта: {message.from_user.first_name}\n"
        f"Телефон: +{phone}"
    )

    try:
        if config.group_thread_id == 0:
            # Тестовий режим (відправляємо просто в особисті повідомлення)
            await bot.send_message(
                chat_id=config.group_chat_id,
                text=text_for_workers,
                reply_markup=get_admin_order_keyboard(req_id, order_number)
            )
        else:
            # Бойовий режим (відправляємо у вказану гілку супергрупи)
            await bot.send_message(
                chat_id=config.group_chat_id,
                message_thread_id=config.group_thread_id,
                text=text_for_workers,
                reply_markup=get_admin_order_keyboard(req_id, order_number)
            )
    except Exception as e:
        logger.error(f"Помилка відправки заявки в групу: {e}", exc_info=True)

    success_text = (
        f"✅ <b>Ваше замовлення №{order_number} відправлено!</b>\n\n"
        f"Операція: {data['exchange_type']}\n"
        f"Сума: {data['amount']} {data['currency']}\n\n"
        "Наш менеджер зв'яжеться з Вами найближчим часом."
    )
    await message.answer(success_text, reply_markup=get_main_menu())
    await state.clear()


# Якщо на етапі відправки телефону надіслали текст, а не контакт
@user_router.message(ExchangeForm.phone)
async def process_phone_invalid(message: Message):
    await message.answer("Будь ласка, використайте кнопку «Поділитись номером» внизу екрану.")
