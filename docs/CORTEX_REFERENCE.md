# Cortex-JS / MathJSON Reference

This document summarizes key learnings from the Cortex-JS compute-engine project
that inform our symbol normalization implementation.

**Source Repository:** https://github.com/cortex-js/compute-engine
**Local Clone:** `/home/mark/Repositories/cortex-compute-engine/`

---

## Key Files to Reference

| File | Purpose | Key Learnings |
|------|---------|---------------|
| `src/compute-engine/latex-syntax/parse-symbol.ts` | LaTeX symbol parsing | Greek letters, subscript handling, modifier detection |
| `src/compute-engine/latex-syntax/serializer.ts` | Symbol serialization to LaTeX | Bidirectional mapping, style wrapping |
| `src/compute-engine/latex-syntax/dictionary/definitions-symbols.ts` | Greek/special symbol mappings | Complete list of Greek letters with LaTeX commands |
| `src/math-json/symbols.ts` | Symbol validation | Unicode UAX31 compliance, emoji handling |
| `src/common/error-messages.json` | Error messages | Internationalization pattern |

---

## Symbol Naming Convention (Cortex-JS Standard)

### 1. Greek Letters
```
LaTeX Command    Internal Name    Unicode
\alpha           alpha            U+03B1
\Delta           Delta            U+0394
\Omega           Omega            U+03A9
```

### 2. Subscripts and Superscripts
```
LaTeX            Internal         Notes
x_1              x_1              Single subscript
x_{12}           x_12             Multi-digit subscript
x_{a,b}          x_a_b            Multiple subscripts (commas → underscores)
T_{h,in}         T_h_in           Nested subscript
x^2              x__2             Superscript uses double underscore
x_1^2            x_1__2           Combined
```

### 3. Modifiers (Accents)
```
LaTeX            Internal Suffix
\dot{x}          x_dot
\hat{x}          x_hat
\vec{x}          x_vec
\bar{x}          x_bar
\tilde{x}        x_tilde
\ddot{x}         x_ddot
```

### 4. Style Modifiers
```
LaTeX            Internal Suffix
\mathrm{x}       x_upright
\mathit{x}       x_italic
\mathbf{x}       x_bold
\mathbb{x}       x_doublestruck
\mathcal{x}      x_calligraphic
\mathfrak{x}     x_fraktur
```

---

## Multi-character Symbol Protection

Cortex-JS wraps multi-character symbols to prevent LaTeX splitting:

```typescript
// From serializer.ts lines 489-504
switch (style) {
  case 'auto':
    if (countTokens(body) > 1) body = `\\mathrm{${body}}`;
    break;
  case 'operator':
    body = `\\operatorname{${body}}`;
    break;
}
```

**Our equivalent:** We use `\text{}` for multi-letter names to protect from `latex2sympy` splitting.

---

## Subscript Parsing Algorithm

From `parseSymbolBody()` in serializer.ts:

1. **Digits at end become subscript:** `alpha0` → `α₀`
2. **Single underscore = subscript:** `x_1` → `x₁`
3. **Double underscore = superscript:** `x__2` → `x²`
4. **Multiple subscripts separated by underscore**

```typescript
// From serializer.ts lines 466-478
while (rest.length > 0) {
  if (rest.startsWith('__')) {
    const [sup, rest2] = parseSymbolBody(rest.substring(2), false, 'none');
    sups.push(sup);
    rest = rest2;
  } else if (rest.startsWith('_')) {
    const [sub, rest2] = parseSymbolBody(rest.substring(1), false, 'none');
    subs.push(sub);
    rest = rest2;
  } else {
    break;
  }
}
```

---

## Symbol Validation (from symbols.ts)

Cortex-JS validates symbols against Unicode UAX31:

```typescript
// Quick check for simple symbols
if (/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(s)) return true;

// Non-ASCII symbols (Unicode identifier syntax)
return /^[\p{XIDS}_]\p{XIDC}*$/u.test(s);
```

**Checks performed:**
- Unicode NFC normalization
- No bidirectional control characters
- Only recommended scripts (Latin, Greek, Cyrillic, etc.)
- Valid identifier start/continuation characters

---

## Error Handling Pattern

From `error-messages.json`:
```json
{
  "en-us": {
    "invalid-identifier": "\"%0\" is not a valid identifier",
    "symbol-expected": "A symbol name was expected",
    "unexpected-symbol": "Unexpected symbol \"%0\""
  }
}
```

**Lesson:** Use parameterized error messages for internationalization.

---

## Problems They Solved

### 1. Greek letter + following symbol
**Problem:** `\Delta T_h` parsed as `Delta * T_h`
**Solution:** Combine into single symbol `Delta_T_h`

### 2. Multi-letter variable splitting
**Problem:** `eta_p` → `e * t * a_p`
**Solution:** Wrap in `\mathrm{}` or `\operatorname{}`

### 3. Subscript with commas
**Problem:** `T_{h,in}` ambiguous (comma could be separator)
**Solution:** Convert commas to underscores: `T_h_in`

### 4. Superscript vs subscript
**Problem:** Ambiguity between `x_2` (subscript) and `x^2` (superscript)
**Solution:** Use `_` for subscript, `__` for superscript in internal names

---

## Implementation Checklist for LiveMathTeX

- [x] Greek letter mapping (GREEK_LETTERS in normalize.py)
- [x] Subscript normalization (commas → underscores)
- [x] Greek + space + symbol pattern handling
- [x] Multi-letter name protection with \text{}
- [ ] Superscript handling (__ convention)
- [ ] Modifier support (_dot, _hat, etc.)
- [ ] Style modifier support (_upright, _bold, etc.)
- [ ] Full Unicode UAX31 validation
- [ ] Parameterized error messages

---

## Future Improvements

1. **Bidirectional serialization:** Ensure `normalize_symbol()` and `denormalize_symbol()` are perfect inverses
2. **Modifier support:** Add accent and style modifiers
3. **Unicode symbols:** Support direct Unicode Greek letters (α instead of \alpha)
4. **Error messages:** Internationalization support

---

**Last Updated:** 2026-01-05
**Maintained by:** LiveMathTeX development
