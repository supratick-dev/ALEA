"""
Medium tasks — logic bug detection and fix.
Each function runs without crashing but returns wrong output on edge cases.
Grader breakdown: 0.3 × syntax + 0.5 × tests + 0.2 × quality
"""

MEDIUM_TASKS = {
    # ── Task 1: First non-repeating character (inverted condition) ─────────
    "medium-bugfix-1": {
        "task_id": "medium-bugfix-1",
        "difficulty": "medium",
        "instructions": (
            "The function below should return the first character in the string "
            "that appears exactly once. It runs without errors but returns the "
            "wrong character on most inputs. "
            "Identify the bug, fix it, and explain what was wrong."
        ),
        "starter_code": (
            "def first_non_repeating_char(text):\n"
            "    counts = {}\n"
            "    for ch in text:\n"
            "        counts[ch] = counts.get(ch, 0) + 1\n"
            "    for ch in text:\n"
            "        if counts[ch] > 1:\n"   # BUG: should be == 1
            "            return ch\n"
            "    return None\n"
        ),
        "visible_tests": [
            "assert first_non_repeating_char('aabbcde') == 'c'",
            "assert first_non_repeating_char('aabbcc') is None",
        ],
        "hidden_tests": (
            "def test_first_non_repeating_found():\n"
            "    assert first_non_repeating_char('swiss') == 'w'\n\n"
            "def test_first_non_repeating_none():\n"
            "    assert first_non_repeating_char('xxyyzz') is None\n\n"
            "def test_first_non_repeating_single():\n"
            "    assert first_non_repeating_char('z') == 'z'\n"
        ),
        "keywords": ["condition", "non-repeating", "comparison", "bug"],
        "max_steps": 5,
        "success_threshold": 0.95,
    },

    # ── Task 2: Binary search off-by-one ──────────────────────────────────
    "medium-bugfix-2": {
        "task_id": "medium-bugfix-2",
        "difficulty": "medium",
        "instructions": (
            "The binary search below fails to find the target when it sits "
            "at the last index of the list. "
            "Fix the off-by-one error in the loop condition and explain why "
            "your change is correct."
        ),
        "starter_code": (
            "def binary_search(nums, target):\n"
            "    lo, hi = 0, len(nums) - 1\n"
            "    while lo < hi:\n"         # BUG: should be lo <= hi
            "        mid = (lo + hi) // 2\n"
            "        if nums[mid] == target:\n"
            "            return mid\n"
            "        elif nums[mid] < target:\n"
            "            lo = mid + 1\n"
            "        else:\n"
            "            hi = mid - 1\n"
            "    return -1\n"
        ),
        "visible_tests": [
            "assert binary_search([1, 3, 5, 7, 9], 5) == 2",
            "assert binary_search([1, 3, 5, 7, 9], 1) == 0",
        ],
        "hidden_tests": (
            "def test_bs_last_element():\n"
            "    assert binary_search([1, 3, 5, 7, 9], 9) == 4\n\n"
            "def test_bs_not_found():\n"
            "    assert binary_search([1, 3, 5, 7, 9], 4) == -1\n\n"
            "def test_bs_single_element():\n"
            "    assert binary_search([42], 42) == 0\n"
        ),
        "keywords": ["off-by-one", "loop condition", "binary search", "boundary"],
        "max_steps": 5,
        "success_threshold": 0.95,
    },

    # ── Task 3: Recursive fibonacci missing base case ──────────────────────
    "medium-bugfix-3": {
        "task_id": "medium-bugfix-3",
        "difficulty": "medium",
        "instructions": (
            "The recursive Fibonacci function below hits infinite recursion for "
            "n=0 and n=1 because the base cases are incomplete. "
            "Fix the base cases so the function returns the correct Fibonacci numbers "
            "for all non-negative n, and explain what you changed."
        ),
        "starter_code": (
            "def fibonacci(n):\n"
            "    if n == 1:\n"             # BUG: missing n == 0 base case
            "        return 1\n"
            "    return fibonacci(n - 1) + fibonacci(n - 2)\n"
        ),
        "visible_tests": [
            "assert fibonacci(5) == 5",
            "assert fibonacci(6) == 8",
        ],
        "hidden_tests": (
            "def test_fibonacci_zero():\n"
            "    assert fibonacci(0) == 0\n\n"
            "def test_fibonacci_one():\n"
            "    assert fibonacci(1) == 1\n\n"
            "def test_fibonacci_ten():\n"
            "    assert fibonacci(10) == 55\n"
        ),
        "keywords": ["base case", "recursion", "fibonacci", "termination"],
        "max_steps": 5,
        "success_threshold": 0.95,
    },
}
