# Livemathtex - Dependencies & Technology Research

## Core Dependencies

### 1. LaTeX Parsing: `latex2sympy2`

**Purpose:** Parse LaTeX mathematical expressions into SymPy objects.

**Repository:** [augustt198/latex2sympy](https://github.com/augustt198/latex2sympy)

**Installation:**
```bash
pip install latex2sympy2
```

**Example:**
```python
from latex2sympy2 import latex2sympy

expr = latex2sympy(r"\frac{x^2 + 1}{x - 1}")
# Returns: (x**2 + 1)/(x - 1)
```

**Capabilities:**
- Fractions, exponents, roots
- Greek letters (α, β, γ, etc.)
- Subscripts and superscripts
- Trigonometric functions
- Matrices and vectors
- Summation and product notation
- Integrals and derivatives

**Limitations:**
- Some advanced LaTeX constructs may not parse
- Units not handled (we add this layer)

---

### 2. Symbolic Math: `sympy`

**Purpose:** Computer algebra system for symbolic mathematics.

**Installation:**
```bash
pip install sympy
```

**Key Features for Livemathtex:**

```python
from sympy import *

# Symbolic variables
x, y = symbols('x y')

# Simplification
simplify(sin(x)**2 + cos(x)**2)  # → 1

# Solving equations
solve(x**2 - 5*x + 6, x)  # → [2, 3]

# Differentiation
diff(x**3, x)  # → 3*x**2

# Integration
integrate(x**2, x)  # → x**3/3

# Numerical evaluation
expr = sqrt(2)
float(expr)  # → 1.4142135623730951
expr.evalf(50)  # 50 decimal places
```

**Why SymPy:**
- Pure Python (no external dependencies)
- Excellent LaTeX output
- Both symbolic and numeric evaluation
- Active development, large community

---

### 3. Unit Handling: `pint`

**Purpose:** Physical quantity calculations with units.

**Repository:** [hgrecco/pint](https://github.com/hgrecco/pint)

**Installation:**
```bash
pip install pint
```

**Example:**
```python
from pint import UnitRegistry

ureg = UnitRegistry()
Q_ = ureg.Quantity

# Define quantities with units
mass = 5 * ureg.kg
acceleration = 9.81 * ureg.m / ureg.s**2

# Calculate
force = mass * acceleration
print(force)  # 49.05 kg·m/s²
print(force.to('N'))  # 49.05 newton

# Unit conversion
speed = Q_(100, 'km/h')
print(speed.to('m/s'))  # 27.78 m/s

# Dimensionality checking
try:
    mass + speed  # Raises DimensionalityError
except Exception as e:
    print(f"Error: {e}")
```

**Key Features:**
- 1000+ built-in units
- Automatic dimension checking
- Unit conversion
- NumPy integration
- Custom unit definitions
- Formatting options

**Custom Units:**
```python
ureg.define('lightyear = 9.461e15 * meter')
distance = 4.2 * ureg.lightyear
print(distance.to('km'))
```

---

### 5. Math Block Detection

**Purpose:** Find `$...$` and `$$...$$` blocks in Markdown.

**Approach:** Simple regex-based detection (no full Markdown parser needed).

```python
import re

# Find inline math: $...$
INLINE_MATH = re.compile(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)')

# Find display math: $$...$$
DISPLAY_MATH = re.compile(r'\$\$(.+?)\$\$', re.DOTALL)

# Skip code blocks (don't process $ inside ```)
CODE_BLOCK = re.compile(r'```.*?```', re.DOTALL)
```

**Why no markdown-it-py:**
- Overkill for our use case
- We only need to find math blocks, not parse full Markdown
- Simpler = fewer dependencies = easier maintenance

---

## PDF Generation (Out of Scope)

PDF export is **intentionally out of scope** for Livemathtex. Use existing tools on the output:

```bash
# Pandoc (recommended)
pandoc output.md -o output.pdf

# Or WeasyPrint for HTML-based
weasyprint output.html output.pdf
```

This keeps Livemathtex focused on one thing: Markdown → Markdown with computed results.

---

## Development Dependencies

```bash
pip install pytest pytest-cov  # Testing
pip install black isort        # Formatting
pip install mypy               # Type checking
pip install ruff               # Linting
```

---

## Full Requirements

**requirements.txt:**
```
# Core
sympy>=1.12
pint>=0.23
latex2sympy2>=1.9
numpy>=1.24

# CLI
click>=8.1
rich>=13.0  # Pretty terminal output

# Watch mode
watchdog>=3.0
```

**pyproject.toml extras:**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "mypy>=1.5",
    "ruff>=0.1",
]
```

---

## Compatibility Notes

### Python Version
- Minimum: Python 3.9
- Recommended: Python 3.11+
- SymPy and Pint require modern Python

### Platform Support
- Linux: Full support
- macOS: Full support
- Windows: Full support

---

## Library Comparison

### LaTeX Parsing Options

| Library | Pros | Cons |
|---------|------|------|
| `latex2sympy2` | Direct to SymPy, maintained | Some constructs unsupported |
| `pylatexenc` | Full LaTeX tokenizer | Lower-level, more work |
| `latexcodec` | Codec only | Not a parser |

**Choice:** `latex2sympy2` - best fit for our use case.

### Unit Libraries

| Library | Pros | Cons |
|---------|------|------|
| `pint` | Most complete, NumPy compat | Slightly complex API |
| `astropy.units` | Scientific focus | Heavy dependency |
| `quantities` | Simple | Less maintained |
| `unyt` | Fast, yt integration | Less units |

**Choice:** `pint` - industry standard, most units.

### Why No Dedicated Parser (lark, pyparsing, etc.)

**We don't need a custom grammar parser because:**
- `latex2sympy2` handles LaTeX parsing → SymPy
- Operator detection (`:=`, `==`, `=>`) is simple string/regex
- Math block detection (`$...$`) is regex-based

**Keep it simple:** regex + latex2sympy2 is sufficient.

---

## References

- [SymPy Documentation](https://docs.sympy.org/)
- [Pint Documentation](https://pint.readthedocs.io/)
- [latex2sympy2 GitHub](https://github.com/augustt198/latex2sympy)
