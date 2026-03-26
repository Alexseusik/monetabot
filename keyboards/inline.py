from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

class OrderCallback(CallbackData, prefix="order"):
    action: str
    req_id: int        # <--- Додали чистий ID для БД
    order_number: str  # Красивий номер для відображення

def get_admin_order_keyboard(req_id: int, order_number: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ В роботу",
                    callback_data=OrderCallback(action="accept", req_id=req_id, order_number=order_number).pack()
                ),
                InlineKeyboardButton(
                    text="❌ Скасувати",
                    callback_data=OrderCallback(action="reject", req_id=req_id, order_number=order_number).pack()
                )
            ]
        ]
    )