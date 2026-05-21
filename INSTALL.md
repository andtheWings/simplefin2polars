# Installation Guide

## From GitHub (Recommended)

### Quick Install

```bash
pip install git+https://github.com/andtheWings/simplefin2polars.git
```

### Install a Specific Version/Tag

```bash
pip install git+https://github.com/andtheWings/simplefin2polars.git@v0.1.0
```

### Install from a Specific Branch

```bash
pip install git+https://github.com/andtheWings/simplefin2polars.git@main
```

## Development Installation

If you want to contribute or modify the code:

```bash
# Clone the repository
git clone https://github.com/andtheWings/simplefin2polars.git
cd simplefin2polars

# Install in editable mode with development dependencies
pip install -e ".[dev]"

# Run tests to verify installation
pytest
```

## Requirements

- Python >= 3.9
- Dependencies (automatically installed):
  - polars >= 0.20
  - requests >= 2.28
  - keyring >= 23.0
  - tzdata >= 2023.3 (Windows only)

## Upgrading

To upgrade to the latest version from GitHub:

```bash
pip install --upgrade git+https://github.com/andtheWings/simplefin2polars.git
```

## Uninstalling

```bash
pip uninstall simplefin2polars
```

## Troubleshooting

### Windows Users

If you encounter timezone-related errors, ensure `tzdata` is installed:

```bash
pip install tzdata
```

### macOS/Linux Users

Keyring support may require additional system packages. If you encounter keyring errors:

- **macOS**: Should work out of the box with Keychain
- **Linux (GNOME)**: Install `python3-dbus` or `dbus-python`
- **Linux (KDE)**: Install `kwalletmanager`

For headless systems or if you prefer not to use keyring, you can pass the Access URL directly:

```python
import os
from simplefin2polars import sfin_accounts

result = sfin_accounts(access_url=os.environ["SIMPLEFIN_ACCESS_URL"])
```
