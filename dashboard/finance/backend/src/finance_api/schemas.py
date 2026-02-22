from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel


class TransactionOut(BaseModel):
    id: int
    account_id: Optional[int] = None
    account_name: Optional[str] = None
    date: dt.datetime
    amount: float
    type: str
    merchant: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    source: str = "email"

    model_config = {"from_attributes": True}


class AccountOut(BaseModel):
    id: int
    name: str
    type: str
    bank: str
    identifier: Optional[str] = None
    last_known_balance: Optional[float] = None
    balance_updated_at: Optional[dt.datetime] = None
    transaction_count: int = 0

    model_config = {"from_attributes": True}


class OverviewOut(BaseModel):
    total_accounts: int
    total_transactions: int
    month_debit: float
    month_credit: float
    recent_transactions: list[TransactionOut]


class MonthlySummaryOut(BaseModel):
    month: str
    total_debit: float
    total_credit: float
    transaction_count: int
    category_breakdown: Optional[dict] = None


class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int


class SyncStatusOut(BaseModel):
    last_sync: Optional[dt.datetime] = None
    emails_processed: int = 0
    last_history_id: Optional[str] = None
