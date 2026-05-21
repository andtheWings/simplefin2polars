"""simplefin2polars — SimpleFIN protocol client with Polars DataFrames.

A Python port of the simplefinr R package. Queries the SimpleFIN protocol
and parses responses into Polars DataFrames instead of tibbles.

Public API
----------
Authentication
    sfin_claim_token

Credential store
    sfin_set_access_url
    sfin_get_access_url
    sfin_delete_access_url
    sfin_list_keys

Querying
    sfin_accounts
    sfin_transactions
"""

from simplefin2polars._accounts import sfin_accounts
from simplefin2polars._auth import sfin_claim_token
from simplefin2polars._keyring import (
    sfin_delete_access_url,
    sfin_get_access_url,
    sfin_list_keys,
    sfin_set_access_url,
)
from simplefin2polars._transactions import sfin_transactions

__all__ = [
    "sfin_claim_token",
    "sfin_set_access_url",
    "sfin_get_access_url",
    "sfin_delete_access_url",
    "sfin_list_keys",
    "sfin_accounts",
    "sfin_transactions",
]

__version__ = "0.1.0"
