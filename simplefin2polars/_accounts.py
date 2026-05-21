"""sfin_accounts(): retrieve accounts and transactions from a SimpleFIN server."""

import json
import warnings
from typing import Any, Dict, List, Optional, Union

import polars as pl
import requests

from simplefin2polars._parse import parse_account_set
from simplefin2polars._utils import parse_access_url, resolve_access_url, to_unix


def sfin_accounts(
    access_url: Optional[str] = None,
    key: Optional[str] = None,
    start_date: Any = None,
    end_date: Any = None,
    pending: bool = False,
    account: Optional[Union[str, List[str]]] = None,
    balances_only: bool = False,
) -> Dict[str, pl.DataFrame]:
    """Retrieve accounts and transactions from a SimpleFIN server.

    Issues a ``GET /accounts`` request to the SimpleFIN Access URL and
    returns the response as a dict of four Polars DataFrames: ``accounts``,
    ``transactions``, ``connections``, and ``errors``.

    Parameters
    ----------
    access_url:
        The Access URL returned by :func:`sfin_claim_token`. Must be an
        HTTPS URL with embedded Basic Auth credentials in the form
        ``https://username:password@host/path``. Provide either this or
        ``key``, not both.
    key:
        A keyring key name set via :func:`sfin_set_access_url`. When
        supplied the Access URL is retrieved from the OS credential store
        and ``access_url`` must be ``None``.
    start_date:
        Restrict transactions to those posted on or after this date.
        Accepts a :class:`datetime.datetime`, :class:`datetime.date`, or a
        numeric UNIX timestamp.
    end_date:
        Restrict transactions to those posted before (**not including**)
        this date. Same accepted types as ``start_date``.
    pending:
        If ``True``, include pending transactions (if supported by the
        server). Default ``False``.
    account:
        A single account ID or list of account IDs to filter to.
    balances_only:
        If ``True``, skip transaction data and return only account
        balances. Default ``False``.

    Returns
    -------
    dict[str, polars.DataFrame]
        A dict with four DataFrames:

        - **accounts** — one row per account.
          Columns: ``account_id``, ``account_name``, ``conn_id``,
          ``conn_name``, ``currency``, ``balance`` (Float64),
          ``available_balance`` (Float64), ``balance_date``
          (Datetime UTC).

        - **transactions** — one row per transaction.
          Columns: ``account_id``, ``transaction_id``, ``posted``
          (Datetime UTC), ``transacted_at`` (Datetime UTC),
          ``amount`` (Float64), ``description``, ``pending``
          (Boolean). ``posted`` is ``null`` for pending transactions.

        - **connections** — one row per institution connection.
          Columns: ``conn_id``, ``name``, ``org_id``, ``org_url``,
          ``sfin_url``.

        - **errors** — one row per server-reported error.
          Columns: ``code``, ``msg``, ``conn_id``, ``account_id``.

    Raises
    ------
    PermissionError
        On HTTP 403 (access revoked or bad credentials).
    RuntimeError
        On HTTP 402 (payment required) or any other unexpected status.

    Warns
    -----
    UserWarning
        If the server returns a non-empty ``errors`` table, a warning is
        issued; inspect ``result["errors"]`` alongside the other frames.
    """
    access_url = resolve_access_url(access_url, key)
    parsed = parse_access_url(access_url)

    # Build query parameters. The SimpleFIN spec uses kebab-case names.
    params: List[tuple] = [("version", "2")]

    if start_date is not None:
        params.append(("start-date", to_unix(start_date)))
    if end_date is not None:
        params.append(("end-date", to_unix(end_date)))
    if pending:
        params.append(("pending", "1"))
    if balances_only:
        params.append(("balances-only", "1"))
    if account is not None:
        if isinstance(account, str):
            account = [account]
        for acct_id in account:
            params.append(("account", acct_id))

    url = parsed["base_url"].rstrip("/") + "/accounts"

    resp = requests.get(
        url,
        params=params,
        auth=(parsed["username"], parsed["password"]),
    )

    if resp.status_code == 403:
        raise PermissionError(
            "HTTP 403: Access denied. Credentials may be invalid or access "
            "has been revoked. Visit your SimpleFIN Bridge to reconnect."
        )
    if resp.status_code == 402:
        raise RuntimeError(
            "HTTP 402: Payment required to access this SimpleFIN server."
        )
    if resp.status_code != 200:
        raise RuntimeError(
            f"Unexpected HTTP {resp.status_code} response from the SimpleFIN server."
        )

    body = json.loads(resp.text)
    result = parse_account_set(body)

    if len(result["errors"]) > 0:
        n = len(result["errors"])
        warnings.warn(
            f"{n} error(s) returned by the server. "
            "Check result['errors'] for details.",
            UserWarning,
            stacklevel=2,
        )

    return result
