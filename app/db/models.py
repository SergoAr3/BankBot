import datetime

from sqlalchemy import BigInteger, String, ForeignKey, Numeric, DateTime, Enum, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .model_types import TransactionType, CreditJobType


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now())



class ScheduledCreditJob(Base):
    __tablename__ = "scheduled_credit_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    apscheduler_job_id: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    credit_id: Mapped[int] = mapped_column(ForeignKey("credits.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(Enum(CreditJobType), nullable=False)
    run_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)


class ScheduledDepositJob(Base):
    __tablename__ = "scheduled_deposit_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    apscheduler_job_id: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    deposit_id: Mapped[int] = mapped_column(ForeignKey("deposits.id", ondelete="CASCADE"))
    run_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(64))
    balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    blocking: Mapped[bool] = mapped_column(Boolean, default=False)


class Credit(Base):
    __tablename__ = "credits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    term: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    percent: Mapped[int] = mapped_column(nullable=False)
    remaining_debt: Mapped[float] = mapped_column(nullable=False, default=0)
    closed: Mapped[bool] = mapped_column(Boolean, default=False)


class Deposit(Base):
    __tablename__ = "deposits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    percent: Mapped[int] = mapped_column(nullable=False)
    payment_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    payment_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)


class Channel(Base):
    __tablename__ = "channels_guide"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_channel_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)


class ChannelSubscription(Base):
    __tablename__ = "channel_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels_guide.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)


class CatImage(Base):
    __tablename__ = "cat_images_guide"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)


class UserCat(Base):
    __tablename__ = "user_cats"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    cat_image_id: Mapped[int] = mapped_column(ForeignKey("cat_images_guide.id"), index=True)
    bought_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now())
