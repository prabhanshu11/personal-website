"""HDFC Bank savings account transaction alert parser.

Handles debit and credit alerts from HDFC Bank.
Common formats:
  - "Rs.1234.00 debited from A/c **5678 on 23-02-26. UPI/merchant. Avl bal: Rs.9999.00"
  - "Rs.50000.00 credited to A/c **5678 on 23-02-26. NEFT-sender. Avl bal: Rs.59999.00"
  - "UPDATE: Rs 1,234.00 debited from a/c **5678 on 23-02-26 to VPA name@upi"
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from .base import BaseParser, ParsedTransaction

# HDFC debit alert patterns
HDFC_DEBIT_PATTERNS = [
    # Standard debit: "Rs.1234.00 debited from A/c **5678 on 23-02-26"
    re.compile(
        r"Rs\.?\s?([\d,]+\.?\d*)\s+debited\s+from\s+(?:A/c|a/c|Ac)\s+\*{0,2}(\d{4})\s+"
        r"on\s+(\d{2}-\d{2}-\d{2,4})",
        re.IGNORECASE,
    ),
    # UPDATE format: "UPDATE: Rs 1,234.00 debited from a/c **5678 on 23-02-26"
    re.compile(
        r"UPDATE.*?Rs\.?\s?([\d,]+\.?\d*)\s+debited\s+from\s+(?:A/c|a/c)\s+\*{0,2}(\d{4})\s+"
        r"on\s+(\d{2}-\d{2}-\d{2,4})",
        re.IGNORECASE,
    ),
]

# HDFC credit alert patterns
HDFC_CREDIT_PATTERNS = [
    # Standard credit: "Rs.50000.00 credited to A/c **5678 on 23-02-26"
    re.compile(
        r"Rs\.?\s?([\d,]+\.?\d*)\s+credited\s+to\s+(?:A/c|a/c|Ac)\s+\*{0,2}(\d{4})\s+"
        r"on\s+(\d{2}-\d{2}-\d{2,4})",
        re.IGNORECASE,
    ),
]

# Available balance after transaction
BALANCE_PATTERN = re.compile(
    r"(?:Avl\s*[Bb]al|Available\s+[Bb]alance|Avl\.?\s*Bal)[\s:]*Rs\.?\s?([\d,]+\.?\d*)",
    re.IGNORECASE,
)

# Merchant/description extraction
MERCHANT_PATTERNS = [
    # UPI: "UPI/merchant-name" or "to VPA name@upi"
    re.compile(r"(?:UPI|VPA)[/\s]+([^\s.]+)", re.IGNORECASE),
    # NEFT: "NEFT-sender-name"
    re.compile(r"NEFT[-/]([^\s.]+)", re.IGNORECASE),
    # IMPS: "IMPS/ref/name"
    re.compile(r"IMPS[/\s]+(?:\w+[/\s]+)?([^\s.]+)", re.IGNORECASE),
    # ATM
    re.compile(r"(ATM\s*(?:withdrawal|WDL)?)", re.IGNORECASE),
]

HDFC_SENDERS = {"alerts@hdfcbank.net", "noreply@hdfcbank.com"}


def _parse_amount(s: str) -> float:
    return float(s.replace(",", ""))


def _parse_date(s: str) -> datetime:
    """Parse DD-MM-YY or DD-MM-YYYY date."""
    for fmt in ("%d-%m-%y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {s}")


def _extract_merchant(text: str) -> Optional[str]:
    for pattern in MERCHANT_PATTERNS:
        m = pattern.search(text)
        if m:
            return m.group(1).strip()
    return None


def _extract_balance(text: str) -> Optional[float]:
    m = BALANCE_PATTERN.search(text)
    if m:
        return _parse_amount(m.group(1))
    return None


def _categorize_merchant(merchant: Optional[str]) -> str:
    if not merchant:
        return "uncategorized"
    ml = merchant.lower()
    if "atm" in ml:
        return "atm_withdrawal"
    if any(x in ml for x in ("swiggy", "zomato", "dominos", "mcd")):
        return "food_delivery"
    if any(x in ml for x in ("blinkit", "bigbasket", "zepto", "dmart")):
        return "groceries"
    if any(x in ml for x in ("amazon", "flipkart", "myntra")):
        return "shopping"
    if any(x in ml for x in ("neft", "imps", "upi")):
        return "transfer"
    return "uncategorized"


class HDFCDebitParser(BaseParser):
    def matches(self, sender: str, subject: str) -> bool:
        sender_email = sender.lower().split("<")[-1].rstrip(">").strip()
        return sender_email in HDFC_SENDERS and any(
            kw in subject.lower() for kw in ("debit", "debited", "transaction")
        )

    def parse(self, sender: str, subject: str, body: str, snippet: str) -> Optional[ParsedTransaction]:
        text = f"{subject} {snippet} {body}"
        for pattern in HDFC_DEBIT_PATTERNS:
            m = pattern.search(text)
            if m:
                amount = _parse_amount(m.group(1))
                acct = m.group(2)
                date = _parse_date(m.group(3))
                merchant = _extract_merchant(text)
                return ParsedTransaction(
                    date=date,
                    amount=amount,
                    type="debit",
                    merchant=merchant,
                    category=_categorize_merchant(merchant),
                    description=snippet[:200] if snippet else None,
                    account_identifier=acct,
                    bank="HDFC",
                    balance_after=_extract_balance(text),
                )
        return None


class HDFCCreditParser(BaseParser):
    def matches(self, sender: str, subject: str) -> bool:
        sender_email = sender.lower().split("<")[-1].rstrip(">").strip()
        return sender_email in HDFC_SENDERS and any(
            kw in subject.lower() for kw in ("credit", "credited", "received")
        )

    def parse(self, sender: str, subject: str, body: str, snippet: str) -> Optional[ParsedTransaction]:
        text = f"{subject} {snippet} {body}"
        for pattern in HDFC_CREDIT_PATTERNS:
            m = pattern.search(text)
            if m:
                amount = _parse_amount(m.group(1))
                acct = m.group(2)
                date = _parse_date(m.group(3))
                merchant = _extract_merchant(text)
                return ParsedTransaction(
                    date=date,
                    amount=amount,
                    type="credit",
                    merchant=merchant,
                    category="salary" if "salary" in text.lower() else _categorize_merchant(merchant),
                    description=snippet[:200] if snippet else None,
                    account_identifier=acct,
                    bank="HDFC",
                    balance_after=_extract_balance(text),
                )
        return None
