# Contributing to simplefin2polars

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/simplefin2polars.git
   cd simplefin2polars
   ```
3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes to the code

3. Add tests for your changes in the `tests/` directory

4. Run the test suite to ensure everything passes:
   ```bash
   pytest
   ```

5. Commit your changes with a clear commit message:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

### Code Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints where appropriate
- Write clear, descriptive variable and function names
- Add docstrings to new functions and classes

### Testing

- All tests must pass before submitting a pull request
- Add tests for new features
- Maintain or improve code coverage
- Run tests with: `pytest`

### Submitting Changes

1. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request on GitHub with:
   - A clear title and description
   - Reference to any related issues
   - Description of what changed and why

## Project Structure

```
simplefin2polars/
├── simplefin2polars/       # Main package code
│   ├── __init__.py         # Package exports
│   ├── auth.py             # Authentication functions
│   ├── credentials.py      # Keyring credential management
│   ├── query.py            # API query functions
│   ├── parse.py            # Response parsing to Polars
│   └── utils.py            # Utility functions
├── tests/                  # Test suite
│   ├── test_auth.py
│   ├── test_credentials.py
│   ├── test_query.py
│   ├── test_parse.py
│   └── test_utils.py
├── README.md               # Main documentation
├── pyproject.toml          # Project configuration
└── LICENSE                 # MIT License
```

## Reporting Issues

- Use GitHub Issues to report bugs or suggest features
- Provide a clear description and steps to reproduce for bugs
- Include your Python version and OS

## Questions?

Feel free to open an issue for questions or discussions about the project.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
