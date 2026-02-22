"""Telegram bot for financial notifications and quick queries.

Uses ship-computer-bot. Runs in polling mode alongside the FastAPI app.
Commands: /balance, /recent, /spend
"""

from __future__ import annotations

import asyncio
import datetime as dt
import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .config import get_settings
from .db import Account, Transaction

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications via Telegram bot."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.settings = get_settings()
        self.session_factory = session_factory
        self._bot = None
        self._app = None

    @property
    def enabled(self) -> bool:
        return bool(self.settings.telegram_bot_token and self.settings.telegram_chat_id)

    async def _get_bot(self):
        if self._bot is None:
            from telegram import Bot
            self._bot = Bot(token=self.settings.telegram_bot_token)
        return self._bot

    async def send_message(self, text: str) -> None:
        """Send a message to the configured chat."""
        if not self.enabled:
            return
        try:
            bot = await self._get_bot()
            await bot.send_message(
                chat_id=self.settings.telegram_chat_id,
                text=text,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")

    async def notify_transaction(self, amount: float, type: str, merchant: Optional[str], bank: Optional[str]) -> None:
        """Send notification for a new transaction (high-value only)."""
        if amount < self.settings.telegram_high_value_threshold:
            return

        emoji = "\U0001f534" if type == "debit" else "\U0001f7e2"  # red/green circle
        merchant_text = f" at {merchant}" if merchant else ""
        bank_text = f" ({bank})" if bank else ""
        text = f"{emoji} <b>Rs.{amount:,.2f}</b> {type}{merchant_text}{bank_text}"
        await self.send_message(text)

    async def handle_balance(self) -> str:
        """Generate balance summary for /balance command."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Account).where(Account.last_known_balance.isnot(None))
            )
            accounts = result.scalars().all()

        if not accounts:
            return "No account balances available yet."

        lines = ["<b>Account Balances</b>\n"]
        for acc in accounts:
            lines.append(f"  {acc.name}: Rs.{acc.last_known_balance:,.2f}")
        return "\n".join(lines)

    async def handle_recent(self) -> str:
        """Generate recent transactions for /recent command."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Transaction)
                .order_by(Transaction.date.desc())
                .limit(5)
            )
            txns = result.scalars().all()

        if not txns:
            return "No transactions found yet."

        lines = ["<b>Last 5 Transactions</b>\n"]
        for t in txns:
            emoji = "\U0001f534" if t.type == "debit" else "\U0001f7e2"
            merchant = t.merchant or "Unknown"
            lines.append(f"  {emoji} Rs.{t.amount:,.2f} - {merchant} ({t.date:%d %b})")
        return "\n".join(lines)

    async def handle_spend(self) -> str:
        """Generate monthly spend summary for /spend command."""
        now = dt.datetime.now(dt.timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        async with self.session_factory() as session:
            result = await session.execute(
                select(
                    Transaction.category,
                    func.sum(Transaction.amount).label("total"),
                    func.count().label("count"),
                )
                .where(Transaction.type == "debit")
                .where(Transaction.date >= month_start)
                .group_by(Transaction.category)
                .order_by(func.sum(Transaction.amount).desc())
            )
            rows = result.all()

        if not rows:
            return f"No spending data for {now:%B %Y}."

        total = sum(r.total for r in rows)
        lines = [f"<b>Spending: {now:%B %Y}</b>\n", f"  Total: Rs.{total:,.2f}\n"]
        for r in rows:
            cat = (r.category or "uncategorized").replace("_", " ").title()
            lines.append(f"  {cat}: Rs.{r.total:,.2f} ({r.count} txns)")
        return "\n".join(lines)

    async def start_polling(self) -> None:
        """Start the Telegram bot polling loop. Call from FastAPI startup."""
        if not self.enabled:
            logger.info("Telegram bot disabled (no token/chat_id)")
            return

        from telegram.ext import Application, CommandHandler

        self._app = Application.builder().token(self.settings.telegram_bot_token).build()

        async def cmd_balance(update, context):
            text = await self.handle_balance()
            await update.message.reply_html(text)

        async def cmd_recent(update, context):
            text = await self.handle_recent()
            await update.message.reply_html(text)

        async def cmd_spend(update, context):
            text = await self.handle_spend()
            await update.message.reply_html(text)

        self._app.add_handler(CommandHandler("balance", cmd_balance))
        self._app.add_handler(CommandHandler("recent", cmd_recent))
        self._app.add_handler(CommandHandler("spend", cmd_spend))

        # Initialize and start polling in background
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling(drop_pending_updates=True)
        logger.info("Telegram bot polling started")

    async def stop_polling(self) -> None:
        """Stop the Telegram bot polling loop."""
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()
