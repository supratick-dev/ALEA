import os
import re
import subprocess
import sys
import tempfile


def grade_quality(code: str, explanation: str, task_keywords: list[str]) -> tuple[float, str]:
    """
    Grades code complexity and explanation quality.

    Scoring:
    - 0.5 points: cyclomatic complexity (radon). Grade A→0.5, B→0.4, …, F→0.0
    - 0.5 points: explanation keyword coverage (ratio of keywords mentioned)

    Returns (score 0.0–1.0, feedback string).
    """

    # ── Step 1: Radon cyclomatic complexity (max 0.5) ──────────────────────
    # radon reads files; we write to a temp file rather than using stdin.
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            prefix="alea_radon_",
        ) as f:
            f.write(code)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, "-m", "radon", "cc", "-s", tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout

        # Extract grade letters: e.g. "  add - A (1)"
        grades = re.findall(r" - ([A-F]) ", output)

        if not grades:
            complexity_score = 0.3  # neutral default when no functions detected
            complexity_feedback = "Could not measure complexity (no functions found)."
        else:
            grade_map = {"A": 0.5, "B": 0.4, "C": 0.3, "D": 0.2, "E": 0.1, "F": 0.0}
            avg = sum(grade_map.get(g, 0.0) for g in grades) / len(grades)
            complexity_score = round(avg, 2)
            complexity_feedback = f"Complexity grades: {', '.join(grades)} → score {complexity_score:.2f}."

    except Exception as e:
        complexity_score = 0.0
        complexity_feedback = f"Complexity check failed: {e}"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    # ── Step 2: Explanation keyword coverage (max 0.5) ─────────────────────
    if not explanation or not explanation.strip():
        explanation_score = 0.0
        explanation_feedback = "No explanation provided."
    elif not task_keywords:
        # Task has no keywords — give full credit for any explanation
        explanation_score = 0.5
        explanation_feedback = "Explanation provided (no specific keywords required)."
    else:
        explanation_lower = explanation.lower()
        matched = [kw for kw in task_keywords if kw.lower() in explanation_lower]
        ratio = len(matched) / len(task_keywords)
        explanation_score = round(ratio * 0.5, 2)
        explanation_feedback = (
            f"Explanation covered {len(matched)}/{len(task_keywords)} key concepts "
            f"({', '.join(matched) or 'none'})."
        )

    total = round(complexity_score + explanation_score, 2)
    feedback = f"{complexity_feedback} {explanation_feedback}"
    return total, feedback