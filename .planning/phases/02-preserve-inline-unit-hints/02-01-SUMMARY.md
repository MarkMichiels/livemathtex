# Phase 2 Plan 1: Preserve Inline Unit Hints Summary

**Inline unit hints now survive processing and re-processing via automatic HTML comment injection.**

## Accomplishments

- Added `TestInlineUnitHintReprocessing` test class with 3 tests proving ISS-013 is fixed
- Implemented inline unit hint preservation in `core.py` by tracking `calc.unit_comment` and passing to renderer
- Updated `MarkdownRenderer` to accept tuple format `(result, inline_unit_hint)` for ISS-013 support
- Verified full test suite: 177 tests pass with no regressions
- Updated example snapshot `simple-units/output.md` to reflect new behavior

## Files Created/Modified

- `tests/test_inline_unit_hints.py` - Added `TestInlineUnitHintReprocessing` class with 3 tests
- `src/livemathtex/core.py` - Track inline unit hint from calculations and pass to renderer as tuple
- `src/livemathtex/render/markdown.py` - Support tuple format and use `effective_unit` for HTML comment
- `examples/simple-units/output.md` - Updated snapshot with new HTML comments

## Decisions Made

- **Tuple format for results dict**: Instead of modifying frozen MathBlock dataclass, pass inline unit hint as second element in tuple `(result, inline_unit_hint)`. Renderer handles both legacy string format and new tuple format.
- **HTML comment injection**: Inline hints `$E == [kJ]$` now produce `$E == 1000\ \text{kJ}$ <!-- [kJ] -->` in output. This preserves the hint for re-processing.
- **Backward compatibility**: HTML comments still take precedence if both inline and HTML comment syntax are present.

## Issues Encountered

- **FrozenInstanceError**: Initial attempt to modify `MathBlock.unit_comment` failed because dataclass is frozen. Solved by passing unit hint through results dict instead.
- **Test variable naming**: Test used `P` which conflicts with poise unit. Renamed to `Power_1`.

## Next Phase Readiness

Ready for Phase 3 (Fix Evaluation Unit Lookup for ISS-009) or Phase 4 if ISS-009 is deferred.
