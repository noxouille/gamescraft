# README

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for Python package and environment management.

### Prerequisites

Install uv:
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Getting Started

1. Create virtual environment:
```bash
uv venv
```

2. Activate the environment:
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:
```bash
# Install from pyproject.toml
uv pip install -e .

# Or install specific packages
uv pip install package-name
```

### Common Commands

```bash
# Run Python scripts
uv run python app.py

# Install a package
uv pip install requests

# Install dev dependencies
uv pip install pytest black ruff

# List installed packages
uv pip list

# Upgrade a package
uv pip install --upgrade package-name
```

### Project Structure

- `pyproject.toml` - Project configuration and dependencies
- `.python-version` - Python version specification (3.11)
- `.venv/` - Virtual environment (auto-created by uv)