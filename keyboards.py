from telebot import types


def create_main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton("Повернутися до головного меню")
    markup.add(button1)
    return markup


def create_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buy_btn = types.KeyboardButton("📈Купити валюту")
    sell_btn = types.KeyboardButton("📉Продати валюту")
    process_btn = types.KeyboardButton("📌Процедура обміну")
    address_btn = types.KeyboardButton("🌐Адреси обмінників")
    markup.add(buy_btn, sell_btn, process_btn, address_btn)
    return markup


def currency_choose_keyboard():
    usd = types.KeyboardButton('🇺🇸USD')
    eur = types.KeyboardButton('🇪🇺EUR')
    pln = types.KeyboardButton('🇵🇱PLN')
    czk = types.KeyboardButton('🇨🇿CZK')
    gbp = types.KeyboardButton('🇬🇧GBP')
    menu = types.KeyboardButton('До головного меню')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).row(usd, eur).row(pln,czk,gbp).row(menu)
    return markup


def address_choose_keyboard():
    add1 = types.KeyboardButton('1')
    add2 = types.KeyboardButton('2')
    add3 = types.KeyboardButton('3')
    add4 = types.KeyboardButton('4')
    add5 = types.KeyboardButton('5')
    add6 = types.KeyboardButton('6')
    add7 = types.KeyboardButton('7')
    menu = types.KeyboardButton('До головного меню')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).row(add1, add2, add3).row(add4, add5, add6).row(add7, menu)
    return markup


def give_number() :
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    contact_button = types.KeyboardButton("Поділитись номером", request_contact=True)
    markup.add(contact_button)
    return markup


def finish_main_btn():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton("/restart")
    markup.add(button1)
    return markup
