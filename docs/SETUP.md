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

**Quick setup for keyboard shortcut processing:**

1. Ensure livemathtex is in your workspace (or copy `.vscode/tasks.json`)
2. Add keybinding to your `keybindings.json`:
   ```json
   {
       "key": "f9",
       "command": "workbench.action.tasks.runTask",
       "args": "LiveMathTeX: Process Current File",
       "when": "editorLangId == markdown"
   }
   ```
3. Press `F9` on any Markdown file to process (same as Mathcad/SMath)

**Workflow:**
1. Edit `.md` file with LiveMathTeX syntax
2. Press `F9` (or run task manually)
3. File updates with calculated results
4. Preview with "Markdown Preview Enhanced" extension

**Full guide:** See **[EDITOR_INTEGRATION.md](EDITOR_INTEGRATION.md)** for:
- All available tasks
- Multi-root workspace setup
- Troubleshooting
- Advanced configuration

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

---

## Development Setup

### Reference Repositories (Important!)

For development and debugging, clone these reference repositories locally.
This has proven **extremely valuable** for understanding and fixing issues.

```bash
cd ~/Repositories  # or your preferred location

# Already required (our fork with bug fix)
git clone https://github.com/MarkMichiels/latex2sympy.git latex2sympy-fork

# Recommended for investigation
git clone --depth 1 https://github.com/sympy/sympy.git sympy
git clone --depth 1 https://github.com/cortex-js/compute-engine.git cortex-compute-engine
```

**Why local clones matter:**
- 🔍 Investigate bugs at the source (not just workarounds)
- 📚 Learn from well-designed architecture (Cortex-JS patterns)
- 🐛 Debug issues by reading actual implementations
- 💡 Find solutions that aren't in documentation

**Useful locations in these repos:**

| Repository | Key Paths | Useful For |
|------------|-----------|------------|
| **sympy** | `sympy/physics/units/` | Unit system, conversions |
| **sympy** | `sympy/parsing/latex/` | Alternative LaTeX parsing |
| **cortex-compute-engine** | `src/compute-engine/latex-syntax/` | Symbol normalization |
| **latex2sympy-fork** | `PS.g4` | ANTLR grammar (our fix) |

**Example investigation workflow:**
```bash
# Problem: Units not converting correctly
# Step 1: Check SymPy's unit definitions
grep -r "kilowatt" sympy/sympy/physics/units/

# Problem: Symbol not parsing
# Step 2: Check latex2sympy grammar
less latex2sympy-fork/PS.g4

# Problem: Understanding MathJSON
# Step 3: Look at Cortex-JS patterns
cat cortex-compute-engine/src/compute-engine/latex-syntax/parse-symbol.ts
```

---

## Next Steps

- **[USAGE.md](USAGE.md)** - Learn the syntax
- **[Examples](../examples/)** - See working examples
- **`/livemathtex`** - Process your first file
