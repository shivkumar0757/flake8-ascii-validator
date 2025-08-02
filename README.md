# flake8-ascii-validator

[![Test Status](https://github.com/shivkumar0757/flake8-ascii-validator/workflows/Test/badge.svg)](https://github.com/shivkumar0757/flake8-ascii-validator/actions)
[![PyPI version](https://badge.fury.io/py/flake8-ascii-validator.svg)](https://badge.fury.io/py/flake8-ascii-validator)
[![Python Support](https://img.shields.io/pypi/pyversions/flake8-ascii-validator.svg)](https://pypi.org/project/flake8-ascii-validator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Flake8 plugin to validate ASCII characters in Python source code.

## Installation

```bash
pip install flake8-ascii-validator
```

## Usage

```bash
flake8 your_file.py
```

Example output:
```bash
example.py:3:5: ASC001 Non-ASCII character 'é' (U+00E9) found in source code
example.py:4:15: ASC002 Non-ASCII character 'ø' (U+00F8) found in string literal
example.py:5:10: ASC003 Non-ASCII character 'ñ' (U+00F1) found in comment
```

## Error Codes

| Code   | Description |
|--------|-------------|
| ASC001 | Non-ASCII character found in source code (variable names, function names, etc.) |
| ASC002 | Non-ASCII character found in string literal |
| ASC003 | Non-ASCII character found in comment |

## Configuration

Ignore specific error codes:
```bash
flake8 --extend-ignore=ASC002
```

Or in your configuration file:
```ini
[flake8]
extend-ignore = ASC002
```

## Examples

Valid ASCII code:
```python
def hello_world():
    message = "Hello, World!"
    return message
```

Invalid non-ASCII code:
```python
def función():  # ASC001: 'ó' in function name
    variável = "café"  # ASC001: 'á' in variable, ASC002: 'é' in string
    # Commentário  # ASC003: 'á' in comment
    return variável
```

## Why Use This Plugin?

- **Team Consistency**: Ensure code works across different environments
- **Legacy Compatibility**: Support systems that don't handle Unicode well
- **Debugging**: ASCII characters are easier to search and debug
- **Code Standards**: Enforce ASCII-only policies in your codebase

## Requirements

- Python 3.7+
- Flake8 3.0.0+

## License

MIT License