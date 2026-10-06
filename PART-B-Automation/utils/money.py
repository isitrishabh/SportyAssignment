"""Helpers for working with monetary values without floating-point errors."""
import re
from decimal import ROUND_HALF_UP, Decimal

_CENT = Decimal("0.01")
_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


def to_decimal(value) -> Decimal:
    """Convert API numbers (int/float) to Decimal via str to avoid binary float artefacts."""
    return Decimal(str(value))


def parse_amount(text: str) -> Decimal:
    """Extract the first number from UI text such as 'Balance: €120.00' or '#B-1 €20.50'."""
    match = _NUMBER.search(text.replace(",", ""))
    if match is None:
        raise ValueError(f"No number found in {text!r}")
    return Decimal(match.group())


def potential_payout(stake: Decimal, odds: Decimal) -> Decimal:
    return (stake * odds).quantize(_CENT, rounding=ROUND_HALF_UP)
