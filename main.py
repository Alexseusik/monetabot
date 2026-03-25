import asyncio
import logging
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.engine import init_db
from handlers.user import user_router


def setup_logging():
    """Налаштовує логування в консоль та у файл з ротацією."""
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    # Вивід у консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Запис у файл bot.log (максимум 5 МБ, зберігаємо 3 старі копії)
    file_handler = RotatingFileHandler(
        "bot.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Застосовуємо налаштування глобально
    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler, file_handler]
    )


async def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Ініціалізація бота...")

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    dp.include_router(user_router)

    await init_db()
    logger.info("База даних готова.")
    logger.info("Бот успішно запущений. Очікування повідомлень...")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот зупинений вручну.")