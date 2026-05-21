"""sfin_transactions(): convenience wrapper returning only transactions."""

from typing import Any, List, Optional, Union

import polars as pl

from simplefin2polars._accounts import sfin_accounts


def sfin_transactions(
    access_url: Optional[str] = None,
    key: Optional[str] = None,
    start_date: Any = None,
    end_date: Any = None,
    pending: bool = False,
    account: Optional[Union[str, List[str]]] = None,
    join_accounts: bool = False,
) -> pl.DataFrame:
    """Retrieve transactions from a SimpleFIN server.

    A convenience wrapper around :func:`sfin_accounts` that returns only the
    transactions DataFrame. Optionally left-joins account-level metadata
    (name, currency, connection) onto each transaction row.

    Parameters
    ----------
    access_url:
        See :func:`sfin_accounts`.
    key:
        See :func:`sfin_accounts`.
    start_date:
        See :func:`sfin_accounts`.
    end_date:
        See :func:`sfin_accounts`.
    pending:
        See :func:`sfin_accounts`.
    account:
        See :func:`sfin_accounts`.
    join_accounts:
        If ``True``, left-join the accounts DataFrame onto the transactions
        by ``account_id``, adding columns ``account_name``, ``conn_id``,
        ``conn_name``, and ``currency`` to every transaction row.
        Default ``False``.

    Returns
    -------
    polars.DataFrame
        One row per transaction. Columns when ``join_accounts=False``:

        ===============  =================  ========================================
        Column           Type               Description
        ===============  =================  ========================================
        account_id       Utf8               Account the transaction belongs to
        transaction_id   Utf8               Unique transaction ID within the account
        posted           Datetime (UTC)     Post date; null for pending transactions
        transacted_at    Datetime (UTC)     Transaction date, if provided
        amount           Float64            Positive = deposit, negative = withdrawal
        description      Utf8               Human-readable description
        pending          Boolean            True if not yet posted
        ===============  =================  ========================================

        When ``join_accounts=True``, four additional columns appear after
        ``account_id``: ``account_name``, ``conn_id``, ``conn_name``,
        ``currency``.

    Notes
    -----
    Any server-level errors are surfaced as warnings (same as
    :func:`sfin_accounts`). Inspect them by calling :func:`sfin_accounts`
    directly and checking ``result["errors"]``.
    """
    result = sfin_accounts(
        access_url=access_url,
        key=key,
        start_date=start_date,
        end_date=end_date,
        pending=pending,
        account=account,
    )

    txns = result["transactions"]

    if not join_accounts:
        return txns

    acct_meta = result["accounts"].select(
        ["account_id", "account_name", "conn_id", "conn_name", "currency"]
    )

    merged = txns.join(acct_meta, on="account_id", how="left")

    return merged.select(
        [
            "account_id",
            "account_name",
            "conn_id",
            "conn_name",
            "currency",
            "transaction_id",
            "posted",
            "transacted_at",
            "amount",
            "description",
            "pending",
        ]
    )
