from langchain.tools import tool

@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, such as '35 + 8' or '(120/400)*100'."""
    try:
        allowed_chars = set("0123456789+-*/(). %")
        if not set(expression) <= allowed_chars:
            return "Invalid expression."

        result = eval(expression, {"__builtins__": {}}, {})
        return f"Calculation result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"
