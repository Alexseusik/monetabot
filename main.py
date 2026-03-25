import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import config
from database.engine import init_db
from handlers.user import user_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)


async def main():
    logger.info("Инициализация бота...")

    # Оновлений синтаксис для aiogram 3.7+
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    dp.include_router(user_router)

    await init_db()
    logger.info("База данных готова.")
    logger.info("Бот успешно запущен. Ожидание сообщений...")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную.")