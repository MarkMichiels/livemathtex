# Debugging Workflow in GSD Framework

## Overview

GSD framework is primarily designed for **greenfield development** (building new features from scratch), not for debugging existing bugs. However, it provides a structured workflow for handling bugs discovered during development.

## Two Types of Issues in GSD

### 1. Global ISSUES.md - Enhancements (ISS-XXX)

**Purpose:** Deferred enhancements discovered during execution (Rule 5 - "nice-to-haves")

**Location:** `.planning/ISSUES.md`

**When to use:**
- Feature improvements that aren't critical
- Refactoring opportunities
- Performance optimizations
- Documentation improvements

**Format:**
```markdown
### ISS-012: Process/clear cycle produces unstable results

- **Discovered:** Post-Phase 4 (2026-01-12)
- **Type:** Bug
- **Description:** [What could be improved]
- **Impact:** High
- **Effort:** Substantial
- **Suggested phase:** Future
```

**Workflow:**
- Created manually or during execution (Rule 5)
- Reviewed with `/gsd:consider-issues`
- Addressed in future phases when prioritized

### 2. UAT Issues - Bugs Found During Testing (UAT-XXX)

**Purpose:** Actual bugs/problems found during user acceptance testing

**Location:** `.planning/phases/XX-name/{phase}-{plan}-ISSUES.md`

**When to use:**
- Bugs discovered during `/gsd:verify-work`
- Problems with delivered features
- Issues that prevent features from working correctly

**Format:**
```markdown
### UAT-001: Process/clear cycle produces unstable results

**Discovered:** 2026-01-12
**Phase/Plan:** 04-02
**Severity:** Major
**Feature:** Process/clear cycle
**Description:** When processing output.md multiple times, content changes unexpectedly
**Expected:** File should be stable (only timestamp changes)
**Actual:** Content changes, errors appear/disappear
**Repro:**
1. Process input.md → output.md
2. Process output.md again
3. Content differs from first processing
```

**Workflow:**
1. `/gsd:verify-work` - Test phase/plan, finds bugs
2. Issues logged to `{phase}-{plan}-ISSUES.md`
3. `/gsd:plan-fix {plan}` - Creates FIX.md plan
4. `/gsd:execute-plan` - Executes fixes
5. Issues moved to "Resolved" section after fix

## Debugging Existing Bugs (Not During Development)

**Problem:** GSD is designed for new development, not debugging existing codebases.

**Current Situation (ISS-012):**
- Bug discovered outside of normal GSD workflow
- Not found during `/gsd:verify-work` (no phase to test)
- Already documented in global `ISSUES.md`

**Options:**

### Option 1: Create a Bug Fix Phase

Treat the bug as a new phase in the roadmap:

```bash
/gsd:add-phase
# Or
/gsd:insert-phase 5  # Insert as Phase 5
```

Then:
1. Create phase for bug fix (e.g., "Phase 5: Bug Fixes")
2. Reference ISS-012 in phase description
3. Use normal GSD workflow: plan → execute → verify

**Pros:**
- Uses standard GSD workflow
- Properly tracked in roadmap
- Can be executed with `/gsd:execute-plan`

**Cons:**
- Requires creating a full phase for a bug
- May feel over-engineered for single bugs

### Option 2: Manual Fix Outside GSD

Fix the bug manually, then document:

1. Investigate bug (create `BUG_INVESTIGATION.md` if needed)
2. Fix the code manually
3. Test the fix
4. Update `ISSUES.md` to mark as resolved
5. Commit changes

**Pros:**
- Fast for urgent bugs
- No GSD overhead
- Direct control

**Cons:**
- Not tracked in GSD workflow
- No automatic planning/verification
- May miss related issues

### Option 3: Convert to UAT Issue (If Applicable)

If the bug affects a recently completed phase:

1. Run `/gsd:verify-work` on that phase
2. Report the bug during testing
3. It gets logged as UAT issue
4. Use `/gsd:plan-fix` to create fix plan

**Pros:**
- Uses GSD's bug workflow
- Properly scoped to affected phase
- Can be fixed with GSD tools

**Cons:**
- Only works if bug affects recent phase
- Requires re-testing completed work

## Recommended Approach for ISS-012

**Current Status:**
- Bug documented in global `ISSUES.md` (ISS-012)
- Detailed investigation in `BUG_INVESTIGATION.md`
- Test framework extended (`test_process_clear_cycle.py`)

**Recommended Next Steps:**

1. **Create a bug fix phase:**
   ```bash
   /gsd:add-phase
   # Name: "Phase 5: Process/Clear Cycle Bug Fixes"
   # Goal: Fix ISS-012 - process/clear cycle stability
   ```

2. **Plan the fix:**
   ```bash
   /gsd:plan-phase 5
   # Creates plan with tasks to fix the bugs
   ```

3. **Execute:**
   ```bash
   /gsd:execute-plan
   # Implements fixes
   ```

4. **Verify:**
   ```bash
   /gsd:verify-work 5
   # Tests that bugs are fixed
   ```

**Alternative (if urgent):**
- Fix manually
- Update `ISSUES.md` to mark resolved
- Document fix in commit message
- Skip GSD workflow for this bug

## Key Differences Summary

| Aspect | Global ISSUES.md | UAT Issues |
|--------|------------------|------------|
| **Purpose** | Enhancements (nice-to-haves) | Bugs (problems) |
| **Location** | `.planning/ISSUES.md` | `.planning/phases/XX-name/{plan}-ISSUES.md` |
| **Numbering** | ISS-001, ISS-002 (global) | UAT-001, UAT-002 (per file) |
| **When created** | During execution (Rule 5) | During `/gsd:verify-work` |
| **Workflow** | `/gsd:consider-issues` → future phase | `/gsd:verify-work` → `/gsd:plan-fix` → fix |
| **Scope** | Project-wide | Phase/plan specific |

## References

- [GSD README - Commands](https://github.com/glittercowboy/get-shit-done)
- [UAT Issues Template](~/.claude/get-shit-done/templates/uat-issues.md)
- [Verify Work Command](~/.claude/get-shit-done/commands/gsd/verify-work.md)
- [Plan Fix Command](~/.claude/get-shit-done/commands/gsd/plan-fix.md)

---

**Last Updated:** 2026-01-12
**Status:** Documentation for debugging workflow in GSD framework

