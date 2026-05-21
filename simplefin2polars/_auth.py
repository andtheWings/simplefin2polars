"""SimpleFIN token-claim authentication."""

import base64

import requests


def sfin_claim_token(token: str) -> str:
    """Exchange a Base64-encoded SimpleFIN Token for a persistent Access URL.

    Takes the one-time token obtained from the SimpleFIN Bridge (or a
    compatible institution endpoint) and POSTs to the decoded claim URL to
    receive a permanent Access URL.

    Parameters
    ----------
    token:
        A Base64-encoded SimpleFIN Token string. Obtain this by visiting
        https://bridge.simplefin.org/simplefin/create.

    Returns
    -------
    str
        The Access URL, which embeds HTTP Basic Auth credentials in the form
        ``https://user:password@host/path``. Store it securely — treat it
        like a password. Pass it to :func:`sfin_set_access_url` to persist
        it in the OS credential store.

    Raises
    ------
    ValueError
        If the token cannot be Base64-decoded or does not resolve to an HTTPS
        URL.
    PermissionError
        On HTTP 403, meaning the token has already been claimed or is invalid.
    RuntimeError
        On any other unexpected HTTP status code.

    Notes
    -----
    Each token can only be claimed once. A 403 response means the token has
    already been claimed or is invalid; the user should revoke and regenerate
    their token, as it may have been compromised.
    """
    try:
        claim_url = base64.b64decode(token.strip()).decode("utf-8")
    except Exception as exc:
        raise ValueError(
            f"Failed to Base64-decode the SimpleFIN token: {exc}"
        ) from exc

    if not claim_url.startswith("https://"):
        raise ValueError(
            "The decoded SimpleFIN token must point to an HTTPS URL. "
            "Only HTTPS connections are permitted."
        )

    resp = requests.post(claim_url)

    if resp.status_code == 403:
        raise PermissionError(
            "HTTP 403: The SimpleFIN token has already been claimed or is "
            "invalid. Their token may be compromised — revoke and regenerate "
            "it from the SimpleFIN Bridge."
        )
    if resp.status_code != 200:
        raise RuntimeError(
            f"Unexpected HTTP {resp.status_code} response while claiming the token."
        )

    return resp.text.strip()
