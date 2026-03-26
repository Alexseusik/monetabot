from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

class OrderCallback(CallbackData, prefix="order"):
    action: str
    order_number: str  # Змінили на рядок (string)

def get_admin_order_keyboard(order_number: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ В роботу", 
                    callback_data=OrderCallback(action="accept", order_number=order_number).pack()
                ),
                InlineKeyboardButton(
                    text="❌ Скасувати", 
                    callback_data=OrderCallback(action="reject", order_number=order_number).pack()
                )
            ]
        ]
    )