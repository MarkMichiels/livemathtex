# Research: Phase 8 - Markdown Parser Integration

**Phase:** 8 - Markdown Parser Integration
**Goal:** Integrate markdown parser library for AST with exact source spans
**Research Date:** 2026-01-13

## Research Questions

1. Which Python markdown parsers provide source position/span tracking?
2. Can we get character-level offsets, not just line numbers?
3. How do these parsers handle math blocks (`$$...$$`)?
4. What's the migration path from current regex-based parsing?

## Findings

### Parser Comparison

| Parser | Line Positions | Character Offsets | Math Support | Extensibility |
|--------|----------------|-------------------|--------------|---------------|
| **markdown-it-py** | ✅ `Token.map` | ❌ declined | ✅ dollarmath plugin | ✅ plugins |
| **mistune** | ❌ | ❌ | ❌ | ✅ renderers |
| **mistletoe** | ✅ block tokens | ❌ | ❌ | ✅ custom tokens |
| **marko** | ❓ unclear | ❓ unclear | ❌ | ✅ extensions |
| **python-markdown** | ❌ | ❌ | ✅ via extension | ✅ extensions |

### Critical Finding: No Character-Level Offsets

**None of the major Python markdown parsers provide character-level source offsets.**

- **markdown-it-py**: The `Token.map` attribute contains `[line_begin, line_end]` (0-indexed lines). Character-level tracking was explicitly "declined at planning phases as too expensive" in the original markdown-it JavaScript library.
- **mistletoe**: Has `line_number` attribute on block tokens only; span/inline tokens lack position tracking.
- **mistune**: AST output via `renderer='ast'` has no built-in position tracking at all.

### markdown-it-py Details

**Source:** [GitHub - executablebooks/markdown-it-py](https://github.com/executablebooks/markdown-it-py)

Token structure:
```python
Token(
    type='math_block',
    tag='math',
    nesting=0,
    attrs={},
    map=[4, 6],           # Line range [start, end) - 0-indexed
    level=0,
    children=None,
    content='x := 5 ...',  # Raw content inside delimiters
    markup='$$',
    info='',
    meta={},
    block=True,
    hidden=False
)
```

Math block support via `mdit-py-plugins`:
```python
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

md = MarkdownIt().use(dollarmath_plugin, allow_space=True, allow_digits=True)
tokens = md.parse(text)
```

**SyntaxTreeNode**: Can convert flat token stream to hierarchical tree:
```python
from markdown_it.tree import SyntaxTreeNode
tree = SyntaxTreeNode(tokens)
```

### Current LiveMathTeX Parser Analysis

**File:** `src/livemathtex/parser/lexer.py`

Current approach:
- Regex-based: `MATH_BLOCK_RE` pattern finds `$$...$$` blocks
- `SourceLocation` dataclass tracks: `start_line`, `end_line`, `start_col`, `end_col`
- `_get_line_number()` calculates line positions from character offsets
- Code block exclusion via `CODE_BLOCK_RE`

**Problems addressed by this phase:**
- ISS-021: Clear corruption around multiline error blocks (regex doesn't track document structure)
- ISS-020: Structural parsing needed for robust clear/process cycle

## Architecture Options

### Option A: Full markdown-it-py Migration (Recommended)

Use markdown-it-py as the document parser, calculate character offsets post-hoc.

**Approach:**
1. Parse document with markdown-it-py + dollarmath_plugin
2. Convert line positions to character offsets using newline counting
3. Extract math blocks as first-class nodes with precise boundaries
4. Keep existing calculation parsing (operators, expressions) unchanged

**Advantages:**
- Battle-tested CommonMark parser
- Reliable code fence detection (avoids parsing math in code blocks)
- Extensible plugin architecture
- Active maintenance by executablebooks

**Character offset calculation:**
```python
def line_to_offset(text: str, line: int) -> int:
    """Convert 0-indexed line number to character offset."""
    lines = text.split('\n')
    return sum(len(lines[i]) + 1 for i in range(line))
```

### Option B: Hybrid (Keep Current + Add Structure)

Keep regex for math extraction, add markdown-it-py only for code block detection.

**Disadvantages:**
- Two parsing passes
- Maintenance burden of two systems
- Doesn't solve root cause (regex fragility)

### Option C: Custom Parser with Spans

Build custom parser tracking character offsets throughout.

**Disadvantages:**
- Significant engineering effort
- CommonMark edge cases
- Maintenance burden

## Recommended Stack

```
Document Input
      │
      ▼
┌─────────────────────────────┐
│ markdown-it-py              │
│ + dollarmath_plugin         │
│ → Token stream with map     │
└─────────────────────────────┘
      │
      ▼
┌─────────────────────────────┐
│ Position Converter          │
│ line_map → char_offsets     │
│ → SourceLocation objects    │
└─────────────────────────────┘
      │
      ▼
┌─────────────────────────────┐
│ Math Block Parser           │
│ (existing calculation       │
│  extraction logic)          │
└─────────────────────────────┘
      │
      ▼
Document Model (existing)
```

## Dependencies

**Required:**
- `markdown-it-py>=3.0.0` - Core parser
- `mdit-py-plugins>=0.4.0` - dollarmath plugin

**Installation:**
```bash
pip install markdown-it-py mdit-py-plugins
```

## Migration Path

1. **Phase 8**: Add markdown-it-py integration alongside existing parser
2. **Phase 9**: Parse math block internals using spans from Phase 8
3. **Phase 10**: Rewrite `clear_text()` using span-based operations

Keep existing `SourceLocation` model - just populate from markdown-it-py tokens instead of regex.

## Common Pitfalls

1. **Off-by-one errors**: markdown-it uses 0-indexed lines, current code may use 1-indexed
2. **Newline handling**: `\r\n` vs `\n` affects offset calculations
3. **Dollar sign in code**: dollarmath plugin needs `allow_space=True` to avoid conflicts
4. **Nested math**: `$...$` inline vs `$$...$$` block have different token types

## Test Strategy

1. Create test documents with:
   - Code fences containing `$$`
   - Math blocks with various operators
   - Multiline math blocks
   - Edge cases from ISS-021

2. Verify position accuracy:
   - Extract math block → modify → reinsert at exact position
   - Round-trip should produce identical document

## References

- [markdown-it-py GitHub](https://github.com/executablebooks/markdown-it-py)
- [mdit-py-plugins dollarmath](https://mdit-py-plugins.readthedocs.io/en/latest/#dollarmath)
- [markdown-it Token structure](https://markdown-it.github.io/markdown-it/#Token)
- [mistletoe GitHub](https://github.com/miyuchina/mistletoe)
- [Python-Markdown Extension API](https://python-markdown.github.io/extensions/api/)

## Conclusion

**Recommendation:** Use **markdown-it-py with dollarmath_plugin** for document structure, with post-hoc character offset calculation. This provides:

- Reliable math block detection with line positions
- Proper code fence handling (no false positives)
- Extensible architecture for future needs
- Minimal changes to existing calculation parsing

The key insight is that character-level precision can be achieved by converting line positions to offsets - we don't need the parser to track characters natively.
