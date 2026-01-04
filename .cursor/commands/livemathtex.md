---
description: Install and run Livemathtex with detailed guide
---

# Livemathtex: The Comprehensive Guide

**Livemathtex** turns your Markdown files into live calculation notebooks. It reads standard LaTeX math blocks, executes the math using a powerful Python engine (SymPy), and writes the results back into your document.

## 1. Installation & Setup

### Prerequisites
- Python 3.10 or higher
- `pip` installed

### Step-by-Step Installation

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone https://github.com/MarkMichiels/livemathtex.git
    cd livemathtex
    ```

2.  **Create a Virtual Environment (Recommended)**:
    It's best practice to keep dependencies isolated.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the Package**:
    Install in "editable" mode (`-e`) so changes to the code are immediately reflected, including development dependencies (`[dev]`).
    ```bash
    pip install -e ".[dev]"
    ```

4.  **Verify Installation**:
    Check if the CLI is accessible.
    ```bash
    python3 -m livemathtex.cli --help
    ```

---

## 2. The Core Syntax

Livemathtex introduces three simple operators inside LaTeX math blocks (`$...$` or `$$...$$`):

| Operator | Name | Description | Example |
| :--- | :--- | :--- | :--- |
| `:=` | **Assignment** | Defines a variable or function. | `$x := 10$` |
| `==` | **Evaluation** | Calculates and displays a numeric result. | `$x + 5 ==$` |
| `=>` | **Symbolic** | Displays the symbolic manipulation result. | `$x + x =>$` |

---

## 3. Features & Examples

### A. Basic Arithmetic
Define variables just like in math. Variables persist throughout the document output.

```markdown
Let's define a width and a height:
$w := 50$
$h := 20$
The area is:
$A := w \cdot h ==$
```
*(Result: `$A := w \cdot h == 1000$`)*

### B. Scientific Units (SI)
You can use units directly. The system understands SI units (kg, m, s, N, etc.).
**Tip**: It is recommended to wrap units in `\text{...}` for clear formatting, but standard text is also parsed.

```markdown
$mass := 75 \text{kg}$
$gravity := 9.81 \text{m}/\text{s}^2$
$Force := mass \cdot gravity ==$
```
*(Result: `$Force := mass \cdot gravity == 735.75 \text{N}$`)*

### C. Custom Functions
Define reusable mathematical functions.

```markdown
$f(x) := x^2 + 2x + 1$
Calculate for x=5:
$result := f(5) ==$
```
*(Result: `$result := f(5) == 36$`)*

### D. Symbolic Math
Derived formulas can be shown symbolically without inserting numbers.

```markdown
$y := x^3$
$dydx := \frac{d}{dx} y =>$  *(Future feature: differentiation syntax)*
Simple symbolic reduction:
$expr := a + a + b$
$expr =>$
```
*(Result: `$expr => 2a + b$`)*

---

## 4. How to Run

### The Process Command
The primary command is `process`. It reads your file, computes values, and updates the file (or a new output file).

**Syntax:**
```bash
python3 -m livemathtex.cli process [INPUT_FILE] [OPTIONS]
```

**Options:**
- `-o, --output [FILE]`: Write output to a specific file instead of overwriting the input.

**Example Workflow:**
1.  Create a file `calc.md`.
2.  Write your formulas.
3.  Run:
    ```bash
    python3 -m livemathtex.cli process calc.md
    ```
4.  Open `calc.md` to see the results filled in!

---

## 5. Troubleshooting / FAQ

-   **"Error: Undefined variable"**: Ensure you defined the variable (`:=`) *before* you tried to use it in the document file. The parser reads from top to bottom.
-   **"Failed to parse LaTeX"**: Check your LaTeX syntax. Ensure braces `{}` are balanced. Unbalanced braces are a common issue.
-   **Units not simplifying?**: Sometimes `kg * m / s^2` stays as is instead of becoming `N`. This is expected behavior in the current MVP; explicit unit conversion syntax is planned for Phase 3.
-   **Function arguments**: When defining `$f(x) := x + 1$`, the `x` is local to the function. It doesn't affect a global `x` variable.

---

## 6. Developer Notes (Running Tests)

If you are modifying the code:
```bash
# Run all tests
pytest

# Run a specific test file
python3 test_units.py
```
