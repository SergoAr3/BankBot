from os import getenv
import enum

from dotenv import load_dotenv
from sqlalchemy import BigInteger, String, ForeignKey, Numeric, DateTime, Boolean, Enum

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

load_dotenv()
engine = create_async_engine(getenv('DATABASE_URL'))

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass

class TransactionType(str, enum.Enum):
    PURCHASE = "purchase"
    CREDIT = "credit"
    DEPOSIT = "deposit"
    SUBSCRIPTION = "subscription"
    TRANSFER = 'transfer'

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now())

    user: Mapped["User"] = relationship("User", back_populates="transactions")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64))
    balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    credits: Mapped[list["Credit"]] = relationship("Credit", back_populates="user", lazy="selectin")
    deposits: Mapped[list["Deposit"]] = relationship("Deposit", back_populates="user", lazy="selectin")
    channel_subscriptions: Mapped[list["ChannelSubscription"]] = relationship("ChannelSubscription", back_populates="user", lazy="selectin")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user", lazy="selectin")



class Credit(Base):
    __tablename__ = "credits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    amount: Mapped[int] = mapped_column(nullable=False)
    term: Mapped[int] = mapped_column(nullable=False)
    percent: Mapped[int] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="credits", lazy="selectin")


class Deposit(Base):
    __tablename__ = "deposits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    amount: Mapped[int] = mapped_column(nullable=False)
    term: Mapped[int] = mapped_column(nullable=False)
    percent: Mapped[int] = mapped_column(nullable=False)
    payment_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    payment_amount: Mapped[int] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="deposits", lazy="selectin")


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False)

    channel_subscriptions: Mapped[list["ChannelSubscription"]] = relationship("ChannelSubscription",
                                                                             back_populates="channel", lazy="selectin")


class ChannelSubscription(Base):
    __tablename__ = "channel_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    subscription: Mapped[bool] = mapped_column(Boolean)

    user: Mapped["User"] = relationship("User", back_populates="channel_subscriptions", lazy="selectin")
    channel: Mapped["Channel"] = relationship("Channel", back_populates="channel_subscriptions", lazy="selectin")

