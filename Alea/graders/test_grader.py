import os
import subprocess
import sys
import tempfile


def grade_tests(code: str, test_code: str) -> tuple[float, str]:
    """
    Runs test_code against the agent's submitted code using pytest.
    Returns score (0.0–1.0) based on fraction of tests passed.
    """
    if not test_code.strip():
        return 0.0, "No hidden tests configured for this task."

    # Combine the agent's code with the test harness
    full_code = code + "\n\n" + test_code

    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            prefix="alea_test_",
        ) as f:
            f.write(full_code)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, "-m", "pytest", tmp_path, "--tb=no", "-q", "--no-header"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = result.stdout + result.stderr

        # Parse pytest summary line robustly.
        # pytest -q can emit tokens in either order with trailing commas:
        #   "1 passed, 2 failed in 0.03s"  OR  "2 failed, 1 passed in 0.03s"
        # Strip commas before comparing so we match regardless of ordering.
        passed = 0
        failed = 0

        for line in output.split("\n"):
            parts = [p.rstrip(",") for p in line.strip().split()]
            for i, part in enumerate(parts):
                if part == "passed" and i > 0:
                    try:
                        passed = int(parts[i - 1])
                    except ValueError:
                        pass
                if part == "failed" and i > 0:
                    try:
                        failed = int(parts[i - 1])
                    except ValueError:
                        pass

        total_tests = passed + failed
        if total_tests == 0:
            # pytest may report "no tests ran" — treat as 0
            return 0.0, f"No tests were found or run. pytest output: {output[:200]}"

        score = round(passed / total_tests, 2)
        feedback = f"{passed}/{total_tests} tests passed."
        return score, feedback

    except subprocess.TimeoutExpired:
        return 0.0, "Code execution timed out (30s limit)."
    except Exception as e:
        return 0.0, f"Test runner error: {e}"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)