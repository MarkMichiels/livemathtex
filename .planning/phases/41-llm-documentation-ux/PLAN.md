---
phase: 41-llm-documentation-ux
plan: 01
status: active
created: 2026-01-16
---

# Phase 41 Plan: LLM Documentation & UX

## Context

Two related issues address the need for AI assistants (Claude, GPT, Cursor) to generate correct LiveMathTeX documents:

1. **ISS-052:** Unit syntax intuitiveness - `\text{}` wrapper requirement not intuitive
2. **ISS-053:** LLM-Aware Documentation - AI assistants generate incorrect syntax

## Goals

1. Create Cursor rule (`.mdc`) with syntax cheatsheet for AI assistants
2. Update USAGE.md with "For AI Assistants" section
3. Document common pitfalls and correct patterns

## Scope

**In scope:**
- Cursor rules file: `.cursor/rules/livemathtex.mdc`
- USAGE.md update: "For AI Assistants" section
- Update `/livemathtex` command to reference new documentation

**Out of scope:**
- Code changes to auto-detect unit patterns (ISS-052 alternative 1)
- Improved error messages (ISS-052 alternative 3)

## Implementation

### Task 1: Create Cursor Rule `.cursor/rules/livemathtex.mdc`

Create a comprehensive rule file that LLMs (in Cursor) will use when generating LiveMathTeX documents.

**Content:**
- Syntax quick reference (`:=`, `==`, `===`, `=>`)
- Unit syntax rules (when `\text{}` is needed)
- Variable naming conventions (avoid single letters that are units)
- Cross-reference syntax (`{{variable}}`, `{{variable [unit]}}`)
- Array syntax
- Function definition syntax
- Common pitfalls with solutions
- Document structure best practices

### Task 2: Add "For AI Assistants" Section to USAGE.md

Add a dedicated section aimed at AI assistants that are generating LiveMathTeX documents.

**Content:**
- Clear rules for when to use `\text{}` for units
- Variable naming conventions
- Complete syntax examples
- Error patterns to avoid

### Task 3: Update `/livemathtex` Command

Reference the new Cursor rule and USAGE.md section.

## Verification

1. The `.mdc` file loads correctly in Cursor
2. USAGE.md renders correctly with new section
3. Test: Ask Claude to generate a LiveMathTeX document using the new rules

## Success Criteria

- [ ] `.cursor/rules/livemathtex.mdc` created with comprehensive syntax guide
- [ ] USAGE.md has "For AI Assistants" section
- [ ] `/livemathtex` command updated to reference new documentation
- [ ] ISS-052 and ISS-053 marked as resolved
