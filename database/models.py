from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, BigInteger

class Base(DeclarativeBase):
    pass

class Client(Base):
    __tablename__ = 'clients'

    req_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    user_phone: Mapped[str] = mapped_column(String(20))
    user_name: Mapped[str] = mapped_column(String(50))
    currency: Mapped[str] = mapped_column(String(5))
    amount: Mapped[int]
    operation: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(String(5))