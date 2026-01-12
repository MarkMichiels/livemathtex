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

**Finding keybindings.json location:**

The `keybindings.json` file is stored in your user configuration directory. To find it:

**Method 1: Via UI (Easiest)**
1. Open keyboard shortcuts (`Ctrl+K Ctrl+S`)
2. Click the icon in the top-right corner (looks like a file with curly braces `{}`)
3. This opens `keybindings.json` directly

**Method 2: Via File System**
The file is located at:
- **Linux**: `~/.config/Cursor/User/keybindings.json` or `~/.config/Code/User/keybindings.json`
- **Mac**: `~/Library/Application Support/Cursor/User/keybindings.json` or `~/Library/Application Support/Code/User/keybindings.json`
- **Windows**: `%APPDATA%\Cursor\User\keybindings.json` or `%APPDATA%\Code\User\keybindings.json`

**Method 3: For AI Assistants (LLMs)**
If you're an AI assistant helping set this up, you can find the file by:
```bash
# Search for keybindings.json files
find ~/.config -name "keybindings.json" 2>/dev/null
# Or check common locations
ls -la ~/.config/Cursor/User/keybindings.json
ls -la ~/.config/Code/User/keybindings.json
```

Once you have `keybindings.json` open, add:

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
2. Press `F9` (or use `Ctrl+Shift+P` → "Tasks: Run Task" → "LiveMathTeX: Process Current File")
3. The file will be processed according to its directive (see "Command Behavior Overview" below)
4. Check the output file (or the same file if `output=inplace`) to see calculated results

**Note:** `livemathtex` is not a command palette command. You cannot type `livemathtex` in the command palette (`Ctrl+Shift+P`). Instead:
- Use keyboard shortcuts (`F9`, `Shift+F9`)
- Or run tasks manually: `Ctrl+Shift+P` → "Tasks: Run Task" → select a LiveMathTeX task
- Or use terminal: `livemathtex process file.md`

---

## Available Tasks

| Task | Description | Shortcut |
|------|-------------|----------|
| **Process Current File** | Calculates all `==` expressions, writes to output per directive | `F9` |
| **Clean (Smart)** | Removes computed values (smart: copies to output or clears in-place) | `Shift+F9` |

**Note:** "Process Current File (Verbose)" is the same as Process but with `--verbose` flag (creates `.lmt.json` debug file). It's not a separate task, just a variant.

---

## Command Behavior Overview

The behavior of both `F9` (process) and `Shift+F9` (clear/copy) depends on:
1. **Which file you have open** (input.md, output.md, or timestamped file)
2. **The document directive** (`<!-- livemathtex: output=... -->`)

### F9 (Process) - Calculates and Writes Results

| File Open | Directive | What Happens |
|-----------|-----------|--------------|
| `input.md` | `output=output.md` | Calculates → writes to `output.md` |
| `input.md` | `output=inplace` | Calculates → overwrites `input.md` |
| `input.md` | `output=timestamped` | Calculates → creates `input_YYYYMMDD_HHMM.md` |
| `output.md` | `output=output.md` | Recalculates → overwrites `output.md` (in-place) |
| `output.md` | `output=other.md` | Calculates → writes to `other.md` |
| `timestamped.md` | `output=...` | Recalculates → overwrites timestamped file (in-place) |

**Key:** Process always uses the directive in the current file. If directive points to the same file, it processes in-place.

### Shift+F9 (Clear/Copy) - Resets Without Calculation

| File Open | Directive | What Happens |
|-----------|-----------|--------------|
| `input.md` | `output=output.md` | Copies clean `input.md` → `output.md` (no calculation) |
| `output.md` | `output=output.md` | Clears computed values in `output.md` (in-place) |
| `output.md` | `output=other.md` | Copies `output.md` → `other.md` |

**Key:** Clear/Copy is smart:
- **Directive points to different file** → Copy operation (clean content, no calculation)
- **Directive points to same file** → Clear operation (removes `== value$` → `==$`)

### Examples

**F9 on input.md with `output=output.md`:**
```markdown
<!-- livemathtex: output=output.md -->
$x := 5$
$x ==$  ← After F9: $x == 5$ in output.md
```

**Shift+F9 on input.md with `output=output.md`:**
```markdown
<!-- livemathtex: output=output.md -->
$x := 5$
$x ==$  ← After Shift+F9: output.md gets clean copy (still $x ==$)
```

**Shift+F9 on output.md with `output=output.md`:**
```markdown
<!-- livemathtex: output=output.md -->
$x == 5$  ← After Shift+F9: $x ==$ (computed value removed)
```

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
        "args": "LiveMathTeX: Clean (Smart)",
        "when": "editorLangId == markdown"
    }
```

**Note:** The `Clean (Smart)` task automatically determines behavior based on the document directive, not the filename. It works with any filename (`input.md`, `output.md`, `calculation.md`, etc.).


| Shortcut | Action |
|----------|--------|
| `F9` | See "How F9 Works" section above for detailed behavior |
| `Shift+F9` | See "How Shift+F9 Works" section above for detailed behavior |

**Quick Reference:**
- `F9` → Processes current file according to directive (may write to different file, in-place, or timestamped)
- `Shift+F9` on `input.md` → Copies clean input to output (no calculations, adds metadata)
- `Shift+F9` on `output.md` → Clears computed values (resets for re-processing, adds metadata)

**Note:** The exact behavior depends on:
1. Which file you have open (input.md, output.md, or timestamped file)
2. The document directive (`output=inplace`, `output=output.md`, `output=timestamped`)
3. See the detailed scenario sections above for complete behavior

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

### Shortcut doesn't work / Terminal opens instead

**Problem:** Pressing Shift+F9 opens a terminal instead of running the task.

**Possible causes:**
1. Keybinding not configured in `keybindings.json`
2. Task name mismatch (check exact spelling)
3. Conflicting keybinding

**Solution:**
1. Open keyboard shortcuts: `Ctrl+K Ctrl+S` (or `Cmd+K Cmd+S` on Mac)
2. Click the icon in top-right to open `keybindings.json`
3. Add the keybindings (see "Recommended Keyboard Shortcuts" section above)
4. Verify task exists: `Ctrl+Shift+P` → "Tasks: Run Task" → should see "LiveMathTeX: Clean (Smart)"
5. Test manually: `Ctrl+Shift+P` → "Tasks: Run Task" → select the task
6. If task works manually but not with shortcut, check for conflicting keybindings

**Verify task is available:**
```bash
# In VS Code/Cursor:
Ctrl+Shift+P → "Tasks: Run Task" → Should see all LiveMathTeX tasks
```

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
