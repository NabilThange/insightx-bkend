"""Safe Python execution for analytics."""
import ast
import subprocess
import json
import tempfile
import os
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from scipy import stats


# Allowed imports for safe execution
ALLOWED_MODULES = {
    "pandas",
    "numpy",
    "scipy",
    "scipy.stats",
    "math",
    "statistics",
    "json",
}

# Dangerous built-ins to block
DANGEROUS_BUILTINS = {
    "open",
    "exec",
    "eval",
    "__import__",
    "compile",
    "globals",
    "locals",
    "vars",
    "dir",
    "getattr",
    "setattr",
    "delattr",
    "hasattr",
}


class ASTValidator(ast.NodeVisitor):
    """Validate AST for dangerous operations."""

    def __init__(self):
        self.errors = []

    def visit_Import(self, node: ast.Import) -> None:
        """Check import statements."""
        for alias in node.names:
            module = alias.name.split(".")[0]
            if module not in ALLOWED_MODULES:
                self.errors.append(f"Import of '{module}' not allowed")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check from...import statements."""
        if node.module:
            module = node.module.split(".")[0]
            if module not in ALLOWED_MODULES:
                self.errors.append(f"Import from '{module}' not allowed")

    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls."""
        if isinstance(node.func, ast.Name):
            if node.func.id in DANGEROUS_BUILTINS:
                self.errors.append(f"Call to '{node.func.id}' not allowed")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Check attribute access."""
        if node.attr.startswith("_"):
            self.errors.append(f"Access to private attribute '{node.attr}' not allowed")
        self.generic_visit(node)


def validate_python_code(code: str) -> Tuple[bool, str]:
    """Validate Python code for safety.

    Args:
        code: Python code string

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax error: {str(e)}"

    validator = ASTValidator()
    validator.visit(tree)

    if validator.errors:
        return False, "; ".join(validator.errors)

    return True, ""


def run_python(
    code: str,
    df: pd.DataFrame,
    result_df: pd.DataFrame = None,
    timeout_s: int = 10,
) -> Tuple[Dict[str, Any], str]:
    """Execute safe Python code for analytics.

    Args:
        code: Python code to execute
        df: Input dataframe (the full dataset)
        result_df: Optional dataframe from SQL query
        timeout_s: Timeout in seconds

    Returns:
        Tuple of (results_dict, execution_summary)

    Raises:
        ValueError: If code is invalid
        RuntimeError: If execution fails or times out
    """
    # Validate code
    is_valid, error_msg = validate_python_code(code)
    if not is_valid:
        raise ValueError(f"Invalid Python code: {error_msg}")

    # Prepare safe locals
    safe_locals = {
        "pd": pd,
        "np": np,
        "stats": stats,
        "df": df,
        "result_df": result_df,
        "math": __import__("math"),
        "json": json,
    }

    # Write code to temp file for subprocess execution
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
    tmp.write(code)
    tmp.close()

    try:
        # Execute in subprocess with timeout
        result = subprocess.run(
            ["python", tmp.name],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            env={**os.environ, "PYTHONPATH": "."},
        )

        if result.returncode != 0:
            raise RuntimeError(f"Execution failed: {result.stderr}")

        # Parse output
        output = result.stdout.strip()
        if output:
            try:
                results = json.loads(output)
            except json.JSONDecodeError:
                results = {"output": output}
        else:
            results = {}

        summary = f"Python execution completed successfully"
        return results, summary

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Python execution timed out after {timeout_s}s")
    except Exception as e:
        raise RuntimeError(f"Python execution failed: {str(e)}")
    finally:
        os.unlink(tmp.name)


def create_safe_python_wrapper(code: str) -> str:
    """Wrap user code with safe execution context.

    Args:
        code: User's Python code

    Returns:
        Wrapped code that can be executed safely
    """
    wrapper = f"""
import pandas as pd
import numpy as np
from scipy import stats
import json
import sys

# User code
{code}

# Output results as JSON
if 'results' in locals():
    print(json.dumps(results))
"""
    return wrapper
