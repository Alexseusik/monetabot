from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📈Купити валюту"), KeyboardButton(text="📉Продати валюту")],
            [KeyboardButton(text="📌Процедура обміну"), KeyboardButton(text="🌐Адреси обмінників")]
        ],
        resize_keyboard=True
    )

def get_currency_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🇺🇸USD'), KeyboardButton(text='🇪🇺EUR')],
            [KeyboardButton(text='🇵🇱PLN'), KeyboardButton(text='🇨🇿CZK'), KeyboardButton(text='🇬🇧GBP')],
            [KeyboardButton(text='До головного меню')]
        ],
        resize_keyboard=True
    )

def get_address_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='1'), KeyboardButton(text='2'), KeyboardButton(text='3')],
            [KeyboardButton(text='4'), KeyboardButton(text='5'), KeyboardButton(text='6')],
            [KeyboardButton(text='7'), KeyboardButton(text='До головного меню')]
        ],
        resize_keyboard=True
    )

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