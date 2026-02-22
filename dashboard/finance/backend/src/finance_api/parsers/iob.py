"""IOB (Indian Overseas Bank) transaction alert parser.

IOB sends SMS-style alerts, sometimes forwarded to email:
  - "IOB: A/c XX1234 Debited Rs.500.00 on 23-02-26 Bal Rs.12345.00"
  - "IOB: Rs.500.00 credited to A/c XX1234 on 23-02-26"
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from .base import BaseParser, ParsedTransaction

IOB_DEBIT_PATTERNS = [
    # "A/c XX1234 Debited Rs.500.00 on DD-MM-YY"
    re.compile(
        r"A/c\s+\w*(\d{4})\s+[Dd]ebited\s+Rs\.?\s?([\d,]+\.?\d*)\s+"
        r"on\s+(\d{2}-\d{2}-\d{2,4})",
        re.IGNORECASE,
    ),
    # "Rs.500.00 debited from A/c XX1234 on DD-MM-YY"
    re.compile(
        r"Rs\.?\s?([\d,]+\.?\d*)\s+debited\s+from\s+A/c\s+\w*(\d{4})\s+"
        r"on\s+(\d{2}-\d{2}-\d{2,4})",
        re.IGNORECASE,
    ),
]

IOB_CREDIT_PATTERNS = [
    # "Rs.500.00 credited to A/c XX1234 on DD-MM-YY"
    re.compile(
        r"Rs\.?\s?([\d,]+\.?\d*)\s+credited\s+to\s+A/c\s+\w*(\d{4})\s+"
        r"on\s+(\d{2}-\d{2}-\d{2,4})",
        re.IGNORECASE,
    ),
    # "A/c XX1234 Credited Rs.500.00 on DD-MM-YY"
    re.compile(
        r"A/c\s+\w*(\d{4})\s+[Cc]redited\s+Rs\.?\s?([\d,]+\.?\d*)\s+"
        r"on\s+(\d{2}-\d{2}-\d{2,4})",
        re.IGNORECASE,
    ),
]

BALANCE_PATTERN = re.compile(
    r"[Bb]al(?:ance)?\s+Rs\.?\s?([\d,]+\.?\d*)", re.IGNORECASE
)

IOB_SENDERS = {"alerts@iob.in", "noreply@iob.in", "donotreply@iob.in"}


def _parse_amount(s: str) -> float:
    return float(s.replace(",", ""))


def _parse_date(s: str) -> datetime:
    for fmt in ("%d-%m-%y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {s}")


class IOBParser(BaseParser):
    def matches(self, sender: str, subject: str) -> bool:
        sender_email = sender.lower().split("<")[-1].rstrip(">").strip()
        return sender_email in IOB_SENDERS or "iob" in sender.lower()

    def parse(self, sender: str, subject: str, body: str, snippet: str) -> Optional[ParsedTransaction]:
        text = f"{subject} {snippet} {body}"

        # Try debit patterns
        for pattern in IOB_DEBIT_PATTERNS:
            m = pattern.search(text)
            if m:
                groups = m.groups()
                # Pattern 1: account, amount, date. Pattern 2: amount, account, date
                if groups[0].replace(",", "").replace(".", "").isdigit():
                    amount_s, acct, date_s = groups
                else:
                    acct, amount_s, date_s = groups

                bal_match = BALANCE_PATTERN.search(text)
                return ParsedTransaction(
                    date=_parse_date(date_s),
                    amount=_parse_amount(amount_s),
                    type="debit",
                    description=snippet[:200] if snippet else None,
                    account_identifier=acct,
                    bank="IOB",
                    category="uncategorized",
                    balance_after=_parse_amount(bal_match.group(1)) if bal_match else None,
                )

        # Try credit patterns
        for pattern in IOB_CREDIT_PATTERNS:
            m = pattern.search(text)
            if m:
                groups = m.groups()
                if groups[0].replace(",", "").replace(".", "").isdigit():
                    amount_s, acct, date_s = groups
                else:
                    acct, amount_s, date_s = groups

                bal_match = BALANCE_PATTERN.search(text)
                return ParsedTransaction(
                    date=_parse_date(date_s),
                    amount=_parse_amount(amount_s),
                    type="credit",
                    description=snippet[:200] if snippet else None,
                    account_identifier=acct,
                    bank="IOB",
                    category="uncategorized",
                    balance_after=_parse_amount(bal_match.group(1)) if bal_match else None,
                )

        return None
