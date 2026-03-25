from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from keyboards.reply import (
    get_main_menu, get_currency_menu,
    get_address_menu, get_cancel_menu, get_phone_menu
)
from utils.states import ExchangeForm
from database.engine import async_session
from database.models import Client
from config import config

# Создаем роутер. К нему мы будем привязывать все обработчики
user_router = Router()

# Словари для маппинга адресов (взято из твоего старого кода)
ADDRESS_CHECK = {
    '1': '485', '2': '78', '3': '151', '4': '321',
    '5': '575', '6': '628', '7': '194'
}


# --- ОБРАБОТЧИК ОТМЕНЫ (КНОПКА НАЗАД) ---
@user_router.message(F.text == "До головного меню")
async def cancel_handler(message: Message, state: FSMContext):
    """Сбрасывает состояние FSM и возвращает в главное меню."""
    await state.clear()
    await message.answer(
        "Ви повернулись до головного меню. Оберіть дію:",
        reply_markup=get_main_menu()
    )


# --- ГЛАВНОЕ МЕНЮ И ИНФО ---
@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "Я чат-бот мережі ліцензованих пунктів обміну валют «МОНЕТА».\n"
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
    text = (
        "🕐 Час роботи: з 9:00 до 20:00\n\n"
        "Працюємо з валютами:\n"
        "🔸 Дол. США\n🔸 Євро\n🔸 Фунт-стерлінгів\n🔸 Польський злотий\n🔸 Чеська крона\n\n"
        "❗️ Згідно чинного законодавства проводимо операції до 400 000 грн.\n"
        "❗️ Бронювання на 1 годину від 1000 $/€.\n\n"
        "📱 <a href='https://t.me/VG_Kiev'>Відділ продажів</a>"
    )
    await message.answer(text, reply_markup=get_main_menu(), disable_web_page_preview=True)


@user_router.message(F.text == "🌐Адреси обмінників")
async def addresses_info(message: Message):
    text = (
        "🏦 <b>Лівий берег</b>\n"
        "📍 вул. Вишняківська 2\n📍 вул. Олени Пчілки 6А\n📍 пр. Миколи Бажана 1-О\n"
        "📍 вул. Кирила Осьмака 1-Б\n📍 вул. Зарічна, 1-В\n📍 вул. Трускавецька, 6-А\n\n"
        "🏦 <b>Правий берег</b>\n"
        "📍 проспект Голосіївський 132"
    )
    await message.answer(text, reply_markup=get_main_menu())


# --- ВОРОНКА ЗАЯВКИ (FSM) ---

# 1. Начало: Выбор Купить/Продать
@user_router.message(F.text.in_({"📈Купити валюту", "📉Продати валюту"}))
async def start_exchange(message: Message, state: FSMContext):
    operation = "Купівля" if message.text == "📈Купити валюту" else "Продаж"
    await state.update_data(exchange_type=operation)
    await state.set_state(ExchangeForm.currency)

    await message.answer(f"Яку валюту ви хочете {operation.lower()}?", reply_markup=get_currency_menu())


# 2. Выбор валюты
@user_router.message(ExchangeForm.currency)
async def process_currency(message: Message, state: FSMContext):
    valid_currencies = ['🇺🇸USD', '🇪🇺EUR', '🇨🇿CZK', '🇵🇱PLN', '🇬🇧GBP']
    if message.text not in valid_currencies:
        await message.answer("Будь ласка, оберіть валюту з клавіатури нижче.")
        return  # Прерываем функцию, состояние не меняется

    await state.update_data(currency=message.text)
    await state.set_state(ExchangeForm.address)

    text = (
        "Оберіть пункт обміну:\n\n"
        "<b>1️⃣</b> вул. Вишняківська 2\n<b>2️⃣</b> вул. Олени Пчілки 6А\n"
        "<b>3️⃣</b> пр. Миколи Бажана 1-О\n<b>4️⃣</b> вул. Кирила Осьмака 1-Б\n"
        "<b>5️⃣</b> вул. Зарічна, 1-В\n<b>6️⃣</b> вул. Трускавецька, 6-А\n\n"
        "<b>7️⃣</b> проспект Голосіївський 132"
    )
    await message.answer(text, reply_markup=get_address_menu())


# 3. Выбор адреса
@user_router.message(ExchangeForm.address)
async def process_address(message: Message, state: FSMContext):
    if message.text not in ADDRESS_CHECK.keys():
        await message.answer("Будь ласка, оберіть адресу цифрами від 1 до 7.")
        return

    await state.update_data(address=message.text)
    await state.set_state(ExchangeForm.amount)
    await message.answer("Введіть суму, яку Ви хочете обміняти (тільки цифри):", reply_markup=get_cancel_menu())


# 4. Ввод суммы
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


# 5. Получение контакта и сохранение в БД
@user_router.message(ExchangeForm.phone, F.contact)
async def process_phone(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    phone = message.contact.phone_number

    # Сохраняем в базу данных
    async with async_session() as session:
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
        await session.flush()  # Получаем req_id до коммита
        req_id = new_client.req_id
        await session.commit()

    # Отправляем сообщение менеджерам
    process_verb = "купити" if data['exchange_type'] == "Купівля" else "продати"
    text_for_workers = (
        f"🔴 <b>Нова заявка №{req_id}</b>\n\n"
        f"Валюта: {data['currency']}\n"
        f"Операційна каса: {ADDRESS_CHECK[data['address']]}\n"
        f"Сума: {data['amount']}\n"
        f"Клієнт хоче {process_verb}\n\n"
        f"Ім'я клієнта: {message.from_user.first_name}\n"
        f"Телефон: +{phone}"
    )

    try:
        await bot.send_message(config.group_chat_id, text_for_workers)
    except Exception as e:
        print(f"Ошибка отправки в группу: {e}")  # В идеале здесь должен быть logger.error

    # Отвечаем пользователю
    success_text = (
        f"✅ <b>Ваше замовлення №{req_id} відправлено!</b>\n\n"
        f"Операція: {data['exchange_type']}\n"
        f"Сума: {data['amount']} {data['currency']}\n\n"
        "Наш менеджер зв'яжеться з Вами найближчим часом."
    )
    await message.answer(success_text, reply_markup=get_main_menu())

    # Очищаем состояние
    await state.clear()


# Если на этапе отправки телефона прислали текст, а не контакт
@user_router.message(ExchangeForm.phone)
async def process_phone_invalid(message: Message):
    await message.answer("Будь ласка, використайте кнопку «Поділитись номером» внизу екрану.")