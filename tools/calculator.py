import ast
import operator as op
import re
from typing import Union

# =========================
# 1. Allowed operators
# =========================

ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

# =========================
# 2. Financial functions (extensible)
# =========================

def calc_margin(revenue: float, cost: float) -> float:
    return (revenue - cost) / revenue * 100

def calc_growth(current: float, previous: float) -> float:
    return (current - previous) / previous * 100

ALLOWED_FUNCTIONS = {
    "margin": calc_margin,
    "growth": calc_growth,
}

# =========================
# 3. Expression Normalizer
# =========================

def normalize_expression(expr: str) -> str:
    """
    Normalize:
    - 120% → (120/100)
    - remove spaces
    """
    expr = expr.strip()
    expr = re.sub(r'(\d+(\.\d+)?)%', r'(\1/100)', expr)
    return expr

# =========================
# 4. Safe Evaluator
# =========================

class SafeCalculator:
    def evaluate(self, expression: str) -> Union[float, str]:
        try:
            expression = normalize_expression(expression)
            node = ast.parse(expression, mode="eval")
            return self._eval(node.body)
        except Exception as e:
            raise ValueError(f"Invalid expression: {expression}") from e

    def _eval(self, node):
        # numbers
        if isinstance(node, ast.Num):
            return node.n

        # binary operations
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in ALLOWED_OPERATORS:
                raise ValueError("Operator not allowed")

            left = self._eval(node.left)
            right = self._eval(node.right)
            return ALLOWED_OPERATORS[type(node.op)](left, right)

        # unary operations (negative)
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in ALLOWED_OPERATORS:
                raise ValueError("Unary operator not allowed")

            operand = self._eval(node.operand)
            return ALLOWED_OPERATORS[type(node.op)](operand)

        # function calls (financial)
        elif isinstance(node, ast.Call):
            func_name = node.func.id

            if func_name not in ALLOWED_FUNCTIONS:
                raise ValueError(f"Function '{func_name}' not allowed")

            args = [self._eval(arg) for arg in node.args]
            return ALLOWED_FUNCTIONS[func_name](*args)

        else:
            raise ValueError("Unsupported expression")

# =========================
# 5. LangChain Tool
# =========================

from langchain.tools import tool

calculator = SafeCalculator()

@tool
def calculator_tool(expression: str) -> str:
    """
    Deterministic calculator for financial and ESG use cases.

    Supports:
    - +, -, *, /, parentheses
    - percentages (e.g., 50%)
    - financial functions:
        - margin(revenue, cost)
        - growth(current, previous)

    Examples:
    - "(120/400)*100"
    - "margin(120, 80)"
    - "growth(150, 100)"
    """

    try:
        result = calculator.evaluate(expression)

        # 控制輸出格式（避免太長小數）
        if isinstance(result, float):
            result = round(result, 6)

        return str(result)

    except Exception as e:
        return f"Error: {str(e)}"