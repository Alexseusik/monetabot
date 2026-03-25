from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import config
from database.models import Base

# Додаємо параметр connect_args={"timeout": 20}
# Тепер база буде чекати до 20 секунд, поки інший процес не закінчить запис
engine = create_async_engine(
    config.db_path,
    echo=False,  # Я вимкнув логування (echo=False), щоб консоль не "захлинулася" від 1000 SQL-запитів
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)