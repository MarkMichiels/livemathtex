# External Library Dependencies

This project uses forked versions of external libraries with bug fixes.

## latex2sympy

**Fork:** [MarkMichiels/latex2sympy](https://github.com/MarkMichiels/latex2sympy)  
**Original:** [OrangeX4/latex2sympy](https://github.com/OrangeX4/latex2sympy)

### Bug Fix: DIFFERENTIAL rule capturing `\cdot`

**Problem:** The ANTLR grammar's `DIFFERENTIAL` rule was too greedy:

```antlr
# OLD (buggy)
DIFFERENTIAL: 'd' WS_CHAR*? ([a-zA-Z] | '\\' [a-zA-Z]+);
```

This matched `d \cdot x` as a differential because `'\\' [a-zA-Z]+` captured `\cdot`.

**Example:**
```
Input:  f_d \cdot x
Before: tokens = f, _, d\cdot, x  (wrong - \cdot captured!)
After:  tokens = f, _, d, \cdot, x (correct)
```

**Fix:** Restrict the suffix to only match Greek letter commands.

### Installation

The fork is automatically installed via `pyproject.toml`:

```bash
pip install -e .
```

### Local Development

If you need to modify the fork:

```bash
# Clone the fork
git clone https://github.com/MarkMichiels/latex2sympy.git

# Make changes to PS.g4, then regenerate parser:
cd latex2sympy
java -jar antlr-4.7.2-complete.jar -Dlanguage=Python3 -o gen PS.g4

# Commit and push
git add -A && git commit -m "your message" && git push
```
