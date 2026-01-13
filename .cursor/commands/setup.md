---
description: Install and setup LiveMathTeX
---

# LiveMathTeX — Setup (AI Command)

This command helps a first-time AI assistant get LiveMathTeX installed and verified, so it can safely process Markdown calculation documents.

## Quick install (from source)

```bash
# If you don't already have the repo locally:
git clone https://github.com/MarkMichiels/livemathtex.git
cd livemathtex

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\\Scripts\\activate  # Windows (cmd)

# Install
pip install -e ".[dev]"

# Verify
livemathtex --help
```

## Prerequisites

- Python 3.10+
- pip

## Verify Installation

```bash
# Should show help
livemathtex --help

# Test with an example (generate IR JSON + inspect it)
#
# Linux/Mac:
livemathtex process examples/simple/input.md -o /tmp/livemathtex_test.md --verbose
livemathtex inspect examples/simple/input.lmt.json
cat /tmp/livemathtex_test.md
#
# Windows (use a relative output path instead of /tmp):
# livemathtex process examples/simple/input.md -o output_test.md --verbose
# livemathtex inspect examples/simple/input.lmt.json
```

## Usage After Setup

Use `/build-calculations` or `/debug-calculations` commands, or run directly:

```bash
livemathtex process your_file.md
```

**Output note:** If you don't pass `-o/--output`, the output path comes from the document/config `output` setting (default is `"timestamped"`, which creates `your_file_YYYYMMDD_HHMM.md` next to the input file). Use `<!-- livemathtex: output=inplace -->` (or `-o your_file.md`) for in-place updates.

## VS Code / Cursor: Recalculate with F9 (recommended)

This repo ships VS Code/Cursor tasks in `.vscode/tasks.json`, so you can “recalculate” the current Markdown file with a single keypress.

1. Ensure the `livemathtex/` folder is part of your workspace (multi-root is fine).
2. Add this keybinding to your `keybindings.json`:

```json
{
    "key": "f9",
    "command": "workbench.action.tasks.runTask",
    "args": "LiveMathTeX: Process Current File",
    "when": "editorLangId == markdown"
}
```

Optional (debug): bind verbose processing to `Shift+F9`:

```json
{
    "key": "shift+f9",
    "command": "workbench.action.tasks.runTask",
    "args": "LiveMathTeX: Process Current File (Verbose)",
    "when": "editorLangId == markdown"
}
```

**Output mode note:** the F9 task runs `livemathtex process ${file}`. It will follow the document/config `output` setting. For true in-place “recalculate”, add `<!-- livemathtex: output=inplace -->` to the document.

Full guide: **[EDITOR_INTEGRATION.md](../../docs/EDITOR_INTEGRATION.md)**.

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
- **`/livemathtex`** - Command reference and overview
- **`/build-calculations`** - Iterative build workflow
- **`/debug-calculations`** - Debug workflow with issue detection
