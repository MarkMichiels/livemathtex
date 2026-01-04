# Background: The Road to Livemathtex

This document captures the research and exploration that led to creating Livemathtex. It explains what alternatives exist, what we tried, and why we decided to build a new tool.

---

## The Original Need

**Goal:** Mathcad-style live calculations in Markdown documents.

- Write formulas in LaTeX notation
- Variables persist across the document
- Change an input → all outputs update
- Git-friendly plain text
- Beautiful rendering

---

## Tools Investigated

### 1. Markdown Preview Enhanced (MPE) Code Chunks

**What it is:** VS Code extension that executes code blocks in Markdown preview.

**Syntax tested:**
```markdown
```python {cmd id="session"}
x = 42
print(x)
`` `

```python {cmd continue="session"}
y = x * 2
print(y)
`` `
```

**What worked:**
- ✅ Code executes in preview
- ✅ Variables persist with `continue="session_name"`
- ✅ Supports Python, JavaScript, etc.

**What didn't work:**
- ❌ Re-executes ALL previous blocks on each run
- ❌ Output accumulates (all previous print statements repeat)
- ❌ Not practical for long documents
- ❌ No LaTeX math integration — you're writing Python, not formulas
- ❌ Formula and result are still separate (code block vs text)

**Verdict:** Good for short demos, not for real calculation documents.

---

### 2. Jupytext

**What it is:** Tool to sync Jupyter notebooks with plain text formats (Markdown, Python scripts).

**How it works:**
```bash
jupytext --to notebook document.md    # MD → ipynb
jupytext --to markdown notebook.ipynb  # ipynb → MD
```

**What worked:**
- ✅ Jupyter's execution model (cells run independently)
- ✅ Variables persist properly
- ✅ Can edit as Markdown, run as notebook

**What didn't work:**
- ❌ Requires Jupyter runtime
- ❌ Still writing Python code, not LaTeX formulas
- ❌ Two environments: edit in VS Code, run in Jupyter
- ❌ Output not embedded in the Markdown file
- ❌ `F = m * a` in code is not `$F = m \cdot a$` in a report

**Verdict:** Solves variable persistence but not the notation problem.

---

### 3. Quarto

**What it is:** Publishing system for scientific documents with executable code.

**Features:**
- Markdown + code blocks → PDF, HTML, Word
- Supports Python, R, Julia
- Beautiful output

**What didn't work:**
- ❌ Still code-based, not formula-based
- ❌ Complex setup (requires Quarto CLI, runtime environments)
- ❌ Overkill for simple calculations
- ❌ Not Mathcad-style — it's Jupyter with better export

**Verdict:** Great for data science reports, not for engineering calculations.

---

### 4. Latex Sympy Calculator (VS Code Extension)

**What it is:** VS Code extension by OrangeX4 that evaluates LaTeX expressions.

**How it works:**
- Write LaTeX in comments or special blocks
- Extension computes and shows results

**What worked:**
- ✅ Actually parses LaTeX!
- ✅ Uses SymPy for computation
- ✅ Inline results

**What didn't work:**
- ❌ Designed for `.tex` files, not Markdown
- ❌ Requires Flask server running
- ❌ Not Markdown-first workflow
- ❌ Results shown in extension, not embedded in document

**Related:** `vscode-typst-sympy-calculator` exists for Typst files.

**Verdict:** Right idea (LaTeX → SymPy), wrong context (not Markdown-native).

---

### 5. Typst

**What it is:** Modern typesetting system, Markdown-inspired.

**Features:**
- Plain text → beautiful PDF
- Own syntax (not LaTeX, but similar)
- Growing ecosystem

**What didn't work:**
- ❌ Own syntax, not standard LaTeX
- ❌ Not Markdown — separate ecosystem
- ❌ Limited calculation support (needs packages)
- ❌ LLMs less fluent in Typst than LaTeX

**Verdict:** Promising for documents, but not the Markdown+LaTeX combo we need.

---

### 6. SMath Studio

**What it is:** Free Mathcad alternative.

**What worked:**
- ✅ Live calculations
- ✅ Mathematical notation
- ✅ Units support

**What didn't work:**
- ❌ GUI application, not plain text
- ❌ XML file format — not Git-friendly
- ❌ Not embeddable in Markdown workflow
- ❌ Separate tool, not part of documentation flow

**Verdict:** Good standalone tool, but doesn't fit text-based workflow.

---

### 7. Qalc (VS Code Extension)

**What it is:** VS Code extension integrating Qalculate! engine.

**Features:**
- Inline calculations in any file
- Unit support
- Natural syntax

**What didn't work:**
- ❌ Own syntax, not LaTeX
- ❌ Results as comments, not embedded in formulas
- ❌ Not designed for Markdown math blocks

**Verdict:** Great calculator, wrong notation.

---

## The Gap

After investigating all these tools, we identified a gap:

| Requirement | Available Tools |
|-------------|-----------------|
| LaTeX notation | ✅ Latex Sympy Calculator (but not Markdown) |
| Markdown-native | ✅ MPE, Jupytext (but Python code, not LaTeX) |
| Git-friendly | ✅ All text-based tools |
| Live calculations | ✅ Jupyter, MPE (but code-based) |
| Variable persistence | ✅ Jupyter (but JSON format) |
| **All of the above** | ❌ Nothing |

**No tool combined LaTeX notation + Markdown + live calculations + Git-friendly.**

---

## The Decision

Rather than forcing existing tools to do something they weren't designed for, we decided to build a focused preprocessor:

1. **Input:** Markdown with LaTeX math blocks
2. **Process:** Parse LaTeX, evaluate with SymPy
3. **Output:** Same Markdown with computed results

**Key insight:** We don't need a full environment. Just a preprocessor that:
- Understands `:=` (assignment) and `=` (evaluation)
- Maintains variable state across the document
- Inserts results back into the LaTeX

**What we DON'T build:**
- No GUI (VS Code is the editor)
- No PDF export (Pandoc does this)
- No live preview (Markdown Preview Enhanced does this)
- No notebook format (we stay in Markdown)

---

## The AI Era Insight

During this research, a key insight emerged:

> **Humans don't write LaTeX by hand anymore — LLMs do.**

This changes the value proposition:

- **Old thinking:** "I need a tool to help me write LaTeX calculations"
- **New thinking:** "LLMs write the LaTeX, I need a tool to make the results verifiable"

Livemathtex bridges the disconnect between AI-generated formulas and computed results. The LLM generates `$F := m \cdot a =$`, Livemathtex fills in `49.05 \text{ N}`.

---

## Conclusion

Livemathtex exists because:

1. **LaTeX + Markdown + live calculations** didn't exist together
2. **LLMs generate LaTeX fluently** — we leverage that
3. **Focused tools beat complex platforms** — do one thing well
4. **Plain text wins** — Git, AI, tooling all work better with text

The research showed many good tools, but none combined everything. Livemathtex fills that specific gap.

---

## References

- [Markdown Preview Enhanced](https://shd101wyy.github.io/markdown-preview-enhanced/)
- [Jupytext](https://jupytext.readthedocs.io/)
- [Quarto](https://quarto.org/)
- [Latex Sympy Calculator](https://github.com/OrangeX4/Latex-Sympy-Calculator)
- [Typst](https://typst.app/)
- [SMath Studio](https://smath.com/)
- [Qalculate!](https://qalculate.github.io/)

