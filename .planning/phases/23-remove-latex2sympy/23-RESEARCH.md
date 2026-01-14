# Phase 23: Remove latex2sympy Dependency - Research

**Researched:** 2026-01-14
**Domain:** LaTeX math parsing → Pint evaluation pipeline
**Confidence:** HIGH

<research_summary>
## Summary

Investigated alternatives to latex2sympy for parsing LaTeX math expressions. The current architecture uses latex2sympy as an intermediate step to convert LaTeX → SymPy AST → Pint evaluation. This causes fundamental issues:

1. **Implicit multiplication:** `PPE` → `P*P*E` (latex2sympy's design decision)
2. **Special symbol handling:** `E` in subscripts conflicts with Euler's number
3. **Unit splitting:** `kg` → `k*g`, `MWh` → `M*W*h`
4. **Parsing failures:** Some valid LaTeX like `E_{26}` fails entirely

**Key insight:** LiveMathTeX doesn't need full symbolic algebra. We only need:
- Variable/function name recognition (with subscripts, superscripts)
- Basic arithmetic operators
- Number parsing
- Unit identification
- Function calls

This is a **much simpler parsing problem** than general LaTeX math, and can be solved with a custom tokenizer + expression parser.

**Primary recommendation:** Build a custom LaTeX math tokenizer + recursive descent parser. Parse directly to a simple expression tree, then evaluate with Pint. Eliminate SymPy from the evaluation path entirely.
</research_summary>

<standard_stack>
## Standard Stack

### Current Architecture (Problems)
```
LaTeX → latex2sympy → SymPy AST → evaluate_sympy_ast_with_pint() → Result
```

Problems with latex2sympy (v1.9.1):
- Based on ANTLR grammar designed for symbolic algebra, not calculations
- Implicit multiplication is intentional (for math like `xy` meaning `x*y`)
- `E` is hardcoded as Euler's number
- Cannot be easily configured or extended

### Proposed Architecture
```
LaTeX → Custom Tokenizer → Expression Tree → Pint Evaluation → Result
```

### Core Libraries to Keep
| Library | Version | Purpose | Why Keep |
|---------|---------|---------|----------|
| Pint | 0.23+ | Unit calculations | Already used, works well |
| pylatexenc | 2.10+ | LaTeX entity handling | Already used for `\text{}` cleanup |
| re (stdlib) | - | Regex tokenization | Standard approach |

### Libraries to Remove
| Library | Version | Why Remove |
|---------|---------|------------|
| latex2sympy2 | 1.9.1 | Root cause of parsing issues |
| sympy | 1.12+ | Only needed for latex2sympy, not for Pint evaluation |

### Alternatives Considered

| Approach | Library | Why Not |
|----------|---------|---------|
| Different LaTeX parser | antlr4_tex2sym | Same architecture, same problems |
| SymPy's Lark parser | sympy.parsing.latex | Still targets symbolic algebra |
| Hugging Face extended | latex2sympy2_extended | Same core issues |
| Pint's string parser | Built-in | Only handles units, not expressions |

**Conclusion:** No existing library fits our use case. Custom parser is the right approach.
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Recommended Project Structure
```
src/livemathtex/
├── parser/
│   ├── lexer.py           # Existing: document structure
│   ├── markdown_parser.py  # Existing: markdown-it integration
│   ├── calculation_parser.py # Existing: operation detection
│   └── expression_parser.py  # NEW: LaTeX expression → AST
├── engine/
│   ├── evaluator.py        # MODIFY: use new parser
│   ├── pint_backend.py     # KEEP: Pint evaluation
│   ├── symbols.py          # KEEP: symbol table
│   └── token_classifier.py # REMOVE: no longer needed
```

### Pattern 1: Tokenizer + Recursive Descent Parser
**What:** Two-pass parsing: tokenize LaTeX, then parse tokens into expression tree
**When to use:** When grammar is simple and well-defined (our case)

**Tokenizer output:**
```python
@dataclass
class Token:
    type: TokenType  # NUMBER, VARIABLE, OPERATOR, UNIT, LPAREN, RPAREN, etc.
    value: str       # Raw string value
    span: Span       # Position in source

class TokenType(Enum):
    NUMBER = "number"      # 3.14, 1e-6
    VARIABLE = "variable"  # E_{26}, PPE_{eff}, R^2
    OPERATOR = "operator"  # +, -, *, /, ^, \cdot, \times
    UNIT = "unit"          # \text{kg}, \mathrm{MWh}
    FRAC = "frac"          # \frac
    LPAREN = "lparen"      # (, \left(
    RPAREN = "rparen"      # ), \right)
    LBRACE = "lbrace"      # {
    RBRACE = "rbrace"      # }
    FUNCTION = "function"  # f_{name}(...)
```

**Expression tree:**
```python
@dataclass
class ExprNode:
    pass

@dataclass
class NumberNode(ExprNode):
    value: float

@dataclass
class VariableNode(ExprNode):
    name: str  # Normalized: "E_26", "PPE_eff", "R_2"

@dataclass
class BinaryOpNode(ExprNode):
    op: str  # "+", "-", "*", "/", "^"
    left: ExprNode
    right: ExprNode

@dataclass
class UnitNode(ExprNode):
    expr: ExprNode
    unit: str  # "kg", "MWh", etc.

@dataclass
class FunctionCallNode(ExprNode):
    name: str
    args: List[ExprNode]
```

### Pattern 2: Grammar-Driven Tokenization
**What:** Define token patterns in priority order, match greedily
**When to use:** When tokens can be ambiguous (our case: `kg` vs `k*g`)

```python
TOKEN_PATTERNS = [
    # Units FIRST (greedy match prevents splitting)
    (r'\\text\{([^}]+)\}', TokenType.UNIT),
    (r'\\mathrm\{([^}]+)\}', TokenType.UNIT),

    # Numbers
    (r'\d+\.?\d*(?:[eE][+-]?\d+)?', TokenType.NUMBER),

    # Variables with subscripts/superscripts (BEFORE single letters)
    (r'[A-Za-z]+_\{[^}]+\}', TokenType.VARIABLE),
    (r'[A-Za-z]+\^[^{}\s]+', TokenType.VARIABLE),
    (r'[A-Za-z]+_[A-Za-z0-9]+', TokenType.VARIABLE),

    # Greek letters
    (r'\\alpha|\\beta|...', TokenType.VARIABLE),

    # Single letters (LAST - fallback)
    (r'[A-Za-z]', TokenType.VARIABLE),

    # Operators
    (r'\\cdot|\\times', TokenType.OPERATOR),
    (r'[+\-*/^]', TokenType.OPERATOR),

    # Fractions
    (r'\\frac', TokenType.FRAC),

    # Parentheses
    (r'\\left\(|\(', TokenType.LPAREN),
    (r'\\right\)|\)', TokenType.RPAREN),
]
```

### Pattern 3: Direct Pint Evaluation
**What:** Walk expression tree and evaluate with Pint directly
**When to use:** When result needs units (our case)

```python
def evaluate_expr(node: ExprNode, symbols: Dict[str, pint.Quantity]) -> pint.Quantity:
    if isinstance(node, NumberNode):
        return ureg.Quantity(node.value, 'dimensionless')

    if isinstance(node, VariableNode):
        return symbols[node.name]

    if isinstance(node, BinaryOpNode):
        left = evaluate_expr(node.left, symbols)
        right = evaluate_expr(node.right, symbols)
        if node.op == '+': return left + right
        if node.op == '-': return left - right
        if node.op == '*': return left * right
        if node.op == '/': return left / right
        if node.op == '^': return left ** right.magnitude

    if isinstance(node, UnitNode):
        value = evaluate_expr(node.expr, symbols)
        return value.to(node.unit)

    if isinstance(node, FunctionCallNode):
        func = symbols[node.name]  # Lambda stored in symbol table
        args = [evaluate_expr(arg, symbols) for arg in node.args]
        return func(*args)
```

### Anti-Patterns to Avoid
- **Trying to extend latex2sympy:** Too deeply integrated, not designed for our use case
- **Using SymPy for evaluation:** Adds complexity, we only need arithmetic
- **Implicit multiplication:** The source of all our problems - be explicit
- **Single-letter priority:** Always match longest token first
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Unit conversion | Custom conversion tables | Pint | 1000+ units, prefixes, conversions |
| LaTeX entity handling | Custom escape handling | pylatexenc | Unicode, special chars |
| Number formatting | Custom format strings | Pint/Python | Scientific notation, precision |
| Markdown parsing | Custom regex | markdown-it-py | Edge cases, extensions |

**Key insight:** We only need to hand-roll the **expression tokenizer** and **recursive descent parser**. Everything else (units, formatting, markdown) has excellent existing solutions.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Greedy Token Matching Order
**What goes wrong:** `kg` tokenizes as `k`, `g` instead of `kg`
**Why it happens:** Single-letter patterns match before multi-letter units
**How to avoid:** Order patterns by specificity - most specific first
**Warning signs:** Unit values are way off (factor of 1000, etc.)

### Pitfall 2: Subscript/Superscript Complexity
**What goes wrong:** `E_{26}` parses incorrectly
**Why it happens:** LaTeX subscripts have nested braces
**How to avoid:** Use proper brace matching, not regex for complex cases
**Warning signs:** Parser errors on valid LaTeX

### Pitfall 3: Operator Precedence
**What goes wrong:** `a + b * c` evaluates as `(a + b) * c`
**Why it happens:** Recursive descent without precedence handling
**How to avoid:** Use Pratt parsing or explicit precedence levels
**Warning signs:** Math results are wrong in specific patterns

### Pitfall 4: Whitespace Handling
**What goes wrong:** `10 kg` vs `10kg` behave differently
**Why it happens:** Inconsistent whitespace normalization
**How to avoid:** Strip/normalize whitespace in tokenizer
**Warning signs:** Some expressions work, equivalent ones don't

### Pitfall 5: Implicit Multiplication Creep
**What goes wrong:** Accidentally reintroduce implicit multiplication
**Why it happens:** Convenience shortcuts in parser
**How to avoid:** Require explicit `\cdot` or `*` for multiplication
**Warning signs:** Multi-letter variables work but single letters don't
</common_pitfalls>

<code_examples>
## Code Examples

### Tokenizer Skeleton
```python
# src/livemathtex/parser/expression_tokenizer.py
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Iterator

class TokenType(Enum):
    NUMBER = "number"
    VARIABLE = "variable"
    UNIT = "unit"
    OPERATOR = "operator"
    FRAC = "frac"
    LPAREN = "lparen"
    RPAREN = "rparen"
    LBRACE = "lbrace"
    RBRACE = "rbrace"
    EOF = "eof"

@dataclass
class Token:
    type: TokenType
    value: str
    start: int
    end: int

class ExpressionTokenizer:
    """Tokenize LaTeX math expressions for LiveMathTeX."""

    # Ordered by priority - most specific first
    PATTERNS = [
        # Units in \text{} or \mathrm{} - HIGHEST PRIORITY
        (r'\\text\{([^}]+)\}', TokenType.UNIT),
        (r'\\mathrm\{([^}]+)\}', TokenType.UNIT),

        # Numbers (including scientific notation)
        (r'\d+\.?\d*(?:[eE][+-]?\d+)?', TokenType.NUMBER),

        # Variables with subscripts/superscripts
        (r'[A-Za-z]+_\{[^}]+\}', TokenType.VARIABLE),
        (r'[A-Za-z]+\^\{[^}]+\}', TokenType.VARIABLE),
        (r'[A-Za-z]+_[A-Za-z0-9]+', TokenType.VARIABLE),
        (r'[A-Za-z]+\^[A-Za-z0-9]+', TokenType.VARIABLE),

        # Greek letters
        (r'\\(?:alpha|beta|gamma|delta|epsilon|mu|pi|sigma|omega)', TokenType.VARIABLE),

        # Fraction command
        (r'\\frac', TokenType.FRAC),

        # Operators
        (r'\\cdot|\\times', TokenType.OPERATOR),
        (r'[+\-*/^]', TokenType.OPERATOR),

        # Parentheses
        (r'\\left\(|\(', TokenType.LPAREN),
        (r'\\right\)|\)', TokenType.RPAREN),

        # Braces
        (r'\{', TokenType.LBRACE),
        (r'\}', TokenType.RBRACE),

        # Single letters LAST (fallback)
        (r'[A-Za-z]', TokenType.VARIABLE),

        # Whitespace (skip)
        (r'\s+', None),
        (r'\\\\', None),  # Line breaks
        (r'\\ ', None),   # LaTeX spaces
    ]

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self._compiled = [(re.compile(p), t) for p, t in self.PATTERNS]

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.pos < len(self.text):
            token = self._next_token()
            if token:
                tokens.append(token)
        tokens.append(Token(TokenType.EOF, '', self.pos, self.pos))
        return tokens

    def _next_token(self) -> Token | None:
        for pattern, token_type in self._compiled:
            match = pattern.match(self.text, self.pos)
            if match:
                start, end = match.start(), match.end()
                value = match.group(1) if match.lastindex else match.group(0)
                self.pos = end
                if token_type is None:
                    return None  # Skip whitespace
                return Token(token_type, value, start, end)

        # Unknown character - skip and continue
        self.pos += 1
        return None
```

### Recursive Descent Parser Skeleton
```python
# src/livemathtex/parser/expression_parser.py
from dataclasses import dataclass
from typing import List

@dataclass
class ExprNode:
    pass

@dataclass
class NumberNode(ExprNode):
    value: float

@dataclass
class VariableNode(ExprNode):
    name: str  # Normalized name

@dataclass
class BinaryOpNode(ExprNode):
    op: str
    left: ExprNode
    right: ExprNode

@dataclass
class UnaryOpNode(ExprNode):
    op: str
    operand: ExprNode

@dataclass
class UnitNode(ExprNode):
    value: ExprNode
    unit: str

class ExpressionParser:
    """Parse tokens into expression tree."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> ExprNode:
        return self._expression()

    def _expression(self) -> ExprNode:
        return self._additive()

    def _additive(self) -> ExprNode:
        left = self._multiplicative()
        while self._match('+', '-'):
            op = self._previous().value
            right = self._multiplicative()
            left = BinaryOpNode(op, left, right)
        return left

    def _multiplicative(self) -> ExprNode:
        left = self._power()
        while self._match('*', '/', '\\cdot', '\\times'):
            op = '*' if self._previous().value in ('\\cdot', '\\times') else self._previous().value
            right = self._power()
            left = BinaryOpNode(op, left, right)
        return left

    def _power(self) -> ExprNode:
        left = self._unary()
        if self._match('^'):
            right = self._power()  # Right associative
            left = BinaryOpNode('^', left, right)
        return left

    def _unary(self) -> ExprNode:
        if self._match('-'):
            return UnaryOpNode('-', self._unary())
        return self._primary()

    def _primary(self) -> ExprNode:
        if self._check(TokenType.NUMBER):
            return NumberNode(float(self._advance().value))

        if self._check(TokenType.VARIABLE):
            name = self._normalize_name(self._advance().value)
            return VariableNode(name)

        if self._check(TokenType.FRAC):
            return self._parse_fraction()

        if self._check(TokenType.LPAREN):
            self._advance()
            expr = self._expression()
            self._expect(TokenType.RPAREN)
            return expr

        raise ParseError(f"Unexpected token: {self._current()}")

    def _normalize_name(self, latex_name: str) -> str:
        """Convert LaTeX name to normalized form."""
        # E_{26} → E_26
        # PPE_{eff} → PPE_eff
        # R^2 → R_2 (or keep as R^2)
        return latex_name.replace('{', '').replace('}', '')
```

### Pint Evaluator
```python
# Integration with pint_backend.py
def evaluate_expression_tree(
    node: ExprNode,
    symbols: Dict[str, pint.Quantity],
    ureg: pint.UnitRegistry
) -> pint.Quantity:
    """Evaluate expression tree using Pint."""

    if isinstance(node, NumberNode):
        return ureg.Quantity(node.value, 'dimensionless')

    if isinstance(node, VariableNode):
        if node.name not in symbols:
            raise UndefinedVariableError(f"Undefined variable: {node.name}")
        return symbols[node.name]

    if isinstance(node, BinaryOpNode):
        left = evaluate_expression_tree(node.left, symbols, ureg)
        right = evaluate_expression_tree(node.right, symbols, ureg)

        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            return left / right
        elif node.op == '^':
            # Exponent must be dimensionless
            exp = right.to('dimensionless').magnitude
            return left ** exp

    if isinstance(node, UnaryOpNode):
        operand = evaluate_expression_tree(node.operand, symbols, ureg)
        if node.op == '-':
            return -operand

    if isinstance(node, UnitNode):
        value = evaluate_expression_tree(node.value, symbols, ureg)
        return value * ureg(node.unit)

    raise EvaluationError(f"Unknown node type: {type(node)}")
```
</code_examples>

<sota_updates>
## State of the Art (2024-2025)

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| latex2sympy | Custom parser for LiveMathTeX | Proposed | Eliminates implicit multiplication |
| SymPy for units | Pint exclusively | v1.6 (done) | Already using Pint for evaluation |
| Regex parsing | Tokenizer + parser | Proposed | More robust, maintainable |

**New tools/patterns to consider:**
- **Pint 0.23:** Better string parsing, could simplify unit handling
- **Lark parser:** If grammar grows complex, switch from hand-written parser
- **Tree-sitter:** For syntax highlighting in editors (future)

**Deprecated/outdated:**
- **latex2sympy:** Too rigid for our use case, replace
- **SymPy evaluation path:** No longer needed once parser is custom
</sota_updates>

<open_questions>
## Open Questions

1. **Function definition syntax**
   - What we know: Functions are defined with `:=` and called with `f(x)`
   - What's unclear: How to handle Lambda storage without SymPy
   - Recommendation: Store as Python callable in symbol table

2. **Backward compatibility**
   - What we know: Need to keep existing document syntax working
   - What's unclear: Edge cases in existing documents
   - Recommendation: Extensive test suite migration, phased rollout

3. **Error messages**
   - What we know: Current errors come from latex2sympy/SymPy
   - What's unclear: What errors users expect
   - Recommendation: Build error message catalog during implementation
</open_questions>

<sources>
## Sources

### Primary (HIGH confidence)
- LiveMathTeX codebase analysis - evaluator.py, pint_backend.py, lexer.py
- latex2sympy2 behavior testing - verified issues with implicit multiplication
- Pint documentation - unit handling confirmed

### Secondary (MEDIUM confidence)
- [pypi.org/project/latex2sympy2](https://pypi.org/project/latex2sympy2/) - library status
- [github.com/phfaist/pylatexenc](https://github.com/phfaist/pylatexenc) - LaTeX entity handling
- [Hackaday - Parsing Math in Python](https://hackaday.com/2020/09/18/parsing-math-in-python/) - general approach

### Tertiary (LOW confidence - needs validation)
- Expression parser patterns - common knowledge, validate during implementation
</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: LaTeX math parsing, custom tokenizer
- Ecosystem: Pint, pylatexenc
- Patterns: Tokenizer + recursive descent, direct Pint evaluation
- Pitfalls: Token ordering, precedence, implicit multiplication

**Confidence breakdown:**
- Standard stack: HIGH - based on codebase analysis
- Architecture: HIGH - well-known patterns
- Pitfalls: HIGH - derived from current bug reports
- Code examples: MEDIUM - need validation during implementation

**Research date:** 2026-01-14
**Valid until:** 2026-02-14 (30 days - stable patterns)
</metadata>

---

*Phase: 23-remove-latex2sympy*
*Research completed: 2026-01-14*
*Ready for planning: yes*
