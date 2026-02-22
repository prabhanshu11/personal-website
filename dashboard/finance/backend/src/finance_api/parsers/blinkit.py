"""Blinkit order/delivery confirmation email parser.

Blinkit sends order confirmations with:
  - Order total
  - Delivery status
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from .base import BaseParser, ParsedTransaction

BLINKIT_AMOUNT_PATTERNS = [
    # "Total: Rs. 456" or "₹456"
    re.compile(r"(?:Total|Grand\s+Total|Amount|Bill)[:\s]*(?:Rs\.?|₹)\s?([\d,]+\.?\d*)", re.IGNORECASE),
    # "paid Rs 456"
    re.compile(r"paid\s+(?:Rs\.?|₹)\s?([\d,]+\.?\d*)", re.IGNORECASE),
]

BLINKIT_SENDERS = {"noreply@blinkit.com", "no-reply@blinkit.com", "noreply@grofers.com"}


class BlinkitParser(BaseParser):
    def matches(self, sender: str, subject: str) -> bool:
        sender_email = sender.lower().split("<")[-1].rstrip(">").strip()
        return sender_email in BLINKIT_SENDERS or "blinkit" in sender.lower()

    def parse(self, sender: str, subject: str, body: str, snippet: str) -> Optional[ParsedTransaction]:
        text = f"{subject} {snippet} {body}"

        for pattern in BLINKIT_AMOUNT_PATTERNS:
            m = pattern.search(text)
            if m:
                amount = float(m.group(1).replace(",", ""))
                return ParsedTransaction(
                    date=datetime.now(),
                    amount=amount,
                    type="debit",
                    merchant="Blinkit",
                    category="groceries",
                    description=snippet[:200] if snippet else None,
                    bank=None,
                )

        return None
