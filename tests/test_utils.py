"""Tests for _utils.py."""

from datetime import date, datetime, timezone

import pytest

from simplefin2polars._utils import (
    null_to_na_bool,
    null_to_na_float,
    null_to_na_str,
    parse_access_url,
    to_unix,
    unix_to_datetime,
)


class TestUnixToDatetime:
    def test_valid_timestamp(self):
        dt = unix_to_datetime(1_700_000_000)
        assert isinstance(dt, datetime)
        assert dt.tzinfo == timezone.utc

    def test_zero_returns_none(self):
        assert unix_to_datetime(0) is None

    def test_none_returns_none(self):
        assert unix_to_datetime(None) is None

    def test_string_timestamp(self):
        dt = unix_to_datetime("1700000000")
        assert isinstance(dt, datetime)

    def test_non_numeric_string_returns_none(self):
        assert unix_to_datetime("not-a-number") is None


class TestToUnix:
    def test_datetime(self):
        dt = datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        assert to_unix(dt) == int(dt.timestamp())

    def test_date(self):
        d = date(2024, 1, 15)
        expected = int(datetime(2024, 1, 15, tzinfo=timezone.utc).timestamp())
        assert to_unix(d) == expected

    def test_numeric(self):
        assert to_unix(1_700_000_000) == 1_700_000_000


class TestNullCoercions:
    def test_null_to_na_str_none(self):
        assert null_to_na_str(None) is None

    def test_null_to_na_str_value(self):
        assert null_to_na_str("hello") == "hello"
        assert null_to_na_str(42) == "42"

    def test_null_to_na_float_none(self):
        assert null_to_na_float(None) is None

    def test_null_to_na_float_string(self):
        assert null_to_na_float("3.14") == pytest.approx(3.14)

    def test_null_to_na_float_invalid(self):
        assert null_to_na_float("not-a-number") is None

    def test_null_to_na_bool_none(self):
        assert null_to_na_bool(None) is None

    def test_null_to_na_bool_false(self):
        assert null_to_na_bool(False) is False

    def test_null_to_na_bool_true(self):
        assert null_to_na_bool(True) is True


class TestParseAccessUrl:
    def test_valid_url(self):
        url = "https://user123:pass456@host.example.com/path/to/api"
        result = parse_access_url(url)
        assert result["username"] == "user123"
        assert result["password"] == "pass456"
        assert result["base_url"] == "https://host.example.com/path/to/api"

    def test_missing_credentials_raises(self):
        with pytest.raises(ValueError, match="Could not parse"):
            parse_access_url("https://host.example.com/path")

    def test_http_scheme_accepted(self):
        url = "http://u:p@host.example.com/path"
        result = parse_access_url(url)
        assert result["base_url"] == "http://host.example.com/path"
