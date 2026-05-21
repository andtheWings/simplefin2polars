"""Internal parsers: JSON response dict → Polars DataFrames."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import polars as pl

from simplefin2polars._utils import (
    null_to_na_bool,
    null_to_na_float,
    null_to_na_str,
    unix_to_datetime,
)


def parse_account_set(x: Dict[str, Any]) -> Dict[str, pl.DataFrame]:
    """Parse a full Account Set response into a dict of four DataFrames.

    Parameters
    ----------
    x:
        Parsed JSON dict from the /accounts endpoint.

    Returns
    -------
    dict with keys: ``accounts``, ``transactions``, ``connections``, ``errors``.
    """
    return {
        "accounts": parse_accounts(x.get("accounts")),
        "transactions": parse_transactions(x.get("accounts")),
        "connections": parse_connections(x.get("connections")),
        "errors": parse_errors(x.get("errlist")),
    }


def parse_accounts(accounts: Optional[List[dict]]) -> pl.DataFrame:
    """Flatten the accounts array into a one-row-per-account DataFrame.

    Transactions are excluded; use :func:`parse_transactions` for those.
    """
    if not accounts:
        return _empty_accounts_df()

    account_id: List[Optional[str]] = []
    account_name: List[Optional[str]] = []
    conn_id: List[Optional[str]] = []
    conn_name: List[Optional[str]] = []
    currency: List[Optional[str]] = []
    balance: List[Optional[float]] = []
    available_balance: List[Optional[float]] = []
    balance_date: List[Optional[datetime]] = []

    for a in accounts:
        account_id.append(null_to_na_str(a.get("id")))
        account_name.append(null_to_na_str(a.get("name")))
        conn_id.append(null_to_na_str(a.get("conn_id")))
        conn_name.append(null_to_na_str(a.get("conn_name")))
        currency.append(null_to_na_str(a.get("currency")))
        balance.append(null_to_na_float(a.get("balance")))
        available_balance.append(null_to_na_float(a.get("available-balance")))
        balance_date.append(unix_to_datetime(a.get("balance-date")))

    return pl.DataFrame(
        {
            "account_id": account_id,
            "account_name": account_name,
            "conn_id": conn_id,
            "conn_name": conn_name,
            "currency": currency,
            "balance": balance,
            "available_balance": available_balance,
            "balance_date": pl.Series(balance_date, dtype=pl.Datetime("us", "UTC")),
        },
        schema={
            "account_id": pl.Utf8,
            "account_name": pl.Utf8,
            "conn_id": pl.Utf8,
            "conn_name": pl.Utf8,
            "currency": pl.Utf8,
            "balance": pl.Float64,
            "available_balance": pl.Float64,
            "balance_date": pl.Datetime("us", "UTC"),
        },
    )


def parse_transactions(accounts: Optional[List[dict]]) -> pl.DataFrame:
    """Flatten all transactions across all accounts into a single DataFrame.

    Each row includes the parent ``account_id`` for joining back to accounts.
    """
    if not accounts:
        return _empty_transactions_df()

    account_id: List[Optional[str]] = []
    transaction_id: List[Optional[str]] = []
    posted: List[Optional[datetime]] = []
    transacted_at: List[Optional[datetime]] = []
    amount: List[Optional[float]] = []
    description: List[Optional[str]] = []
    pending: List[Optional[bool]] = []

    for a in accounts:
        txns = a.get("transactions")
        if not txns:
            continue
        acct_id = null_to_na_str(a.get("id"))
        for t in txns:
            account_id.append(acct_id)
            transaction_id.append(null_to_na_str(t.get("id")))
            posted.append(unix_to_datetime(t.get("posted")))
            transacted_at.append(unix_to_datetime(t.get("transacted_at")))
            amount.append(null_to_na_float(t.get("amount")))
            description.append(null_to_na_str(t.get("description")))
            pending.append(null_to_na_bool(t.get("pending")))

    if not account_id:
        return _empty_transactions_df()

    return pl.DataFrame(
        {
            "account_id": account_id,
            "transaction_id": transaction_id,
            "posted": pl.Series(posted, dtype=pl.Datetime("us", "UTC")),
            "transacted_at": pl.Series(transacted_at, dtype=pl.Datetime("us", "UTC")),
            "amount": amount,
            "description": description,
            "pending": pending,
        },
        schema={
            "account_id": pl.Utf8,
            "transaction_id": pl.Utf8,
            "posted": pl.Datetime("us", "UTC"),
            "transacted_at": pl.Datetime("us", "UTC"),
            "amount": pl.Float64,
            "description": pl.Utf8,
            "pending": pl.Boolean,
        },
    )


def parse_connections(connections: Optional[List[dict]]) -> pl.DataFrame:
    """Flatten the connections array into a one-row-per-connection DataFrame."""
    if not connections:
        return _empty_connections_df()

    conn_id: List[Optional[str]] = []
    name: List[Optional[str]] = []
    org_id: List[Optional[str]] = []
    org_url: List[Optional[str]] = []
    sfin_url: List[Optional[str]] = []

    for c in connections:
        conn_id.append(null_to_na_str(c.get("conn_id")))
        name.append(null_to_na_str(c.get("name")))
        org_id.append(null_to_na_str(c.get("org_id")))
        org_url.append(null_to_na_str(c.get("org_url")))
        sfin_url.append(null_to_na_str(c.get("sfin_url")))

    return pl.DataFrame(
        {
            "conn_id": conn_id,
            "name": name,
            "org_id": org_id,
            "org_url": org_url,
            "sfin_url": sfin_url,
        },
        schema={
            "conn_id": pl.Utf8,
            "name": pl.Utf8,
            "org_id": pl.Utf8,
            "org_url": pl.Utf8,
            "sfin_url": pl.Utf8,
        },
    )


def parse_errors(errlist: Optional[List[dict]]) -> pl.DataFrame:
    """Flatten the errlist array into a one-row-per-error DataFrame."""
    if not errlist:
        return _empty_errors_df()

    code: List[Optional[str]] = []
    msg: List[Optional[str]] = []
    conn_id: List[Optional[str]] = []
    account_id: List[Optional[str]] = []

    for e in errlist:
        code.append(null_to_na_str(e.get("code")))
        msg.append(null_to_na_str(e.get("msg")))
        conn_id.append(null_to_na_str(e.get("conn_id")))
        account_id.append(null_to_na_str(e.get("account_id")))

    return pl.DataFrame(
        {
            "code": code,
            "msg": msg,
            "conn_id": conn_id,
            "account_id": account_id,
        },
        schema={
            "code": pl.Utf8,
            "msg": pl.Utf8,
            "conn_id": pl.Utf8,
            "account_id": pl.Utf8,
        },
    )


# ---------------------------------------------------------------------------
# Empty DataFrame constructors (correct schema, zero rows)
# ---------------------------------------------------------------------------


def _empty_accounts_df() -> pl.DataFrame:
    return pl.DataFrame(
        schema={
            "account_id": pl.Utf8,
            "account_name": pl.Utf8,
            "conn_id": pl.Utf8,
            "conn_name": pl.Utf8,
            "currency": pl.Utf8,
            "balance": pl.Float64,
            "available_balance": pl.Float64,
            "balance_date": pl.Datetime("us", "UTC"),
        }
    )


def _empty_transactions_df() -> pl.DataFrame:
    return pl.DataFrame(
        schema={
            "account_id": pl.Utf8,
            "transaction_id": pl.Utf8,
            "posted": pl.Datetime("us", "UTC"),
            "transacted_at": pl.Datetime("us", "UTC"),
            "amount": pl.Float64,
            "description": pl.Utf8,
            "pending": pl.Boolean,
        }
    )


def _empty_connections_df() -> pl.DataFrame:
    return pl.DataFrame(
        schema={
            "conn_id": pl.Utf8,
            "name": pl.Utf8,
            "org_id": pl.Utf8,
            "org_url": pl.Utf8,
            "sfin_url": pl.Utf8,
        }
    )


def _empty_errors_df() -> pl.DataFrame:
    return pl.DataFrame(
        schema={
            "code": pl.Utf8,
            "msg": pl.Utf8,
            "conn_id": pl.Utf8,
            "account_id": pl.Utf8,
        }
    )
