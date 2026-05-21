"""Tests for _parse.py."""

from datetime import timezone

import polars as pl
import pytest

from simplefin2polars._parse import (
    _empty_accounts_df,
    _empty_connections_df,
    _empty_errors_df,
    _empty_transactions_df,
    parse_account_set,
    parse_accounts,
    parse_connections,
    parse_errors,
    parse_transactions,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_ACCOUNT_SET = {
    "accounts": [
        {
            "id": "acct-001",
            "name": "Checking",
            "conn_id": "conn-1",
            "conn_name": "My Bank",
            "currency": "USD",
            "balance": "1234.56",
            "available-balance": "1200.00",
            "balance-date": 1_700_000_000,
            "transactions": [
                {
                    "id": "txn-a",
                    "posted": 1_699_950_000,
                    "transacted_at": 1_699_940_000,
                    "amount": "-42.00",
                    "description": "Coffee shop",
                    "pending": False,
                },
                {
                    "id": "txn-b",
                    "posted": 0,          # pending → null
                    "transacted_at": None,
                    "amount": "-10.00",
                    "description": "Pending charge",
                    "pending": True,
                },
            ],
        },
        {
            "id": "acct-002",
            "name": "Savings",
            "conn_id": "conn-1",
            "conn_name": "My Bank",
            "currency": "USD",
            "balance": "5000.00",
            "available-balance": None,
            "balance-date": 1_700_000_000,
            "transactions": [],
        },
    ],
    "connections": [
        {
            "conn_id": "conn-1",
            "name": "My Bank",
            "org_id": "org-xyz",
            "org_url": "https://mybank.example.com",
            "sfin_url": "https://sfin.mybank.example.com",
        }
    ],
    "errlist": [],
}

SAMPLE_ERROR_SET = {
    "accounts": [],
    "connections": [],
    "errlist": [
        {
            "code": "403",
            "msg": "Access denied for account",
            "conn_id": "conn-2",
            "account_id": "acct-003",
        }
    ],
}


# ---------------------------------------------------------------------------
# Empty constructors
# ---------------------------------------------------------------------------


class TestEmptyConstructors:
    def test_empty_accounts_schema(self):
        df = _empty_accounts_df()
        assert df.shape == (0, 8)
        assert df.schema["balance"] == pl.Float64
        assert df.schema["balance_date"] == pl.Datetime("us", "UTC")

    def test_empty_transactions_schema(self):
        df = _empty_transactions_df()
        assert df.shape == (0, 7)
        assert df.schema["amount"] == pl.Float64
        assert df.schema["pending"] == pl.Boolean

    def test_empty_connections_schema(self):
        df = _empty_connections_df()
        assert df.shape == (0, 5)

    def test_empty_errors_schema(self):
        df = _empty_errors_df()
        assert df.shape == (0, 4)


# ---------------------------------------------------------------------------
# parse_accounts
# ---------------------------------------------------------------------------


class TestParseAccounts:
    def test_returns_empty_for_none(self):
        df = parse_accounts(None)
        assert df.shape == (0, 8)

    def test_returns_empty_for_empty_list(self):
        df = parse_accounts([])
        assert df.shape == (0, 8)

    def test_row_count(self):
        df = parse_accounts(SAMPLE_ACCOUNT_SET["accounts"])
        assert df.shape[0] == 2

    def test_column_names(self):
        df = parse_accounts(SAMPLE_ACCOUNT_SET["accounts"])
        assert list(df.columns) == [
            "account_id", "account_name", "conn_id", "conn_name",
            "currency", "balance", "available_balance", "balance_date",
        ]

    def test_balance_is_float(self):
        df = parse_accounts(SAMPLE_ACCOUNT_SET["accounts"])
        assert df.schema["balance"] == pl.Float64
        assert df["balance"][0] == pytest.approx(1234.56)

    def test_null_available_balance(self):
        df = parse_accounts(SAMPLE_ACCOUNT_SET["accounts"])
        assert df["available_balance"][1] is None

    def test_balance_date_is_utc_datetime(self):
        df = parse_accounts(SAMPLE_ACCOUNT_SET["accounts"])
        assert df.schema["balance_date"] == pl.Datetime("us", "UTC")
        dt = df["balance_date"][0]
        assert dt is not None


# ---------------------------------------------------------------------------
# parse_transactions
# ---------------------------------------------------------------------------


class TestParseTransactions:
    def test_returns_empty_for_none(self):
        df = parse_transactions(None)
        assert df.shape == (0, 7)

    def test_row_count(self):
        df = parse_transactions(SAMPLE_ACCOUNT_SET["accounts"])
        # acct-001 has 2 txns, acct-002 has 0
        assert df.shape[0] == 2

    def test_pending_txn_has_null_posted(self):
        df = parse_transactions(SAMPLE_ACCOUNT_SET["accounts"])
        pending_row = df.filter(pl.col("transaction_id") == "txn-b")
        assert pending_row["posted"][0] is None

    def test_amount_is_float(self):
        df = parse_transactions(SAMPLE_ACCOUNT_SET["accounts"])
        assert df.schema["amount"] == pl.Float64
        coffee_row = df.filter(pl.col("transaction_id") == "txn-a")
        assert coffee_row["amount"][0] == pytest.approx(-42.00)

    def test_pending_column_is_boolean(self):
        df = parse_transactions(SAMPLE_ACCOUNT_SET["accounts"])
        assert df.schema["pending"] == pl.Boolean

    def test_account_id_propagated(self):
        df = parse_transactions(SAMPLE_ACCOUNT_SET["accounts"])
        assert all(v == "acct-001" for v in df["account_id"].to_list())

    def test_no_transactions_returns_empty(self):
        accounts_no_txns = [
            {**a, "transactions": []}
            for a in SAMPLE_ACCOUNT_SET["accounts"]
        ]
        df = parse_transactions(accounts_no_txns)
        assert df.shape == (0, 7)


# ---------------------------------------------------------------------------
# parse_connections
# ---------------------------------------------------------------------------


class TestParseConnections:
    def test_row_count(self):
        df = parse_connections(SAMPLE_ACCOUNT_SET["connections"])
        assert df.shape[0] == 1

    def test_columns(self):
        df = parse_connections(SAMPLE_ACCOUNT_SET["connections"])
        assert "conn_id" in df.columns
        assert "sfin_url" in df.columns

    def test_empty_list(self):
        df = parse_connections([])
        assert df.shape == (0, 5)


# ---------------------------------------------------------------------------
# parse_errors
# ---------------------------------------------------------------------------


class TestParseErrors:
    def test_empty_errlist(self):
        df = parse_errors([])
        assert df.shape == (0, 4)

    def test_row_count(self):
        df = parse_errors(SAMPLE_ERROR_SET["errlist"])
        assert df.shape[0] == 1

    def test_columns(self):
        df = parse_errors(SAMPLE_ERROR_SET["errlist"])
        assert list(df.columns) == ["code", "msg", "conn_id", "account_id"]


# ---------------------------------------------------------------------------
# parse_account_set (integration)
# ---------------------------------------------------------------------------


class TestParseAccountSet:
    def test_keys(self):
        result = parse_account_set(SAMPLE_ACCOUNT_SET)
        assert set(result.keys()) == {"accounts", "transactions", "connections", "errors"}

    def test_all_dataframes(self):
        result = parse_account_set(SAMPLE_ACCOUNT_SET)
        for name, df in result.items():
            assert isinstance(df, pl.DataFrame), f"{name} is not a DataFrame"

    def test_error_set_has_errors(self):
        result = parse_account_set(SAMPLE_ERROR_SET)
        assert len(result["errors"]) == 1
