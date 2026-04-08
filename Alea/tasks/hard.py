"""
Hard tasks — performance optimisation with written explanation.
Each function is correct but uses an inefficient algorithm.
Agents must return faster code AND explain the complexity improvement.
Grader breakdown: 0.3 × syntax + 0.5 × tests + 0.2 × quality
"""

HARD_TASKS = {
    # ── Task 1: Duplicate detection O(n²) → O(n) via set ─────────────────
    "hard-optimization-1": {
        "task_id": "hard-optimization-1",
        "difficulty": "hard",
        "instructions": (
            "The function below detects duplicates in O(n²) time using nested loops. "
            "Rewrite it to run in O(n) average time. "
            "Your explanation must describe: (1) the data structure you used, "
            "(2) the new time complexity, and (3) the space trade-off."
        ),
        "starter_code": (
            "def has_duplicates(items):\n"
            "    for i in range(len(items)):\n"
            "        for j in range(i + 1, len(items)):\n"
            "            if items[i] == items[j]:\n"
            "                return True\n"
            "    return False\n"
        ),
        "visible_tests": [
            "assert has_duplicates([1, 2, 3, 1]) is True",
            "assert has_duplicates([1, 2, 3, 4]) is False",
        ],
        "hidden_tests": (
            "import time\n\n"
            "def test_has_duplicates_correctness_true():\n"
            "    assert has_duplicates([4, 7, 9, 4]) is True\n\n"
            "def test_has_duplicates_correctness_false():\n"
            "    assert has_duplicates(list(range(2000))) is False\n\n"
            "def test_has_duplicates_performance():\n"
            "    data = list(range(5000)) + [1234]\n"
            "    start = time.time()\n"
            "    assert has_duplicates(data) is True\n"
            "    assert (time.time() - start) < 1.5\n"
        ),
        "keywords": ["set", "time complexity", "O(n)", "space trade-off"],
        "max_steps": 7,
        "success_threshold": 0.90,
    },

    # ── Task 2: Flatten nested list — recursion → iterative stack ─────────
    "hard-optimization-2": {
        "task_id": "hard-optimization-2",
        "difficulty": "hard",
        "instructions": (
            "The recursive flatten function below works correctly but risks "
            "RecursionError on deeply nested lists and has overhead from repeated "
            "list concatenation. "
            "Rewrite it using an explicit stack (iterative approach) to avoid "
            "recursion limits and reduce memory allocations. "
            "Explain: (1) how the stack replaces the call stack, "
            "(2) why list concatenation is avoided, "
            "(3) the time and space complexity of your solution."
        ),
        "starter_code": (
            "def flatten(lst):\n"
            "    result = []\n"
            "    for item in lst:\n"
            "        if isinstance(item, list):\n"
            "            result = result + flatten(item)  # O(n) concat each time\n"
            "        else:\n"
            "            result = result + [item]\n"
            "    return result\n"
        ),
        "visible_tests": [
            "assert flatten([1, [2, 3], [4, [5, 6]]]) == [1, 2, 3, 4, 5, 6]",
            "assert flatten([1, 2, 3]) == [1, 2, 3]",
        ],
        "hidden_tests": (
            "import sys\n\n"
            "def test_flatten_empty():\n"
            "    assert flatten([]) == []\n\n"
            "def test_flatten_deeply_nested():\n"
            "    # Build a list nested 200 levels deep — would cause RecursionError recursively\n"
            "    nested = [1]\n"
            "    for _ in range(200):\n"
            "        nested = [nested]\n"
            "    assert flatten(nested) == [1]\n\n"
            "def test_flatten_mixed():\n"
            "    assert flatten([[1, 2], [3, [4, 5]], 6]) == [1, 2, 3, 4, 5, 6]\n"
        ),
        "keywords": ["stack", "iterative", "recursion", "concatenation", "O(n)"],
        "max_steps": 7,
        "success_threshold": 0.90,
    },

    # ── Task 3: Top-k word frequency — sort → heap ────────────────────────
    "hard-optimization-3": {
        "task_id": "hard-optimization-3",
        "difficulty": "hard",
        "instructions": (
            "The function below counts word frequencies and returns the k most "
            "common words by sorting the entire frequency dictionary. "
            "For large texts this is O(n log n) in the number of unique words. "
            "Rewrite it using a min-heap of size k to achieve O(n log k) time. "
            "Explain: (1) why a min-heap is better than full sort for top-k, "
            "(2) the complexity improvement, "
            "(3) any edge cases you handled."
        ),
        "starter_code": (
            "def top_k_words(text, k):\n"
            "    counts = {}\n"
            "    for word in text.lower().split():\n"
            "        counts[word] = counts.get(word, 0) + 1\n"
            "    # Sort all words — O(n log n) where n = unique words\n"
            "    sorted_words = sorted(counts, key=lambda w: counts[w], reverse=True)\n"
            "    return sorted_words[:k]\n"
        ),
        "visible_tests": [
            "assert top_k_words('the cat sat on the mat the cat', 2) == ['the', 'cat']",
            "assert top_k_words('a b c', 2) == ['a', 'b'] or "
            "top_k_words('a b c', 2) == ['b', 'a'] or "
            "top_k_words('a b c', 2) == ['c', 'a']",
        ],
        "hidden_tests": (
            "import heapq, time\n\n"
            "def _reference_top_k(text, k):\n"
            "    counts = {}\n"
            "    for w in text.lower().split():\n"
            "        counts[w] = counts.get(w, 0) + 1\n"
            "    return [w for w, _ in heapq.nlargest(k, counts.items(), key=lambda x: x[1])]\n\n"
            "def test_top_k_correctness():\n"
            "    text = 'the cat sat on the mat the cat'\n"
            "    assert top_k_words(text, 1) == ['the']\n\n"
            "def test_top_k_large_k():\n"
            "    text = 'a a a b b c'\n"
            "    result = top_k_words(text, 10)  # k > unique words\n"
            "    assert set(result) == {'a', 'b', 'c'}\n\n"
            "def test_top_k_performance():\n"
            "    import random, string\n"
            "    words = [random.choice(string.ascii_lowercase) for _ in range(50_000)]\n"
            "    text = ' '.join(words)\n"
            "    start = time.time()\n"
            "    result = top_k_words(text, 5)\n"
            "    assert len(result) == 5\n"
            "    assert time.time() - start < 1.0\n"
        ),
        "keywords": ["heap", "heapq", "O(n log k)", "top-k", "complexity"],
        "max_steps": 7,
        "success_threshold": 0.90,
    },
}
