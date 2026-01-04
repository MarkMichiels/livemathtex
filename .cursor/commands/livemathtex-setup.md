---
description: Install and setup LiveMathTeX
---

# LiveMathTeX - Setup

Install LiveMathTeX for live LaTeX calculations in Markdown.

## Quick Install

```bash
# Clone repository
git clone https://github.com/MarkMichiels/livemathtex.git
cd livemathtex

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install
pip install -e ".[dev]"

# Verify
livemathtex --help
```

## Prerequisites

- Python 3.10 or higher
- pip installed

## Verify Installation

```bash
# Should show help
livemathtex --help

# Test with example
livemathtex process examples/simple/input.md -o /tmp/test.md
cat /tmp/test.md
```

## Usage After Setup

Use `/livemathtex` command or run directly:

```bash
livemathtex process your_file.md
```

## Troubleshooting

### "command not found: livemathtex"

Activate the virtual environment:
```bash
source .venv/bin/activate
```

### "ModuleNotFoundError"

Reinstall in the correct environment:
```bash
pip install -e .
```

### "Permission denied"

On Linux/Mac, you may need:
```bash
chmod +x .venv/bin/livemathtex
```

## More Information

- **[SETUP.md](../../docs/SETUP.md)** - Detailed installation guide
- **[README.md](../../README.md)** - Project overview
- **`/livemathtex`** - Process files after setup

