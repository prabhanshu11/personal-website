"""Swiggy order confirmation email parser.

Swiggy sends order confirmations with:
  - Order total in subject or body
  - Restaurant name
  - Items ordered
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from .base import BaseParser, ParsedTransaction

# Swiggy amount patterns
SWIGGY_AMOUNT_PATTERNS = [
    # "Total: Rs. 456" or "Grand Total ₹456"
    re.compile(r"(?:Total|Grand\s+Total|Amount)[:\s]*(?:Rs\.?|₹)\s?([\d,]+\.?\d*)", re.IGNORECASE),
    # "paid Rs 456" or "Paid ₹456"
    re.compile(r"paid\s+(?:Rs\.?|₹)\s?([\d,]+\.?\d*)", re.IGNORECASE),
    # "Order worth Rs. 456"
    re.compile(r"(?:order|bill)\s+(?:worth|of)\s+(?:Rs\.?|₹)\s?([\d,]+\.?\d*)", re.IGNORECASE),
]

RESTAURANT_PATTERN = re.compile(
    r"(?:from|at|order(?:ed)?\s+from)\s+([A-Z][A-Za-z\s'&-]+?)(?:\s+(?:is|has|was|via|on|\.))",
    re.IGNORECASE,
)

SWIGGY_SENDERS = {"noreply@swiggy.in", "no-reply@swiggy.in", "noreply@swiggy.com"}


class SwiggyParser(BaseParser):
    def matches(self, sender: str, subject: str) -> bool:
        sender_email = sender.lower().split("<")[-1].rstrip(">").strip()
        return sender_email in SWIGGY_SENDERS or "swiggy" in sender.lower()

    def parse(self, sender: str, subject: str, body: str, snippet: str) -> Optional[ParsedTransaction]:
        text = f"{subject} {snippet} {body}"

        for pattern in SWIGGY_AMOUNT_PATTERNS:
            m = pattern.search(text)
            if m:
                amount = float(m.group(1).replace(",", ""))
                restaurant_match = RESTAURANT_PATTERN.search(text)
                restaurant = restaurant_match.group(1).strip() if restaurant_match else "Swiggy"

                return ParsedTransaction(
                    date=datetime.now(),
                    amount=amount,
                    type="debit",
                    merchant=f"Swiggy - {restaurant}",
                    category="food_delivery",
                    description=snippet[:200] if snippet else None,
                    bank=None,
                )

        return None
