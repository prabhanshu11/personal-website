"""HDFC Credit Card transaction alert parser.

Common formats:
  - "Rs 1234.00 spent on HDFC Bank Credit Card **9876 at MERCHANT on 23-02-26"
  - "Payment of Rs 5000.00 received towards HDFC Bank Credit Card **9876"
  - "Your HDFC Bank Credit Card **9876 has been used for Rs.1234.00 at MERCHANT on 23-02-26"
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from .base import BaseParser, ParsedTransaction

CC_DEBIT_PATTERNS = [
    # "Rs 1234.00 spent on HDFC Bank Credit Card **9876 at MERCHANT on DD-MM-YY"
    re.compile(
        r"Rs\.?\s?([\d,]+\.?\d*)\s+spent\s+on\s+.*?(?:Card|card)\s+\*{0,2}(\d{4})\s+"
        r"at\s+(.+?)\s+on\s+(\d{2}-\d{2}-\d{2,4})",
        re.IGNORECASE,
    ),
    # "Credit Card **9876 has been used for Rs.1234.00 at MERCHANT on DD-MM-YY"
    re.compile(
        r"(?:Card|card)\s+\*{0,2}(\d{4})\s+.*?(?:used|charged)\s+.*?"
        r"Rs\.?\s?([\d,]+\.?\d*)\s+(?:at\s+)?(.+?)\s+on\s+(\d{2}-\d{2}-\d{2,4})",
        re.IGNORECASE,
    ),
]

CC_CREDIT_PATTERNS = [
    # "Payment of Rs 5000.00 received towards HDFC Bank Credit Card **9876"
    re.compile(
        r"[Pp]ayment\s+of\s+Rs\.?\s?([\d,]+\.?\d*)\s+received\s+.*?"
        r"(?:Card|card)\s+\*{0,2}(\d{4})",
        re.IGNORECASE,
    ),
]

HDFC_SENDERS = {"alerts@hdfcbank.net", "noreply@hdfcbank.com"}


def _parse_amount(s: str) -> float:
    return float(s.replace(",", ""))


def _parse_date(s: str) -> datetime:
    for fmt in ("%d-%m-%y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {s}")


class HDFCCreditCardParser(BaseParser):
    def matches(self, sender: str, subject: str) -> bool:
        sender_email = sender.lower().split("<")[-1].rstrip(">").strip()
        return sender_email in HDFC_SENDERS and any(
            kw in subject.lower() for kw in ("credit card", "cc", "card")
        )

    def parse(self, sender: str, subject: str, body: str, snippet: str) -> Optional[ParsedTransaction]:
        text = f"{subject} {snippet} {body}"

        # Try debit patterns first (spending)
        for pattern in CC_DEBIT_PATTERNS:
            m = pattern.search(text)
            if m:
                groups = m.groups()
                # Pattern 1: amount, card, merchant, date
                # Pattern 2: card, amount, merchant, date
                if groups[0].replace(",", "").replace(".", "").isdigit():
                    amount, card, merchant, date_str = groups
                else:
                    card, amount, merchant, date_str = groups

                return ParsedTransaction(
                    date=_parse_date(date_str),
                    amount=_parse_amount(amount),
                    type="debit",
                    merchant=merchant.strip(),
                    category="credit_card_spend",
                    description=snippet[:200] if snippet else None,
                    account_identifier=card,
                    bank="HDFC",
                )

        # Try credit patterns (payment received)
        for pattern in CC_CREDIT_PATTERNS:
            m = pattern.search(text)
            if m:
                amount = _parse_amount(m.group(1))
                card = m.group(2)
                return ParsedTransaction(
                    date=datetime.now(),
                    amount=amount,
                    type="credit",
                    merchant="CC Payment",
                    category="credit_card_payment",
                    description=snippet[:200] if snippet else None,
                    account_identifier=card,
                    bank="HDFC",
                )

        return None
