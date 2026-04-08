from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional

from graders.quality_grader import grade_quality
from graders.syntax_grader import grade_syntax
from graders.test_grader import grade_tests
from models import Action, EnvironmentState, Observation, Reward
from tasks.easy import EASY_TASKS
from tasks.hard import HARD_TASKS
from tasks.medium import MEDIUM_TASKS

TaskDef = Dict[str, Any]
TaskMap = Dict[str, TaskDef]

# Reward weights — must sum to 1.0
_W_SYNTAX = 0.30
_W_TESTS = 0.50
_W_QUALITY = 0.20

# Step penalty rate: each extra step beyond step 1 costs this much
_STEP_PENALTY = 0.05


def load_tasks() -> TaskMap:
    task_map: TaskMap = {}
    for bucket in (EASY_TASKS, MEDIUM_TASKS, HARD_TASKS):
        for task_id, task in bucket.items():
            task_map[task_id] = deepcopy(task)
    return task_map


def _compute_reward(
    syntax_score: float,
    test_score: float,
    quality_score: float,
    step_count: int,
) -> float:
    """
    Weighted composite reward with an efficiency step penalty.

    raw  = 0.30 × syntax + 0.50 × tests + 0.20 × quality
    shaped = max(0.0, raw − 0.05 × max(0, step_count − 1))

    The penalty encourages solving tasks in fewer steps, providing
    shaped reward signal across the entire trajectory.
    """
    raw = _W_SYNTAX * syntax_score + _W_TESTS * test_score + _W_QUALITY * quality_score
    step_penalty = _STEP_PENALTY * max(0, step_count - 1)
    shaped = max(0.0, raw - step_penalty)
    return round(shaped, 4)


class AleaEnvironment:
    def __init__(self, tasks: Optional[TaskMap] = None):
        self.tasks: TaskMap = tasks if tasks is not None else load_tasks()
        self._session: Dict[str, Any] = {}

    # ── helpers ────────────────────────────────────────────────────────────

    def _select_task(self, task_id: str | None, difficulty: str | None) -> tuple[str, TaskDef]:
        if task_id:
            task = self.tasks.get(task_id)
            if not task:
                raise LookupError(f"Unknown task_id: {task_id!r}")
            if difficulty and task["difficulty"] != difficulty:
                raise ValueError(
                    f"Task {task_id!r} has difficulty={task['difficulty']!r}, not {difficulty!r}."
                )
            return task_id, task

        for candidate_id, task in self.tasks.items():
            if difficulty is None or task["difficulty"] == difficulty:
                return candidate_id, task

        raise LookupError(f"No task found for difficulty={difficulty!r}.")

    # ── public API ─────────────────────────────────────────────────────────

    def reset(
        self,
        task_id: str | None = None,
        difficulty: str | None = None,
    ) -> tuple[Observation, EnvironmentState]:
        selected_id, selected_task = self._select_task(task_id, difficulty)
        self._session = {
            "task_id": selected_id,
            "task": deepcopy(selected_task),
            "step_count": 0,
            "current_code": selected_task["starter_code"],
            "current_score": 0.0,
            "done": False,
        }

        observation = Observation(
            task_id=selected_id,
            difficulty=selected_task["difficulty"],
            code_snippet=self._session["current_code"],
            instructions=selected_task["instructions"],
            test_cases=selected_task.get("visible_tests", []),
            step_count=0,
            previous_score=None,
        )
        return observation, self.state()

    def step(self, action: Action) -> tuple[Reward, EnvironmentState, Observation | None]:
        if not self._session:
            raise RuntimeError("Environment not initialised. Call /reset first.")
        if self._session["done"]:
            raise RuntimeError("Episode is already complete. Call /reset to start a new one.")
        if not action.revised_code.strip():
            raise ValueError("Action.revised_code cannot be empty.")

        task = self._session["task"]
        self._session["step_count"] += 1
        self._session["current_code"] = action.revised_code
        step_count = self._session["step_count"]

        # ── grade ──────────────────────────────────────────────────────────
        syntax_score, syntax_fb = grade_syntax(action.revised_code)
        test_score, test_fb = grade_tests(action.revised_code, task.get("hidden_tests", ""))
        quality_score, quality_fb = grade_quality(
            action.revised_code,
            action.explanation or "",
            task.get("keywords", []),
        )

        # ── shaped reward ──────────────────────────────────────────────────
        total_score = _compute_reward(syntax_score, test_score, quality_score, step_count)
        self._session["current_score"] = total_score

        max_steps = task.get("max_steps", 3)
        success_threshold = task.get("success_threshold", 0.95)
        self._session["done"] = (
            total_score >= success_threshold or step_count >= max_steps
        )

        reward = Reward(
            score=total_score,
            syntax_score=round(syntax_score, 4),
            test_score=round(test_score, 4),
            quality_score=round(quality_score, 4),
            feedback=f"{syntax_fb} | {test_fb} | {quality_fb}",
            done=self._session["done"],
        )
        env_state = self.state()

        next_observation: Observation | None = None
        if not self._session["done"]:
            next_observation = Observation(
                task_id=self._session["task_id"],
                difficulty=task["difficulty"],
                code_snippet=self._session["current_code"],
                instructions=task["instructions"],
                test_cases=task.get("visible_tests", []),
                step_count=step_count,
                previous_score=total_score,
            )

        return reward, env_state, next_observation

    def state(self) -> EnvironmentState:
        if not self._session:
            raise RuntimeError("Environment not initialised. Call /reset first.")

        task = self._session["task"]
        return EnvironmentState(
            task_id=self._session["task_id"],
            difficulty=task["difficulty"],
            step_count=self._session["step_count"],
            max_steps=task.get("max_steps", 3),
            current_score=self._session["current_score"],
            done=self._session["done"],
        )
