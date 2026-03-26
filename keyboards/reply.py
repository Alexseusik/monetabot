from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from utils.data_loader import NETWORK_DATA

def get_main_menu() -> ReplyKeyboardMarkup:
    # Залишаємо без змін, це сталі кнопки
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📈Купити валюту"), KeyboardButton(text="📉Продати валюту")],
            [KeyboardButton(text="📌Процедура обміну"), KeyboardButton(text="🌐Адреси обмінників")]
        ],
        resize_keyboard=True
    )

def get_currency_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    # Динамічно додаємо всі валюти з JSON
    for curr in NETWORK_DATA["currencies"]:
        builder.add(KeyboardButton(text=curr))

    # Вирівнюємо: наприклад, по 2 кнопки в ряд
    builder.adjust(2)
    # Додаємо кнопку повернення окремим нижнім рядом
    builder.row(KeyboardButton(text='До головного меню'))
    return builder.as_markup(resize_keyboard=True)


def get_address_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    # Динамічно додаємо номери відділень (1, 2, 3...)
    for branch_id in NETWORK_DATA["branches"].keys():
        builder.add(KeyboardButton(text=branch_id))

    # Вирівнюємо по 3 кнопки в ряд
    builder.adjust(3)
    builder.row(KeyboardButton(text='До головного меню'))
    return builder.as_markup(resize_keyboard=True)


def get_cancel_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='До головного меню')]],
        resize_keyboard=True
    )


def get_phone_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поділитись номером", request_contact=True)],
            [KeyboardButton(text='До головного меню')]
        ],
        resize_keyboard=True,
        # one_time_keyboard скроет клавиатуру после нажатия (удобно для отправки контакта)
        one_time_keyboard=True
    )