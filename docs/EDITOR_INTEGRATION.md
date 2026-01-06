# LiveMathTeX - Editor Integration

Process Markdown files with a keyboard shortcut directly from VS Code or Cursor.

---

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Edit Markdown file                                        │
│  ↓                                                         │
│  Press F9 (same as Mathcad/SMath)                          │
│  ↓                                                         │
│  LiveMathTeX processes calculations                        │
│  ↓                                                         │
│  File updated with results                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Setup (2 Minutes)

### Prerequisites

1. **LiveMathTeX CLI installed and in PATH**
   ```bash
   # Verify installation
   livemathtex --help
   ```

   If not installed, see [SETUP.md](SETUP.md).

2. **LiveMathTeX repository in your workspace**
   The task definitions are in `.vscode/tasks.json` in this repository.

### Step 1: Add Keyboard Shortcut

Open keyboard shortcuts:
- **VS Code/Cursor**: `Ctrl+K Ctrl+S` (or `Cmd+K Cmd+S` on Mac)
- Or: File → Preferences → Keyboard Shortcuts

Click the icon in the top-right to open `keybindings.json` and add:

```json
[
    {
        "key": "f9",
        "command": "workbench.action.tasks.runTask",
        "args": "LiveMathTeX: Process Current File",
        "when": "editorLangId == markdown"
    }
]
```

> **Why F9?** This is the standard "recalculate" shortcut in Mathcad and SMath Studio.

### Step 2: Test It

1. Open any Markdown file with LiveMathTeX syntax
2. Press `F9`
3. Check the terminal panel for output

---

## Available Tasks

| Task | Description | Use Case |
|------|-------------|----------|
| **Process Current File** | Updates file in place | Normal workflow |
| **Process Current File (Verbose)** | Shows debug info, creates `.lmt.json` | Debugging |

### Run Tasks Manually

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Tasks: Run Task"
3. Select the desired LiveMathTeX task

---

## Recommended Keyboard Shortcuts

Add these to your `keybindings.json`:

```json
[
    {
        "key": "f9",
        "command": "workbench.action.tasks.runTask",
        "args": "LiveMathTeX: Process Current File",
        "when": "editorLangId == markdown"
    },
    {
        "key": "shift+f9",
        "command": "workbench.action.tasks.runTask",
        "args": "LiveMathTeX: Process Current File (Verbose)",
        "when": "editorLangId == markdown"
    }
]
```

| Shortcut | Action |
|----------|--------|
| `F9` | Process file (same as Mathcad/SMath) |
| `Shift+F9` | Process with debug output |

---

## Multi-Root Workspace Setup

If you have a multi-root workspace (multiple folders), the tasks from LiveMathTeX are automatically available to all folders.

**Example workspace:**
```
My Workspace
├── proviron/
├── mark-private/
├── livemathtex/        ← Tasks defined here
└── other-projects/
```

The keyboard shortcut works on Markdown files in **any** of these folders.

### Verify Tasks Are Available

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Tasks: Run Task"
3. You should see "LiveMathTeX: Process Current File" in the list

---

## Single Repository Setup

If livemathtex is **not** in your workspace, copy the tasks to your project:

### Option A: Copy tasks.json

```bash
# From your project root
mkdir -p .vscode
cp /path/to/livemathtex/.vscode/tasks.json .vscode/
```

### Option B: Symlink (Linux/Mac)

```bash
mkdir -p .vscode
ln -s /path/to/livemathtex/.vscode/tasks.json .vscode/tasks.json
```

### Option C: Merge with existing tasks

If you already have a `tasks.json`, add the LiveMathTeX tasks to the `"tasks"` array.

---

## Troubleshooting

### "livemathtex: command not found"

The virtual environment is not activated or livemathtex is not in PATH.

**Solution 1: Activate venv first**
```bash
source /path/to/livemathtex/.venv/bin/activate
```

**Solution 2: Install globally in your main venv**
```bash
# If you have a main project venv
source /path/to/your/project/venv/bin/activate
pip install -e /path/to/livemathtex
```

**Solution 3: Use full path in task**

Edit `.vscode/tasks.json`:
```json
{
    "command": "/home/youruser/Repositories/livemathtex/.venv/bin/livemathtex"
}
```

### Task not appearing in list

1. Ensure livemathtex repository is in your workspace
2. Reload window (`Ctrl+Shift+P` → "Reload Window")
3. Check `.vscode/tasks.json` exists and is valid JSON

### Shortcut doesn't work

1. Check for conflicting shortcuts (`Ctrl+K Ctrl+S` → search for your shortcut)
2. Ensure `"when": "editorLangId == markdown"` is correct
3. Verify the task name matches exactly: `"LiveMathTeX: Process Current File"`

### File not updating

1. Check terminal output for errors
2. Run verbose task to see debug info
3. Ensure file has valid LiveMathTeX syntax (`:=` and `==`)

---

## Advanced: Auto-Process on Save

**Coming in future version.** For now, use the keyboard shortcut workflow.

Workaround using VS Code's "Run on Save" extension:

1. Install "Run on Save" extension
2. Add to `settings.json`:
   ```json
   {
       "emeraldwalk.runonsave": {
           "commands": [
               {
                   "match": "\\.md$",
                   "cmd": "livemathtex process ${file}"
               }
           ]
       }
   }
   ```

**Note:** This runs on ALL markdown files. Use with caution.

---

## Example Workflow

```markdown
# My Calculation

Define values:
$m := 5 \text{ kg}$
$a := 9.81 \text{ m/s}^2$

Calculate force:
$F := m \cdot a ==$
```

1. Save file
2. Press `F9`
3. Result appears:

```markdown
# My Calculation

Define values:
$m := 5 \text{ kg}$
$a := 9.81 \text{ m/s}^2$

Calculate force:
$F := m \cdot a == 49.05 \text{ N}$
```

---

## See Also

- [SETUP.md](SETUP.md) - Installation guide
- [USAGE.md](USAGE.md) - Syntax reference
- [Examples](../examples/) - Working examples
