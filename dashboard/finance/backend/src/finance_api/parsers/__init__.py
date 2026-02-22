"""Email parser registry. Import all parsers here so they auto-register."""

from .hdfc import HDFCDebitParser, HDFCCreditParser
from .hdfc_cc import HDFCCreditCardParser
from .iob import IOBParser
from .swiggy import SwiggyParser
from .blinkit import BlinkitParser

ALL_PARSERS = [
    HDFCDebitParser(),
    HDFCCreditParser(),
    HDFCCreditCardParser(),
    IOBParser(),
    SwiggyParser(),
    BlinkitParser(),
]
