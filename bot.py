import re
import telebot
import sqlite3
from keyboards import *

admin_chat_id = 130946738

address_check = {
    '1' : '150',
    '2' : '194',
    '3' : '334',
    '4' : '78',
    '5' : '151',
    '6' : '321'
}

proccess_check = {
    'Купівля' : 'купити',
    'Продаж' : 'продати'
}

user_data = {
    'Request number' : 0,
    'User id': 0,
    'User phone': '',
    'User name' : '',
    'Currency' : '',
    'Amount' : '',
    'Exchange type': '',
    'Address': 0
}

TOKEN = '6380884350:AAFRxB35XYeYtzC6QHxeQ9Vq7xmJo9iEvkI'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message):

    chat_id = message.chat.id
    print(f'user_id {message.from_user.id}')

    if message.from_user.id == admin_chat_id:
        bot.send_message(chat_id, f"""
Вітаю {message.from_user.username} у адмін панелі бота. Нижче у вас є можливість подивитись потрібну інформацію""")
        print('Ok')

    else:
        bot.send_message(chat_id, """Я чат-бот мережі  ліцензованих пунктів обміну валют «МОНЕТА».
        
З моєю допомогою можна: 

🔸️ вигідно купувати та продавати валюту;
🔸️ ознайомитися з процедурою обміну, графіком роботи, переліком валют з якими ми працюємо;️
🔸  дізнатися адреси наших пунктів обміну валют у Києві.
❕гарантуємо конфіденційність
    
Оберіть потрібну дію:""", reply_markup=create_keyboard())
        bot.register_next_step_handler(message, choice)


@bot.message_handler(func=lambda message: (message is True) and (message.text != '/start'))
def choice(message):

    chat_id = message.chat.id
    text = message.text

    if text == "📈Купити валюту":
        bot.send_message(chat_id, "Яку валюту ви хочете купити ?", reply_markup=currency_choose_keyboard())
        bot.register_next_step_handler(message, choose_address)
        user_data['Exchange type'] = 'Купівля'

    elif text == "📉Продати валюту":
        bot.send_message(chat_id, "Яку валюту ви хочете продати ?", reply_markup=currency_choose_keyboard())
        bot.register_next_step_handler(message, choose_address)
        user_data['Exchange type'] = 'Продаж'

    elif text == "📌Процедура обміну":
        bot.send_message(chat_id, """
🕐 Час роботи: з 9:00 до 20:00  
 
Працюємо з валютами:  
🔸 Дол. США  
🔸 Євро  
🔸 Фунт-стерлінгів  
🔸 Польський злотий  
🔸 Чеська крона  
 
Відділ продажів:  
❗️Згідно чинного законодавства проводимо валютообмінні операції на суми в еквіваленті до 400 000 грн на одну людину.  
❗️Долари 1996 року, долари номіналом менше 100 та євро номіналом менше 50 купуємо тільки за роздрібним курсом.  
❗️Долари нового зразка продаємо по роздрібному курсу.  
❗️ Бронювання на 1 годину від 1000 $/€💵💶. Суми до 1000 не бронюються.  
 
📱 <a href = "https://t.me/VG_Kiev">Відділ продажів</a>
        """, parse_mode="HTML", reply_markup=create_main_menu_keyboard(), disable_web_page_preview=True)
        bot.register_next_step_handler(message, process_main_menu_choice)

    elif text == "🌐Адреси обмінників":
        bot.send_message(chat_id, """
Перелік обмінників:

🏦 Правий берег:
1. вул. Симона Петлюри, 13/135, магазин «КОЛО», +380680183006
2. проспект Голосіївський, буд. 132, БЦ РЕЛЕ, +380955884583
3. Андріївський узвіз, 34, магазин «КОЛО», +380672786678

🏦 Лівий берег:
4. вул. Олени Пчілки 6А, магазин "BOTTLE", +380675486380
5. проспект Миколи Бажана, 1-О, метро Позняки у бік правого берега, +380996400122
6. вул. Кирила Осьмака, 1-Б, Бортничі, магазин «ФОРА», +380675486381
        """, reply_markup=create_main_menu_keyboard())
        bot.register_next_step_handler(message, process_main_menu_choice)

    else:
        bot.send_message(chat_id, """Будь-ласка оберіть дію кнопкою: """, reply_markup=create_keyboard())
        bot.register_next_step_handler(message, choice)


