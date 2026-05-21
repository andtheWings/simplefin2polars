"""Internal utility helpers for simplefin2polars."""

import re
from datetime import date, datetime, timezone
from typing import Any, Optional


def unix_to_datetime(x: Any) -> Optional[datetime]:
    """Convert a UNIX epoch integer to a timezone-aware datetime (UTC).

    Returns None for missing or zero values. The SimpleFIN protocol uses 0
    to indicate a pending transaction with no post date.
    """
    if x is None:
        return None
    try:
        val = float(x)
    except (TypeError, ValueError):
        return None
    if val == 0:
        return None
    return datetime.fromtimestamp(val, tz=timezone.utc)


def to_unix(x: Any) -> int:
    """Convert a date-like value to a UNIX timestamp integer.

    Accepts datetime, date, or a numeric value already in epoch seconds.
    date objects are interpreted as midnight UTC.
    """
    if isinstance(x, datetime):
        return int(x.timestamp())
    if isinstance(x, date):
        return int(datetime(x.year, x.month, x.day, tzinfo=timezone.utc).timestamp())
    return int(x)


def null_to_na_str(x: Any) -> Optional[str]:
    """Coerce to str or return None if missing."""
    if x is None:
        return None
    return str(x)


def null_to_na_float(x: Any) -> Optional[float]:
    """Coerce to float or return None if missing."""
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def null_to_na_bool(x: Any) -> Optional[bool]:
    """Coerce to bool or return None if missing."""
    if x is None:
        return None
    return bool(x)


def resolve_access_url(access_url: Optional[str], key: Optional[str]) -> str:
    """Return the Access URL, resolving from keyring if a key is given.

    Exactly one of access_url or key must be non-None.
    """
    if access_url is not None and key is not None:
        raise ValueError("Provide `access_url` or `key`, not both.")
    if key is not None:
        from simplefin2polars._keyring import sfin_get_access_url
        return sfin_get_access_url(key)
    if access_url is None:
        raise ValueError(
            "Provide an `access_url` or a keyring `key` (e.g. key='default'). "
            "Store an Access URL first with sfin_set_access_url()."
        )
    return access_url


def parse_access_url(access_url: str) -> dict:
    """Parse embedded Basic Auth credentials from an Access URL.

    Access URLs are of the form: https://username:password@host/path

    Returns a dict with keys: username, password, base_url.
    """
    m = re.match(r"^(https?)://([^:@/]+):([^@/]+)@(.+)$", access_url)
    if not m:
        raise ValueError(
            "Could not parse the Access URL. "
            "Expected format: https://username:password@host/path"
        )
    scheme, username, password, rest = m.groups()
    return {
        "username": username,
        "password": password,
        "base_url": f"{scheme}://{rest}",
    }
