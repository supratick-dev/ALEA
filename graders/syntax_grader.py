import ast
import subprocess
import sys


def grade_syntax(code: str) -> tuple[float, str]:
    """
    Returns a score (0.0–1.0) and feedback string.
    - 0.5 points: AST parse succeeds (no SyntaxError)
    - 0.5 points: pyflakes reports no warnings
    """

    # Step 1 — AST parse check (0.5 points)
    try:
        ast.parse(code)
        parse_score = 0.5
        parse_feedback = "Code parses successfully."
    except SyntaxError as e:
        return 0.0, f"Syntax error: {e}"

    # Step 2 — pyflakes check (0.5 points)
    # pyflakes reads from stdin when invoked as: python -m pyflakes -
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pyflakes", "-"],
            input=code,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.stdout.strip() == "":
            pyflakes_score = 0.5
            pyflakes_feedback = "No pyflakes warnings."
        else:
            pyflakes_score = 0.2
            pyflakes_feedback = f"Pyflakes warnings: {result.stdout.strip()}"
    except Exception as e:
        pyflakes_score = 0.0
        pyflakes_feedback = f"Pyflakes check failed: {e}"

    total = round(parse_score + pyflakes_score, 2)
    feedback = f"{parse_feedback} {pyflakes_feedback}"
    return total, feedback