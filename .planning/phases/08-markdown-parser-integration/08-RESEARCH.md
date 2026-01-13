# Research: Phase 8 - Markdown Parser Integration

**Phase:** 8 - Markdown Parser Integration
**Goal:** Integrate markdown parser library for AST with exact source spans
**Research Date:** 2026-01-13 (updated)
**Confidence:** HIGH

## Research Questions

1. Which Python markdown parsers provide source position/span tracking?
2. Can we get character-level offsets, not just line numbers?
3. How do these parsers handle math blocks (`$$...$$`)?
4. What's the migration path from current regex-based parsing?
5. **NEW:** Can we get character-level positions WITHIN LaTeX math blocks?

## Findings

### Markdown Parser Comparison

| Parser | Line Positions | Character Offsets | Math Support | Extensibility |
|--------|----------------|-------------------|--------------|---------------|
| **markdown-it-py** | ✅ `Token.map` | ❌ declined | ✅ dollarmath plugin | ✅ plugins |
| **mistune** | ❌ | ❌ | ❌ | ✅ renderers |
| **mistletoe** | ✅ block tokens | ❌ | ❌ | ✅ custom tokens |
| **marko** | ❓ unclear | ❓ unclear | ❌ | ✅ extensions |
| **python-markdown** | ❌ | ❌ | ✅ via extension | ✅ extensions |

### LaTeX Parser Comparison

| Parser | Character Positions | Line/Col Support | Fault Tolerant | Notes |
|--------|---------------------|------------------|----------------|-------|
| **pylatexenc** | ✅ `pos`, `pos_end` | ✅ `pos_to_lineno_colno()` | ✅ `tolerant_parsing` | Best choice |
| **TexSoup** | ❌ | ❌ | ✅ | No fine offsets |
| **Pandoc** | ✅ `--track-source-pos` | ✅ | ✅ | Heavy, external binary |

### Critical Finding: Hybrid Approach Required

**Markdown parsers don't provide character-level offsets**, but **pylatexenc does** for LaTeX content.

**Solution:** Two-layer parsing:
1. **markdown-it-py** → Find math blocks with document positions
2. **pylatexenc** → Parse LaTeX content with character-level precision

### pylatexenc LatexWalker Details

