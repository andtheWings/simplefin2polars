"""Tests for sfin_accounts() and sfin_transactions()."""

import json
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from simplefin2polars._accounts import sfin_accounts
from simplefin2polars._transactions import sfin_transactions

ACCESS_URL = "https://user:pass@sfin.example.com/api"

SAMPLE_RESPONSE = {
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
                }
            ],
        }
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


def _make_mock_resp(status: int, body: dict) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status
    mock.text = json.dumps(body)
    return mock


class TestSfinAccounts:
    def test_returns_dict_of_dataframes(self):
        with patch(
            "simplefin2polars._accounts.requests.get",
            return_value=_make_mock_resp(200, SAMPLE_RESPONSE),
        ):
            result = sfin_accounts(access_url=ACCESS_URL)

        assert set(result.keys()) == {"accounts", "transactions", "connections", "errors"}
        for df in result.values():
            assert isinstance(df, pl.DataFrame)

    def test_403_raises_permission_error(self):
        with patch(
            "simplefin2polars._accounts.requests.get",
            return_value=_make_mock_resp(403, {}),
        ):
            with pytest.raises(PermissionError):
                sfin_accounts(access_url=ACCESS_URL)

    def test_402_raises_runtime_error(self):
        with patch(
            "simplefin2polars._accounts.requests.get",
            return_value=_make_mock_resp(402, {}),
        ):
            with pytest.raises(RuntimeError, match="402"):
                sfin_accounts(access_url=ACCESS_URL)

    def test_server_errors_emit_warning(self):
        body_with_errors = {**SAMPLE_RESPONSE, "errlist": [
            {"code": "500", "msg": "oops", "conn_id": "c1", "account_id": "a1"}
        ]}
        with patch(
            "simplefin2polars._accounts.requests.get",
            return_value=_make_mock_resp(200, body_with_errors),
        ):
            with pytest.warns(UserWarning, match="error"):
                result = sfin_accounts(access_url=ACCESS_URL)

        assert len(result["errors"]) == 1

    def test_both_access_url_and_key_raises(self):
        with pytest.raises(ValueError, match="not both"):
            sfin_accounts(access_url=ACCESS_URL, key="default")

    def test_neither_access_url_nor_key_raises(self):
        with pytest.raises(ValueError, match="Provide"):
            sfin_accounts()

    def test_start_date_added_to_params(self):
        from datetime import date

        with patch(
            "simplefin2polars._accounts.requests.get",
            return_value=_make_mock_resp(200, SAMPLE_RESPONSE),
        ) as mock_get:
            sfin_accounts(access_url=ACCESS_URL, start_date=date(2024, 1, 1))

        call_kwargs = mock_get.call_args
        params = dict(call_kwargs[1]["params"])
        assert "start-date" in params


class TestSfinTransactions:
    def test_returns_dataframe(self):
        with patch(
            "simplefin2polars._accounts.requests.get",
            return_value=_make_mock_resp(200, SAMPLE_RESPONSE),
        ):
            df = sfin_transactions(access_url=ACCESS_URL)

        assert isinstance(df, pl.DataFrame)
        assert "transaction_id" in df.columns

    def test_join_accounts_adds_columns(self):
        with patch(
            "simplefin2polars._accounts.requests.get",
            return_value=_make_mock_resp(200, SAMPLE_RESPONSE),
        ):
            df = sfin_transactions(access_url=ACCESS_URL, join_accounts=True)

        assert "account_name" in df.columns
        assert "currency" in df.columns

    def test_join_accounts_column_order(self):
        with patch(
            "simplefin2polars._accounts.requests.get",
            return_value=_make_mock_resp(200, SAMPLE_RESPONSE),
        ):
            df = sfin_transactions(access_url=ACCESS_URL, join_accounts=True)

        expected_start = ["account_id", "account_name", "conn_id", "conn_name", "currency"]
        assert df.columns[: len(expected_start)] == expected_start
