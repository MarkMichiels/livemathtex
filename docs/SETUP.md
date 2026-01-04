# LiveMathTeX - Setup Guide

Complete installation and configuration guide for LiveMathTeX.

---

## Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.10+ | `python3 --version` |
| pip | Latest | `pip --version` |
| Git | Any | `git --version` |

---

## Installation Methods

### Method 1: From Source (Recommended for Development)

```bash
# 1. Clone the repository
git clone https://github.com/MarkMichiels/livemathtex.git
cd livemathtex

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate          # Linux/Mac
# .venv\Scripts\activate           # Windows (cmd)
# .venv\Scripts\Activate.ps1       # Windows (PowerShell)

# 4. Install with development dependencies
pip install -e ".[dev]"

# 5. Verify installation
livemathtex --help
```

### Method 2: From PyPI (When Published)

```bash
pip install livemathtex
```

---

## Configuration

### Project Configuration (`.livemathtex.toml`)

Create in your project directory:

```toml
# .livemathtex.toml
digits = 4              # Decimal precision
scientific = false      # Use scientific notation
timeout = 5             # Max seconds per expression

[units]
system = "SI"           # Unit system (SI or imperial)
```

### Document Directives

Override settings per document:

```markdown
<!-- livemathtex: digits=2 -->

$result := 1/3 ==$
```

---

## IDE Integration

### VS Code / Cursor

1. Install "Markdown Preview Enhanced" extension
2. LiveMathTeX processes files, MPE renders LaTeX

**Workflow:**
1. Edit `.md` file
2. Run `livemathtex process file.md`
3. Preview updates automatically

### Watch Mode (Future)

```bash
livemathtex watch input.md  # Auto-process on save
```

---

## Virtual Environment Tips

### Always Activate Before Use

```bash
cd /path/to/livemathtex
source .venv/bin/activate
```

### Check if Activated

```bash
which livemathtex
# Should show: /path/to/livemathtex/.venv/bin/livemathtex
```

### Deactivate When Done

```bash
deactivate
```

---

## Troubleshooting

### "command not found: livemathtex"

**Cause:** Virtual environment not activated

**Solution:**
```bash
source .venv/bin/activate
```

### "ModuleNotFoundError: No module named 'livemathtex'"

**Cause:** Package not installed in current environment

**Solution:**
```bash
pip install -e .
```

### "Permission denied" on Linux/Mac

**Solution:**
```bash
chmod +x .venv/bin/livemathtex
```

### LaTeX parsing errors

**Common causes:**
- Unbalanced braces `{}`
- Missing `$` delimiters
- Unsupported LaTeX commands

**Solution:** Check [USAGE.md](USAGE.md) for supported syntax.

---

## Updating

```bash
cd /path/to/livemathtex
git pull
pip install -e ".[dev]"
```

---

## Uninstalling

```bash
pip uninstall livemathtex
rm -rf /path/to/livemathtex
```

---

## Next Steps

- **[USAGE.md](USAGE.md)** - Learn the syntax
- **[Examples](../examples/)** - See working examples
- **`/livemathtex`** - Process your first file
