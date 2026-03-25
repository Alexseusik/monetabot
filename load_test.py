import asyncio
import time
from database.engine import async_session, init_db
from database.models import Client


async def simulate_user_request(user_id: int):
    """Імітує процес збереження заявки від одного користувача"""
    async with async_session() as session:
        new_client = Client(
            user_id=user_id,
            user_phone=f"38050{user_id:07d}",  # Генеруємо фейковий номер
            user_name=f"Тест_Юзер_{user_id}",
            currency="🇺🇸USD",
            amount=1000,
            operation="Купівля",
            address="1"
        )
        session.add(new_client)
        # SQLAlchemy автоматично чекатиме своєї черги для запису у файл
        await session.commit()


async def main():
    print("⏳ Ініціалізація бази даних...")
    await init_db()

    # Кількість одночасних "користувачів"
    users_count = 1000
    print(f"🚀 Запускаємо симуляцію для {users_count} одночасних заявок...")

    start_time = time.time()

    # Створюємо список завдань для asyncio
    tasks = [simulate_user_request(i) for i in range(users_count)]

    # asyncio.gather запускає всі ці завдання ОДНОЧАСНО
    await asyncio.gather(*tasks)

    end_time = time.time()
    duration = end_time - start_time

    print(f"✅ Успішно! {users_count} заявок збережено за {duration:.2f} секунд.")
    print(f"⚡ Швидкість: {users_count / duration:.2f} заявок на секунду.")


if __name__ == "__main__":
    # На Windows іноді потрібна ця строчка для уникнення помилок з EventLoop
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())