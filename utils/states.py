from aiogram.fsm.state import State, StatesGroup

class ExchangeForm(StatesGroup):
    exchange_type = State()  # Выбор: Купить или Продать
    currency = State()       # Выбор валюты (USD, EUR...)
    address = State()        # Выбор номера отделения
    amount = State()         # Ввод суммы
    phone = State()          # Отправка контакта