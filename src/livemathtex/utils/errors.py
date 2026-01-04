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