@bot.message_handler(func=lambda message: (message is True) and (message.text != '/start'))
def choose_address(message):
    chat_id = message.chat.id
    currency = message.text

    if currency in ('🇺🇸USD', '🇪🇺EUR', '🇨🇿CZK', '🇨🇿PLN', '🇬🇧GBP'):
        user_data['Currency'] = currency

        bot.send_message(chat_id, """
Оберіть пункт в якому вам зручно провести обмін:

🏦 Правий берег:
1. вул. Симона Петлюри, 13/135, магазин «КОЛО», +380680183006
2. проспект Голосіївський, буд. 132, БЦ РЕЛЕ, +380955884583
3. Андріївський узвіз, 34, магазин «КОЛО», +380672786678

🏦 Лівий берег:
4. вул. Олени Пчілки 6А, магазин "BOTTLE", +380675486380
5. проспект Миколи Бажана, 1-О, метро Позняки у бік правого берега, +380996400122
6. вул. Кирила Осьмака, 1-Б, Бортничі, магазин «ФОРА», +380675486381""", reply_markup=address_choose_keyboard())
        bot.register_next_step_handler(message, choose_amount)

    elif currency == "До головного меню" :

        bot.send_message(chat_id, """Ви повернулись до головного меню. Оберіть дію : """,
                         reply_markup=create_keyboard())
        bot.register_next_step_handler(message, choice)

    else:
        bot.send_message(chat_id, """
        Ви обрали не правильну валюту, оберіть одну із зазначених валют, або настніть /stop
        """)
        bot.register_next_step_handler(message, choose_address)


