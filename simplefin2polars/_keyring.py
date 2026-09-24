"""OS credential-store integration for SimpleFIN Access URLs.

Access URLs are stored under the fixed service name "simplefin" (matching
the R package's namespace so credentials are interoperable) with a
user-chosen key as the account/username field.
"""

import polars as pl

_SFIN_SERVICE = "simplefin"


def _get_keyring():
    try:
        import keyring
        return keyring
    except ImportError as exc:
        raise ImportError(
            "The 'keyring' package is required to use credential-store "
            "functions. Install it with: pip install keyring"
        ) from exc


def sfin_set_access_url(access_url: str, key: str = "default") -> str:
    """Save a SimpleFIN Access URL to the OS credential store.

    Uses the system keyring (macOS Keychain, Windows Credential Store, or
    the Secret Service on Linux) via the ``keyring`` package.

    Parameters
    ----------
    access_url:
        The Access URL returned by :func:`sfin_claim_token`.
    key:
        A name that identifies this credential, e.g. ``"personal"`` or
        ``"business"``. Defaults to ``"default"``.

    Returns
    -------
    str
        The ``access_url``, unchanged.
    """
    kr = _get_keyring()
    kr.set_password(_SFIN_SERVICE, key, access_url)
    return access_url


def sfin_get_access_url(key: str = "default") -> str:
    """Retrieve a stored SimpleFIN Access URL from the OS credential store.

    Parameters
    ----------
    key:
        The name used when the credential was stored with
        :func:`sfin_set_access_url`. Defaults to ``"default"``.

    Returns
    -------
    str
        The stored Access URL.

    Raises
    ------
    KeyError
        If no credential is found for the given key.
    """
    kr = _get_keyring()
    result = kr.get_password(_SFIN_SERVICE, key)
    if result is None:
        raise KeyError(
            f"No SimpleFIN Access URL found for key '{key}'. "
            f"Store one first with sfin_set_access_url(access_url, key='{key}')."
        )
    return result


def sfin_delete_access_url(key: str = "default") -> None:
    """Remove a stored SimpleFIN Access URL from the OS credential store.

    This does **not** revoke the credential on the SimpleFIN server.
    Visit your SimpleFIN Bridge account to revoke server-side access.

    Parameters
    ----------
    key:
        The name of the credential to remove. Defaults to ``"default"``.
    """
    kr = _get_keyring()
    kr.delete_password(_SFIN_SERVICE, key)


def sfin_list_keys() -> pl.DataFrame:
    """List all SimpleFIN key names stored in the OS credential store.

    Returns a Polars DataFrame with one column ``key``, one row per stored
    credential name.

    .. note::
        Listing credentials is a backend-specific operation. This function
        works on most platforms (Windows Credential Manager, macOS Keychain,
        Secret Service on Linux) but may raise ``NotImplementedError`` on
        backends that do not expose a list API. If it fails, use
        :func:`sfin_get_access_url` with a known key name instead.

    Returns
    -------
    polars.DataFrame
        DataFrame with column ``key`` (Utf8).

    Raises
    ------
    NotImplementedError
        If the active keyring backend does not support listing credentials.
    """
    kr = _get_keyring()

    backend = kr.get_keyring()

    # Try the standard keyring ≥ 24 API first
    if hasattr(backend, "get_all_credentials"):
        creds = backend.get_all_credentials(_SFIN_SERVICE)
        keys = [c.username for c in creds]
        return pl.DataFrame({"key": keys})

    # Fallback: some backends expose a keyring-specific API
    try:
        # keyring.backend.SecretService, WinVaultKeyring, etc.
        items = backend.get_all_service_names()  # type: ignore[attr-defined]
        keys = [k for k in items if k.startswith(_SFIN_SERVICE + ":")]
        return pl.DataFrame({"key": [k[len(_SFIN_SERVICE) + 1:] for k in keys]})
    except AttributeError:
        pass

    raise NotImplementedError(
        "Your keyring backend does not support listing credentials. "
        "Use sfin_get_access_url() with a known key name instead."
    )
