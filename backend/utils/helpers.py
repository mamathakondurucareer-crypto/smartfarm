"""Common utility functions."""

from datetime import date, datetime, timezone
import re
import json


def generate_code(prefix: str, number: int, width: int = 4) -> str:
    return f"{prefix}-{str(number).zfill(width)}"


def today() -> date:
    return date.today()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def safe_json_loads(s: str | None, default=None):
    if not s:
        return default or {}
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return default or {}


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    return a / b if b != 0 else default


def format_inr(amount: float) -> str:
    if amount >= 10_000_000:
        return f"₹{amount / 10_000_000:.2f} Cr"
    if amount >= 100_000:
        return f"₹{amount / 100_000:.2f} L"
    return f"₹{amount:,.0f}"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
