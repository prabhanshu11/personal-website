"""Finance Dashboard API — Gmail transaction parser + data API.

Polls Gmail for transactional emails, parses them into structured data,
and serves it via REST endpoints for the dashboard frontend.
"""

from __future__ import annotations

import datetime as dt
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .db import (
    Account,
    MonthlySummary,
    SessionLocal,
    SyncState,
    Transaction,
    get_session,
    init_db,
)
from .gmail import GmailClient
from .parsers import ALL_PARSERS
from .parsers.base import ParsedTransaction
from .schemas import (
    AccountOut,
    CategoryBreakdown,
    MonthlySummaryOut,
    OverviewOut,
    SyncStatusOut,
    TransactionOut,
)
from .telegram_bot import TelegramNotifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
scheduler = AsyncIOScheduler()
gmail_client: Optional[GmailClient] = None
telegram: Optional[TelegramNotifier] = None


# ── Sync engine ─────────────────────────────────────────────

async def _get_or_create_account(session: AsyncSession, txn: ParsedTransaction) -> Optional[int]:
    """Find or create an account based on parsed transaction data."""
    if not txn.bank or not txn.account_identifier:
        return None

    result = await session.execute(
        select(Account).where(
            Account.bank == txn.bank,
            Account.identifier == txn.account_identifier,
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        acct_type = "credit_card" if "cc" in (txn.category or "").lower() or "credit_card" in (txn.category or "").lower() else "savings"
        account = Account(
            name=f"{txn.bank} {'CC' if acct_type == 'credit_card' else 'Savings'} **{txn.account_identifier}",
            type=acct_type,
            bank=txn.bank,
            identifier=txn.account_identifier,
        )
        session.add(account)
        await session.flush()

    # Update balance if available
    if txn.balance_after is not None:
        account.last_known_balance = txn.balance_after
        account.balance_updated_at = dt.datetime.now(dt.timezone.utc)

    return account.id


async def _store_transaction(
    session: AsyncSession, txn: ParsedTransaction, gmail_msg_id: Optional[str]
) -> Optional[Transaction]:
    """Store a parsed transaction, deduplicating by gmail_msg_id."""
    if gmail_msg_id:
        existing = await session.execute(
            select(Transaction).where(Transaction.gmail_msg_id == gmail_msg_id)
        )
        if existing.scalar_one_or_none():
            return None  # Already stored

    account_id = await _get_or_create_account(session, txn)

    record = Transaction(
        account_id=account_id,
        gmail_msg_id=gmail_msg_id,
        date=txn.date,
        amount=txn.amount,
        type=txn.type,
        merchant=txn.merchant,
        category=txn.category,
        description=txn.description,
        raw_snippet=txn.description,
        source="email",
    )
    session.add(record)
    return record


async def _update_monthly_summary(session: AsyncSession, txn_date: dt.datetime, account_id: Optional[int]) -> None:
    """Update the monthly summary for the transaction's month."""
    month_str = txn_date.strftime("%Y-%m")

    result = await session.execute(
        select(MonthlySummary).where(
            MonthlySummary.account_id == account_id,
            MonthlySummary.month == month_str,
        )
    )
    summary = result.scalar_one_or_none()

    if not summary:
        summary = MonthlySummary(
            account_id=account_id,
            month=month_str,
        )
        session.add(summary)

    # Recalculate from transactions
    debit_result = await session.execute(
        select(func.sum(Transaction.amount), func.count()).where(
            Transaction.account_id == account_id,
            Transaction.type == "debit",
            func.strftime("%Y-%m", Transaction.date) == month_str,
        )
    )
    debit_row = debit_result.one()
    summary.total_debit = debit_row[0] or 0.0

    credit_result = await session.execute(
        select(func.sum(Transaction.amount), func.count()).where(
            Transaction.account_id == account_id,
            Transaction.type == "credit",
            func.strftime("%Y-%m", Transaction.date) == month_str,
        )
    )
    credit_row = credit_result.one()
    summary.total_credit = credit_row[0] or 0.0
    summary.transaction_count = (debit_row[1] or 0) + (credit_row[1] or 0)

    # Category breakdown
    cat_result = await session.execute(
        select(Transaction.category, func.sum(Transaction.amount)).where(
            Transaction.account_id == account_id,
            Transaction.type == "debit",
            func.strftime("%Y-%m", Transaction.date) == month_str,
        ).group_by(Transaction.category)
    )
    breakdown = {row[0] or "uncategorized": row[1] for row in cat_result.all()}
    summary.category_breakdown = json.dumps(breakdown)
    summary.updated_at = dt.datetime.now(dt.timezone.utc)


async def sync_gmail() -> int:
    """Poll Gmail for new transactional emails and parse them."""
    if gmail_client is None:
        logger.warning("Gmail client not initialized, skipping sync")
        return 0

    async with SessionLocal() as session:
        # Get sync state
        result = await session.execute(select(SyncState).limit(1))
        sync_state = result.scalar_one_or_none()
        if not sync_state:
            sync_state = SyncState()
            session.add(sync_state)
            await session.flush()

        # Fetch messages (incremental if possible)
        messages = []
        new_history_id = None
        if sync_state.last_history_id:
            messages, new_history_id = await gmail_client.fetch_messages_since_history(
                sync_state.last_history_id
            )
        else:
            messages = await gmail_client.fetch_messages()

        if not messages:
            # Update history ID even if no new messages
            if not new_history_id:
                new_history_id = await gmail_client.get_current_history_id()
            sync_state.last_history_id = new_history_id
            sync_state.last_full_sync = dt.datetime.now(dt.timezone.utc)
            await session.commit()
            return 0

        count = 0
        for msg_stub in messages:
            msg_id = msg_stub.get("id") if isinstance(msg_stub, dict) else msg_stub
            try:
                message = await gmail_client.get_message(msg_id)
                headers = GmailClient.extract_headers(message)
                sender = headers.get("from", "")
                subject = headers.get("subject", "")
                body = GmailClient.extract_body_text(message)
                snippet = message.get("snippet", "")

                # Try each parser
                for parser in ALL_PARSERS:
                    if parser.matches(sender, subject):
                        parsed = parser.parse(sender, subject, body, snippet)
                        if parsed:
                            record = await _store_transaction(session, parsed, msg_id)
                            if record:
                                count += 1
                                await _update_monthly_summary(
                                    session, parsed.date, record.account_id
                                )
                                # Telegram notification
                                if telegram:
                                    await telegram.notify_transaction(
                                        parsed.amount, parsed.type, parsed.merchant, parsed.bank
                                    )
                            break  # Only one parser per message
            except Exception as e:
                logger.error(f"Error processing message {msg_id}: {e}")
                continue

        # Update sync state
        if not new_history_id:
            new_history_id = await gmail_client.get_current_history_id()
        sync_state.last_history_id = new_history_id
        sync_state.last_full_sync = dt.datetime.now(dt.timezone.utc)
        sync_state.emails_processed = (sync_state.emails_processed or 0) + len(messages)
        await session.commit()

        logger.info(f"Synced {count} new transactions from {len(messages)} emails")
        return count


# ── App lifecycle ───────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global gmail_client, telegram

    await init_db()

    # Initialize Gmail client (may fail if no credentials)
    try:
        gmail_client = GmailClient()
        gmail_client.authenticate()
        logger.info("Gmail client authenticated")
    except Exception as e:
        logger.warning(f"Gmail client not available: {e}")
        gmail_client = None

    # Initialize Telegram bot
    telegram = TelegramNotifier(SessionLocal)
    await telegram.start_polling()

    # Start scheduler
    if settings.scheduler_enabled:
        scheduler.add_job(
            sync_gmail,
            "interval",
            seconds=settings.poll_interval_seconds,
            id="gmail_sync",
            replace_existing=True,
        )
        scheduler.start()
        logger.info(f"Scheduler started (every {settings.poll_interval_seconds}s)")

    yield

    # Shutdown
    if scheduler.running:
        scheduler.shutdown(wait=False)
    await telegram.stop_polling()


app = FastAPI(title="Finance Dashboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── API endpoints ───────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "finance-api"}


@app.get("/api/overview", response_model=OverviewOut)
async def overview(session: AsyncSession = Depends(get_session)):
    now = dt.datetime.now(dt.timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Counts
    acct_count = (await session.execute(select(func.count(Account.id)))).scalar() or 0
    txn_count = (await session.execute(select(func.count(Transaction.id)))).scalar() or 0

    # Monthly totals
    debit = (await session.execute(
        select(func.sum(Transaction.amount)).where(
            Transaction.type == "debit", Transaction.date >= month_start
        )
    )).scalar() or 0.0
    credit = (await session.execute(
        select(func.sum(Transaction.amount)).where(
            Transaction.type == "credit", Transaction.date >= month_start
        )
    )).scalar() or 0.0

    # Recent transactions
    recent_result = await session.execute(
        select(Transaction).order_by(Transaction.date.desc()).limit(10)
    )
    recent = recent_result.scalars().all()

    return OverviewOut(
        total_accounts=acct_count,
        total_transactions=txn_count,
        month_debit=debit,
        month_credit=credit,
        recent_transactions=[
            TransactionOut(
                id=t.id,
                account_id=t.account_id,
                date=t.date,
                amount=t.amount,
                type=t.type,
                merchant=t.merchant,
                category=t.category,
                description=t.description,
                source=t.source,
            )
            for t in recent
        ],
    )


@app.get("/api/transactions", response_model=list[TransactionOut])
async def list_transactions(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    query = select(Transaction).order_by(Transaction.date.desc())

    if category:
        query = query.where(Transaction.category == category)
    if type:
        query = query.where(Transaction.type == type)
    if from_date:
        query = query.where(Transaction.date >= dt.datetime.fromisoformat(from_date))
    if to_date:
        query = query.where(Transaction.date <= dt.datetime.fromisoformat(to_date))

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await session.execute(query)
    txns = result.scalars().all()

    return [
        TransactionOut(
            id=t.id,
            account_id=t.account_id,
            date=t.date,
            amount=t.amount,
            type=t.type,
            merchant=t.merchant,
            category=t.category,
            description=t.description,
            source=t.source,
        )
        for t in txns
    ]


@app.get("/api/transactions/recent", response_model=list[TransactionOut])
async def recent_transactions(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Transaction).order_by(Transaction.date.desc()).limit(20)
    )
    txns = result.scalars().all()
    return [
        TransactionOut(
            id=t.id, account_id=t.account_id, date=t.date, amount=t.amount,
            type=t.type, merchant=t.merchant, category=t.category,
            description=t.description, source=t.source,
        )
        for t in txns
    ]


@app.get("/api/accounts", response_model=list[AccountOut])
async def list_accounts(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Account))
    accounts = result.scalars().all()

    out = []
    for acc in accounts:
        txn_count = (await session.execute(
            select(func.count(Transaction.id)).where(Transaction.account_id == acc.id)
        )).scalar() or 0
        out.append(AccountOut(
            id=acc.id, name=acc.name, type=acc.type, bank=acc.bank,
            identifier=acc.identifier, last_known_balance=acc.last_known_balance,
            balance_updated_at=acc.balance_updated_at, transaction_count=txn_count,
        ))
    return out


@app.get("/api/accounts/{account_id}/summary", response_model=AccountOut)
async def account_summary(account_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Account not found")

    txn_count = (await session.execute(
        select(func.count(Transaction.id)).where(Transaction.account_id == account_id)
    )).scalar() or 0

    return AccountOut(
        id=account.id, name=account.name, type=account.type, bank=account.bank,
        identifier=account.identifier, last_known_balance=account.last_known_balance,
        balance_updated_at=account.balance_updated_at, transaction_count=txn_count,
    )


@app.get("/api/spending/monthly", response_model=list[MonthlySummaryOut])
async def monthly_spending(
    months: int = Query(6, ge=1, le=24),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(MonthlySummary)
        .order_by(MonthlySummary.month.desc())
        .limit(months)
    )
    summaries = result.scalars().all()

    return [
        MonthlySummaryOut(
            month=s.month,
            total_debit=s.total_debit,
            total_credit=s.total_credit,
            transaction_count=s.transaction_count,
            category_breakdown=json.loads(s.category_breakdown) if s.category_breakdown else None,
        )
        for s in summaries
    ]


@app.get("/api/spending/categories", response_model=list[CategoryBreakdown])
async def category_breakdown(session: AsyncSession = Depends(get_session)):
    now = dt.datetime.now(dt.timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    result = await session.execute(
        select(
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
            func.count().label("count"),
        )
        .where(Transaction.type == "debit", Transaction.date >= month_start)
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
    )
    rows = result.all()

    return [
        CategoryBreakdown(
            category=row.category or "uncategorized",
            total=row.total,
            count=row.count,
        )
        for row in rows
    ]


@app.post("/api/sync/trigger")
async def trigger_sync():
    count = await sync_gmail()
    return {"status": "ok", "new_transactions": count}


@app.get("/api/sync/status", response_model=SyncStatusOut)
async def sync_status(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(SyncState).limit(1))
    state = result.scalar_one_or_none()
    if not state:
        return SyncStatusOut()
    return SyncStatusOut(
        last_sync=state.last_full_sync,
        emails_processed=state.emails_processed or 0,
        last_history_id=state.last_history_id,
    )