@bot.message_handler(func=lambda message: (message is True) and (message.text != '/start'))
def choose_amount(message):
    chat_id = message.chat.id
    address = message.text

    if address in ('1', '2', '3', '4', '5', '6', '7'):

        user_data['Address'] = address

        bot.send_message(chat_id, "Введіть суму яку Ви хочете обміняти:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, choose_phone)

    elif address == "До головного меню" :

        bot.send_message(chat_id, """Ви повернулись до головного меню. Оберіть дію : """,
                         reply_markup=create_keyboard())
        bot.register_next_step_handler(message, choice)

    else:
        bot.send_message(chat_id, 'Будь ласка оберіть адресу із списку', reply_markup=address_choose_keyboard())
        bot.register_next_step_handler(message, choose_amount)


@bot.message_handler(func=lambda message: (message is True) and (message.text != '/start'))
def choose_phone(message):
    chat_id = message.chat.id
    amount = message.text
    amount_pattern = r'^\d+$'

    if re.match(amount_pattern, amount):

        user_data['Amount'] = amount

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        contact_button = types.KeyboardButton("Відправити мій номер телефону", request_contact=True)
        markup.add(contact_button)

        bot.send_message(message.chat.id, 'Натисніть кнопку «поділитись номером», '
                                          'щоб менеджер мав змогу зв`язатися з Вами для уточнення деталей угоди.',
                         reply_markup=markup)

        bot.register_next_step_handler(message, congratulation)

    elif amount == "До головного меню" :

        bot.send_message(chat_id, """Ви повернулись до головного меню. Оберіть дію : """,
                         reply_markup=create_keyboard())
        bot.register_next_step_handler(message, choice)

    else:
        bot.send_message(chat_id, 'Будь ласка введіть суму без символів')
        bot.register_next_step_handler(message, choose_phone)


@bot.message_handler(func=lambda message: (message is True) and (message.text != '/start'))
def congratulation(message):

    chat_id = message.chat.id
    phone = message.contact.phone_number

    if phone:

        user_data['User phone'] = phone

        conn = sqlite3.connect('db/clients.db')
        cur = conn.cursor()

        cur.execute(
            'CREATE TABLE IF NOT EXISTS clients(req_id int auto_increment primary key, user_id int, user_phone varchar(20), user_name varchar(50), currency varchar(5), amount int, operation varchar(20), address varchar(5))')

        conn.commit()

        cur.execute('SELECT req_id FROM clients ORDER BY req_id DESC LIMIT 1;')
        req_id = cur.fetchone()[0] + 1

        conn.commit()

        user_id = message.from_user.id
        user_name = message.from_user.first_name

        user_data['User id'] = user_id
        user_data['User name'] = user_name
        user_data['Request number'] = req_id

        cur.execute('''INSERT INTO clients 
                          (req_id, user_id, user_phone, user_name, currency, amount, operation, address)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (user_data['Request number'], user_data['User id'], user_data['User phone'],
                        user_data['User name'], user_data['Currency'], user_data['Amount'],
                        user_data['Exchange type'], user_data['Address']))
        conn.commit()

        cur.close()
        conn.close()

        bot.send_message(chat_id, f"""
Ваше замовлення:

№{user_data['Request number']}
{user_data['Exchange type']}
{user_data['Amount']}
{user_data['Currency']}

Відправлено.""")

        bot.send_message(chat_id, """
Дякуємо за Ваше замовлення.

Наш менеджер зв'яжеться з Вами найближчим часом.

🕐 Робочий час обробки заявок: з 9:00 до 20:00 кожного дня.""")

        bot.send_message(chat_id, """Якщо хочете залишити ще заявку натисніть кнопку /restart нижче""",
                         reply_markup=finish_main_btn())

        try:
            bot.send_message(admin_chat_id, f"""
            Заявка {user_data['Request number']}
            Валюта {user_data['Currency']}
            Операційна каса {address_check[user_data['Address']]}
            Сума {user_data['Amount']}
            Клієнт хоче {proccess_check[user_data['Exchange type']]}
            
            Ім'я клієнта {user_data['User name']}
            Телефон клієнта +{user_data['User phone']}
            """)
        except:
            pass

        bot.register_next_step_handler(message, choice)
        print(user_data)

    else:
        bot.send_message(chat_id, """ Будь ласка натисніть кнопку «поділитись номером», щоб менеджер мав змогу зв`язатися з Вами для уточнення деталей угоди. """)
        bot.register_next_step_handler(message, congratulation)

@bot.message_handler(commands=['restart'])
def restart_message(message):
    bot.send_message(message.chat.id, """Вітаю знову! Я чат-бот мережі  ліцензованих пунктів обміну валют «МОНЕТА».
        
З моєю допомогою можна: 

🔸️ вигідно купувати та продавати валюту;
🔸️ ознайомитися з процедурою обміну, графіком роботи, переліком валют з якими ми працюємо;️
🔸  дізнатися адреси наших пунктів обміну валют у Києві.
❕гарантуємо конфіденційність
    
Оберіть потрібну дію:""", reply_markup=create_keyboard())
    bot.register_next_step_handler(message, choice)

@bot.message_handler(func=lambda message: (message is True) and (message.text != '/start'))
def process_main_menu_choice(message):
    chat_id = message.chat.id
    text = message.text

    if text == "Повернутися до головного меню":
        bot.send_message(chat_id, "Ви повернулись до головного меню. Оберіть дію :", reply_markup=create_keyboard())
        bot.register_next_step_handler(message, choice)
    else:
        bot.send_message(chat_id, "Ви обрали іншу опцію у головному меню.")
        bot.register_next_step_handler(message, process_main_menu_choice)


if __name__ == "__main__":
    bot.polling(none_stop=True)
