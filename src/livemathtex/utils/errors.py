class LiveMathTexError(Exception):
    """Base exception for livemathtex."""
    pass

class ParserError(LiveMathTexError):
    """Error during parsing."""
    pass

class EvaluationError(LiveMathTexError):
    """Error during evaluation."""
    pass

class UndefinedVariableError(EvaluationError):
    """Reference to an undefined variable."""
    pass


class UnitConversionWarning(Exception):
    """
    Warning for unit conversion failures (not calculation errors).

    Used when a calculation succeeds but the requested unit conversion
    fails due to dimension mismatch. Shows warning (orange) with SI fallback
    instead of error (red).
    """
    def __init__(self, message: str, current_unit: str, target_unit: str, si_value: str):
        super().__init__(message)
        self.current_unit = current_unit
        self.target_unit = target_unit
        self.si_value = si_value  # Value in SI base units as string
