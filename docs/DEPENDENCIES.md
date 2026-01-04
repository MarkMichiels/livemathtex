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

### 4. Plotting: `matplotlib`

**Purpose:** Generate graphs and visualizations.

**Installation:**
```bash
pip install matplotlib
```

**Example for Livemathtex:**
```python
import matplotlib.pyplot as plt
import numpy as np

def generate_plot(func, x_range, title="", xlabel="x", ylabel="y"):
    x = np.linspace(x_range[0], x_range[1], 500)
    y = func(x)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, y, 'b-', linewidth=2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)

    # Save to file
    fig.savefig('plot.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

    return 'plot.png'
```

**Alternative: `plotly`**
- Interactive plots
- HTML output
- Better for web deployment

---

### 5. Expression Parsing: `lark`

**Purpose:** Build parser for Livemathtex syntax (`:=`, `=`, `=>`).

**Repository:** [lark-parser/lark](https://github.com/lark-parser/lark)

**Installation:**
```bash
pip install lark
```

**Example Grammar:**
```python
from lark import Lark

grammar = r"""
    start: statement+

    statement: definition | evaluation | expression

    definition: VARIABLE ":=" expression
    evaluation: expression "=" "?"?

    expression: term ((ADD | SUB) term)*
    term: factor ((MUL | DIV) factor)*
    factor: atom ("^" factor)?
    atom: NUMBER unit? | VARIABLE | function | "(" expression ")"

    function: FUNC_NAME "(" expression ("," expression)* ")"
    unit: UNIT_NAME ("/" UNIT_NAME)? ("^" NUMBER)?

    ADD: "+"
    SUB: "-"
    MUL: "*" | "·" | "\\cdot"
    DIV: "/" | "÷"

    VARIABLE: /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMBER: /\d+\.?\d*/
    UNIT_NAME: /[a-zA-Z]+/
    FUNC_NAME: /sin|cos|tan|log|sqrt|exp/

    %import common.WS
    %ignore WS
"""

parser = Lark(grammar, start='start')
```

**Why Lark:**
- EBNF grammar (readable)
- Generates AST automatically
- Fast (Earley or LALR)
- Good error messages

---

### 6. Markdown Processing: `markdown-it-py`

**Purpose:** Parse and render Markdown with extensions.

**Installation:**
```bash
pip install markdown-it-py mdit-py-plugins
```

**Example:**
```python
from markdown_it import MarkdownIt

md = MarkdownIt()

# Parse to tokens
tokens = md.parse("# Hello\n\n$x := 5$")

# Render to HTML
html = md.render("# Hello\n\n$x := 5$")
```

**Alternative: `mistune`**
- Faster
- More customizable
- Less plugin ecosystem

---

### 7. PDF Generation

**Option A: Pandoc (External)**

```bash
pip install pypandoc
```

```python
import pypandoc

pypandoc.convert_file(
    'output.md',
    'pdf',
    outputfile='output.pdf',
    extra_args=['--pdf-engine=xelatex']
)
```

**Requires:** pandoc + LaTeX installation

**Option B: WeasyPrint (Pure Python)**

```bash
pip install weasyprint
```

```python
from weasyprint import HTML

HTML('output.html').write_pdf('output.pdf')
```

**Pros:** No external dependencies
**Cons:** CSS-based layout, less LaTeX-native

**Recommendation:** Start with Pandoc for best LaTeX quality.

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
lark>=1.1
markdown-it-py>=3.0
mdit-py-plugins>=0.4

# Plotting
matplotlib>=3.8
numpy>=1.24

# PDF (optional, requires external pandoc)
pypandoc>=1.12

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
pdf = [
    "pypandoc>=1.12",
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
- Windows: Full support (may need additional LaTeX setup for PDF)

### External Requirements for PDF
- **pandoc** (>= 2.0)
- **LaTeX** (TeX Live, MiKTeX, or MacTeX)
- Or use WeasyPrint for PDF without LaTeX

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

### Parser Libraries

| Library | Pros | Cons |
|---------|------|------|
| `lark` | EBNF, clear, fast | Learning curve |
| `pyparsing` | Pythonic | Slower |
| `ply` | Classic lex/yacc | Verbose |
| `parsimonious` | PEG grammar | Less features |

**Choice:** `lark` - best balance of power and clarity.

---

## References

- [SymPy Documentation](https://docs.sympy.org/)
- [Pint Documentation](https://pint.readthedocs.io/)
- [Lark Documentation](https://lark-parser.readthedocs.io/)
- [latex2sympy2 GitHub](https://github.com/augustt198/latex2sympy)
- [Matplotlib Documentation](https://matplotlib.org/stable/)
- [Pandoc User Guide](https://pandoc.org/MANUAL.html)
