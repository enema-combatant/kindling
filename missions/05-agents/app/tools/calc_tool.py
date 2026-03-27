"""
Agent tool: calculate — safe math expression evaluation.

Uses Python's ast module to parse and evaluate expressions.
Only arithmetic operators and a whitelist of math functions are allowed.
Arbitrary code execution is not possible — the AST walker rejects
anything that isn't a number, operator, or allowed function call.
"""

import ast
import math
import operator


# Allowed operators — the only operations the calculator can perform
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Allowed functions — safe math functions only
_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "ceil": math.ceil,
    "floor": math.floor,
    "pi": math.pi,
    "e": math.e,
}


def _safe_ast_walk(node):
    """Recursively walk an AST node using only allowed operations."""
    if isinstance(node, ast.Expression):
        return _safe_ast_walk(node.body)

    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

    elif isinstance(node, ast.BinOp):
        op = _OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        left = _safe_ast_walk(node.left)
        right = _safe_ast_walk(node.right)
        return op(left, right)

    elif isinstance(node, ast.UnaryOp):
        op = _OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        return op(_safe_ast_walk(node.operand))

    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls are allowed")
        func_name = node.func.id
        func = _FUNCTIONS.get(func_name)
        if func is None:
            raise ValueError(f"Unknown function: {func_name}")
        args = [_safe_ast_walk(arg) for arg in node.args]
        return func(*args)

    elif isinstance(node, ast.Name):
        # Allow named constants like pi and e
        val = _FUNCTIONS.get(node.id)
        if val is not None and isinstance(val, (int, float)):
            return val
        raise ValueError(f"Unknown variable: {node.id}")

    elif isinstance(node, ast.List):
        return [_safe_ast_walk(el) for el in node.elts]

    elif isinstance(node, ast.Tuple):
        return tuple(_safe_ast_walk(el) for el in node.elts)

    else:
        raise ValueError(f"Unsupported expression type: {type(node).__name__}")


def calculate(expression: str) -> str:
    """
    Safely process a math expression using AST parsing.

    Supports: +, -, *, /, //, %, ** (power), parentheses,
    and functions: abs, round, min, max, sum, sqrt, log, log10, ceil, floor.
    Constants: pi, e.

    Examples: '2 + 3 * 4', 'round(2048 / 3, 2)', 'sqrt(144)', '120 * 0.8'
    """
    expression = expression.strip()
    if not expression:
        return "Error: empty expression"

    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_ast_walk(tree)
        return str(result)
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError) as e:
        return f"Error: {str(e)}"
