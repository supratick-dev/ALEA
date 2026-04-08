"""
Easy tasks — syntax & style fixes.
Each task has a genuine syntax error or PEP 8 violation that an agent must repair.
Grader breakdown: 0.3 × syntax + 0.5 × tests + 0.2 × quality
"""

EASY_TASKS = {
    # ── Task 1: Wrong operator (logic fix dressed as easy) ─────────────────
    "easy-syntax-1": {
        "task_id": "easy-syntax-1",
        "difficulty": "easy",
        "instructions": (
            "The function below should return the sum of two integers, "
            "but it uses the wrong operator. Fix the operator so all tests pass. "
            "Provide a brief explanation of what you changed."
        ),
        "starter_code": (
            "def add(a, b):\n"
            "    return a - b\n"
        ),
        "visible_tests": [
            "assert add(2, 3) == 5",
            "assert add(-1, 1) == 0",
        ],
        "hidden_tests": (
            "def test_add_positive():\n"
            "    assert add(7, 8) == 15\n\n"
            "def test_add_zero():\n"
            "    assert add(0, 0) == 0\n\n"
            "def test_add_negative():\n"
            "    assert add(-3, -4) == -7\n"
        ),
        "keywords": ["sum", "addition", "operator"],
        "max_steps": 3,
        "success_threshold": 0.95,
    },

    # ── Task 2: Real SyntaxError — missing colon + bad indentation ────────
    "easy-syntax-2": {
        "task_id": "easy-syntax-2",
        "difficulty": "easy",
        "instructions": (
            "The function below contains two syntax errors: a missing colon "
            "after the if-statement and incorrect indentation on the return. "
            "Fix both errors so the function returns True when a number is even, "
            "False otherwise."
        ),
        "starter_code": (
            "def is_even(n):\n"
            "    if n % 2 == 0\n"       # missing colon
            "        return True\n"
            "  return False\n"          # bad indentation
        ),
        "visible_tests": [
            "assert is_even(4) is True",
            "assert is_even(7) is False",
        ],
        "hidden_tests": (
            "def test_is_even_zero():\n"
            "    assert is_even(0) is True\n\n"
            "def test_is_even_negative_even():\n"
            "    assert is_even(-2) is True\n\n"
            "def test_is_even_negative_odd():\n"
            "    assert is_even(-3) is False\n"
        ),
        "keywords": ["syntax", "colon", "indentation", "even"],
        "max_steps": 3,
        "success_threshold": 0.95,
    },

    # ── Task 3: PEP 8 violations + unused import ──────────────────────────
    "easy-style-3": {
        "task_id": "easy-style-3",
        "difficulty": "easy",
        "instructions": (
            "The function below has three PEP 8 / style issues: "
            "(1) an unused import, "
            "(2) a variable name that conflicts with a built-in (l vs length), "
            "(3) a magic number with no context. "
            "Clean up the code so it passes pyflakes with no warnings and "
            "still returns the correct result. "
            "Explain each change you made."
        ),
        "starter_code": (
            "import os\n\n"             # unused import
            "def clamp(value, lo, hi):\n"
            "    l = hi - lo\n"         # 'l' looks like '1'; shadows nothing but is bad style
            "    if value < lo:\n"
            "        return lo\n"
            "    if value > hi:\n"
            "        return hi\n"
            "    return value\n"
        ),
        "visible_tests": [
            "assert clamp(5, 0, 10) == 5",
            "assert clamp(-1, 0, 10) == 0",
            "assert clamp(15, 0, 10) == 10",
        ],
        "hidden_tests": (
            "def test_clamp_at_lower():\n"
            "    assert clamp(0, 0, 10) == 0\n\n"
            "def test_clamp_at_upper():\n"
            "    assert clamp(10, 0, 10) == 10\n\n"
            "def test_clamp_negative_range():\n"
            "    assert clamp(-5, -10, -1) == -5\n"
        ),
        "keywords": ["unused import", "pep8", "variable name", "style"],
        "max_steps": 3,
        "success_threshold": 0.90,
    },
}
