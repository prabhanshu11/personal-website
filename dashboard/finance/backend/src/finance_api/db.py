from __future__ import annotations

import datetime as dt
from typing import AsyncIterator, Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from .config import get_settings


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))  # "HDFC Savings", "IOB Savings"
    type: Mapped[str] = mapped_column(String(50))  # "savings", "credit_card", "wallet"
    bank: Mapped[str] = mapped_column(String(100))  # "HDFC", "IOB"
    identifier: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # Last 4 digits
    last_known_balance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    balance_updated_at: Mapped[Optional[dt.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint("gmail_msg_id", name="uq_transactions_gmail_msg_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL"), index=True, nullable=True
    )
    gmail_msg_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Dedup key
    date: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), index=True)
    amount: Mapped[float] = mapped_column(Float)
    type: Mapped[str] = mapped_column(String(10))  # "debit", "credit"
    merchant: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="email")
    parsed_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )

    account: Mapped[Optional[Account]] = relationship(back_populates="transactions")


class MonthlySummary(Base):
    __tablename__ = "monthly_summaries"
    __table_args__ = (
        UniqueConstraint("account_id", "month", name="uq_monthly_account_month"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=True
    )
    month: Mapped[str] = mapped_column(String(7))  # "2026-02"
    total_debit: Mapped[float] = mapped_column(Float, default=0.0)
    total_credit: Mapped[float] = mapped_column(Float, default=0.0)
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    category_breakdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    updated_at: Mapped[Optional[dt.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class SyncState(Base):
    __tablename__ = "sync_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_history_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_full_sync: Mapped[Optional[dt.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    emails_processed: Mapped[int] = mapped_column(Integer, default=0)


# Engine and session factory
settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