**Source:** [pylatexenc documentation](https://pylatexenc.readthedocs.io/en/latest/latexwalker/)

Node position tracking:
```python
from pylatexenc.latexwalker import LatexWalker

w = LatexWalker(r"x := 5 \cdot \text{kg}")
nodes, pos, length = w.get_latex_nodes()

# Each node has:
# - node.pos      : start position in string
# - node.pos_end  : end position (pylatexenc 3.0+)
# - node.len      : length (deprecated, use pos_end - pos)

# Convert to line/column:
lineno, colno = w.pos_to_lineno_colno(node.pos)
```

Node types:
- `LatexCharsNode`: Plain text characters
- `LatexMacroNode`: Macros like `\text`, `\frac`
- `LatexGroupNode`: Brace groups `{...}`
- `LatexMathNode`: Math environments

**Version note:** pylatexenc 3.0+ uses `pos_end` instead of `len`. Both work for compatibility.

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

## Recommended Architecture: Hybrid Stack

```
Document Input
      │
      ▼
┌─────────────────────────────┐
│ Layer 1: markdown-it-py     │
│ + dollarmath_plugin         │
│ → Math block boundaries     │
│ → Code fence exclusion      │
└─────────────────────────────┘
      │
      ▼
┌─────────────────────────────┐
│ Position Converter          │
│ line_map → char_offsets     │
│ → Math block char positions │
└─────────────────────────────┘
      │
      ▼
┌─────────────────────────────┐
│ Layer 2: pylatexenc         │
│ LatexWalker per math block  │
│ → Character-level positions │
│ → LaTeX node structure      │
└─────────────────────────────┘
      │
      ▼
┌─────────────────────────────┐
│ Unified Document Model      │
│ MathBlock with:             │
│ - document offsets          │
│ - internal LaTeX positions  │
└─────────────────────────────┘
```

### Why This Works

1. **markdown-it-py** reliably finds `$$...$$` blocks and excludes code fences
2. **Position converter** translates line positions to character offsets
3. **pylatexenc** parses the LaTeX content with exact character positions
4. **Offset combination**: `document_offset + latex_node.pos` = absolute position

### Example Pipeline

```python
# 1. Parse markdown
md = MarkdownIt().use(dollarmath_plugin)
tokens = md.parse(document_text)

# 2. For each math_block token
for token in tokens:
    if token.type == 'math_block':
        # Get document position
        start_line = token.map[0]
        doc_offset = line_to_offset(document_text, start_line)

        # 3. Parse LaTeX content
        latex_content = token.content
        walker = LatexWalker(latex_content, tolerant_parsing=True)
        nodes, _, _ = walker.get_latex_nodes()

        # 4. Combine positions
        for node in nodes:
            absolute_pos = doc_offset + node.pos
            # Now we know exactly where this LaTeX element is in the document
```

## Dependencies

**Required:**
- `markdown-it-py>=3.0.0` - Markdown parser
- `mdit-py-plugins>=0.4.0` - dollarmath plugin
- `pylatexenc>=2.10` - LaTeX parser with position tracking

**Installation:**
```bash
pip install markdown-it-py mdit-py-plugins pylatexenc
```

## Migration Path

1. **Phase 8**: Add hybrid parser (markdown-it-py + pylatexenc)
2. **Phase 9**: Use LaTeX node positions for operator parsing
3. **Phase 10**: Rewrite `clear_text()` using span-based operations
4. **Phase 11**: Use LaTeX AST for token classification

## Common Pitfalls

1. **Off-by-one errors**: markdown-it uses 0-indexed lines, pylatexenc uses 0-indexed chars
2. **Newline handling**: `\r\n` vs `\n` affects offset calculations - normalize first
3. **Dollar sign in code**: dollarmath plugin needs `allow_space=True`
4. **pylatexenc tolerant mode**: Use `tolerant_parsing=True` to handle malformed LaTeX
5. **Position combination**: Remember to add math block's document offset to LaTeX node positions
6. **pylatexenc 3.0 changes**: `len` deprecated, use `pos_end` or `pos_end - pos`

## Test Strategy

1. **Document-level tests:**
   - Code fences containing `$$` (should be excluded)
   - Multiple math blocks
   - Math at document start/end

2. **Position accuracy tests:**
   - `text[start:end] == content` for all extracted blocks
   - Round-trip: extract → modify → reinsert produces correct result

3. **LaTeX position tests:**
   - Operator positions (`:=`, `==`) within math blocks
   - Nested structures (`\frac{a}{b}`)
   - Error positions for malformed LaTeX

## References

- [markdown-it-py GitHub](https://github.com/executablebooks/markdown-it-py)
- [mdit-py-plugins dollarmath](https://mdit-py-plugins.readthedocs.io/en/latest/#dollarmath)
- [pylatexenc documentation](https://pylatexenc.readthedocs.io/en/latest/latexwalker/)
- [pylatexenc GitHub](https://github.com/phfaist/pylatexenc)
- [pylatexenc node classes](https://pylatexenc.readthedocs.io/en/latest/latexnodes.nodes/)

## Conclusion

**Recommendation:** Use **hybrid approach** with:
1. **markdown-it-py + dollarmath_plugin** for document structure
2. **pylatexenc LatexWalker** for character-level LaTeX parsing

This provides:
- Reliable math block detection with proper code fence handling
- Character-level precision within LaTeX content
- Fault-tolerant parsing for malformed LaTeX
- Foundation for future phases (token classification, clear refactor)

The key insight is that **two specialized parsers** (markdown + LaTeX) work better than trying to find one parser that does everything.
