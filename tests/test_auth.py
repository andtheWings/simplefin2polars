"""Tests for _auth.py."""

import base64
from unittest.mock import MagicMock, patch

import pytest

from simplefin2polars._auth import sfin_claim_token


def _encode(url: str) -> str:
    return base64.b64encode(url.encode()).decode()


class TestSfinClaimToken:
    def test_invalid_base64_raises(self):
        with pytest.raises(ValueError, match="Failed to Base64-decode"):
            sfin_claim_token("!!!not-valid-base64!!!")

    def test_http_url_raises(self):
        http_token = _encode("http://bridge.simplefin.org/claim/demo")
        with pytest.raises(ValueError, match="HTTPS"):
            sfin_claim_token(http_token)

    def test_403_raises_permission_error(self):
        token = _encode("https://bridge.simplefin.org/claim/demo")
        mock_resp = MagicMock()
        mock_resp.status_code = 403

        with patch("simplefin2polars._auth.requests.post", return_value=mock_resp):
            with pytest.raises(PermissionError, match="already been claimed"):
                sfin_claim_token(token)

    def test_non_200_raises_runtime_error(self):
        token = _encode("https://bridge.simplefin.org/claim/demo")
        mock_resp = MagicMock()
        mock_resp.status_code = 500

        with patch("simplefin2polars._auth.requests.post", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="500"):
                sfin_claim_token(token)

    def test_success_returns_stripped_url(self):
        token = _encode("https://bridge.simplefin.org/claim/demo")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "  https://user:pass@sfin.example.com/api  "

        with patch("simplefin2polars._auth.requests.post", return_value=mock_resp):
            result = sfin_claim_token(token)

        assert result == "https://user:pass@sfin.example.com/api"
