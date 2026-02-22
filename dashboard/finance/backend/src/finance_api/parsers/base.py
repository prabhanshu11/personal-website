"""Base parser interface for transactional email parsing."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ParsedTransaction:
    """Data extracted from a transactional email."""

    date: datetime
    amount: float
    type: str  # "debit" or "credit"
    merchant: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    account_identifier: Optional[str] = None  # Last 4 digits of account/card
    bank: Optional[str] = None
    balance_after: Optional[float] = None  # Available balance after transaction


class BaseParser(ABC):
    """Identifies and parses transaction emails from a specific source."""

    @abstractmethod
    def matches(self, sender: str, subject: str) -> bool:
        """Return True if this parser can handle the email."""

    @abstractmethod
    def parse(self, sender: str, subject: str, body: str, snippet: str) -> Optional[ParsedTransaction]:
        """Extract transaction data from email content.

        Returns None if the email doesn't contain a parseable transaction.
        """
