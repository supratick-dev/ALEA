"""
ALEA Baseline Inference Script
===============================
Runs an LLM agent through the ALEA environment for one episode per task.

Required environment variables:
  HF_TOKEN      — Hugging Face / OpenAI-compatible API key
  API_BASE_URL  — Base URL of the model endpoint (e.g. https://router.huggingface.co/v1)
  MODEL_NAME    — Model identifier (e.g. Qwen/Qwen2.5-72B-Instruct)

Optional environment variables:
  ALEA_BASE_URL — ALEA server URL (default: http://127.0.0.1:7860)

Usage:
  HF_TOKEN=... API_BASE_URL=... MODEL_NAME=... python inference.py
  HF_TOKEN=... API_BASE_URL=... MODEL_NAME=... python inference.py --difficulty hard
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict

import httpx
from openai import OpenAI

# ── LLM client — initialised from environment variables ───────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

if "api-inference.huggingface.co" in API_BASE_URL:
    print("[WARN] Overriding deprecated api-inference URL with router.huggingface.co", file=sys.stderr)
    API_BASE_URL = API_BASE_URL.replace("api-inference.huggingface.co", "router.huggingface.co")

if HF_TOKEN and API_BASE_URL:
    client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)
else:
    # Fallback: use default OpenAI client (OPENAI_API_KEY from env)
    client = OpenAI()

MODEL = MODEL_NAME

SYSTEM_PROMPT = (
    "You are a code review agent specialised in Python. "
    "Given a code snippet and instructions, return a JSON object with two keys:\n"
    '  "revised_code": the corrected / optimised Python code (string)\n'
    '  "explanation": a clear explanation of every change you made (string)\n'
    "Return strict JSON only — no markdown fences, no extra text."
)


# ── Prompt builder ─────────────────────────────────────────────────────────────

def _build_prompt(observation: Dict[str, Any]) -> str:
    visible_tests = "\n".join(observation.get("test_cases", []))
    prev_score = observation.get("previous_score")
    prev_line = f"\nPrevious step score: {prev_score:.4f}" if prev_score is not None else ""
    return (
        f"Task ID   : {observation['task_id']}\n"
        f"Difficulty: {observation['difficulty']}\n"
        f"Step      : {observation['step_count']}"
        f"{prev_line}\n\n"
        f"Instructions:\n{observation['instructions']}\n\n"
        f"Current code:\n```python\n{observation['code_snippet']}\n```\n\n"
        f"Visible tests:\n{visible_tests}\n\n"
        "Return JSON only."
    )


# ── Code extractor — handles both raw and markdown-fenced responses ───────────

def _extract_action(raw: str, fallback_code: str) -> Dict[str, str]:
    """Parse LLM response into {revised_code, explanation}."""
    # Strip markdown fences if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        return {"revised_code": fallback_code, "explanation": raw}

    revised_code = payload.get("revised_code") or fallback_code
    explanation = payload.get("explanation") or ""
    return {"revised_code": str(revised_code), "explanation": str(explanation)}


# ── LLM step ──────────────────────────────────────────────────────────────────

def _propose_action(observation: Dict[str, Any]) -> Dict[str, str]:
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_prompt(observation)},
            ],
        )
        raw = completion.choices[0].message.content or "{}"
    except Exception as exc:
        print(f"[WARN] LLM call failed: {exc}", file=sys.stderr)
        raw = "{}"

    return _extract_action(raw, observation["code_snippet"])


# ── Episode runner — mandatory log format ─────────────────────────────────────

def run_episode(base_url: str, difficulty: str | None = None, task_id: str | None = None) -> float:
    """
    Run a single episode against the ALEA server.
    """
    with httpx.Client(timeout=60.0) as http:
        # ── Reset ──────────────────────────────────────────────────────────
        reset_payload: Dict[str, Any] = {}
        if task_id:
            reset_payload["task_id"] = task_id
        if difficulty:
            reset_payload["difficulty"] = difficulty

        reset_resp = http.post(f"{base_url}/reset", json=reset_payload)
        reset_resp.raise_for_status()
        episode = reset_resp.json()

        observation: Dict[str, Any] = episode["observation"]
        done: bool = episode["state"]["done"]
        task_name = observation["task_id"]

        print(f"[START] task={task_name} env=alea model={MODEL}", flush=True)

        rewards: list[float] = []
        step = 0

        # ── Episode loop ───────────────────────────────────────────────────
        while not done:
            action = _propose_action(observation)

            step_resp = http.post(f"{base_url}/step", json={"action": action})
            step_resp.raise_for_status()
            step_payload = step_resp.json()

            reward_obj = step_payload["reward"]
            step += 1
            reward_val = float(reward_obj["score"])
            rewards.append(reward_val)
            done = reward_obj["done"]

            # Must not contain newlines
            action_str = "submit_code"
            
            print(f"[STEP] step={step} action={action_str} reward={reward_val:.2f} done={str(done).lower()} error=null", flush=True)

            next_obs = step_payload.get("next_observation")
            if next_obs is not None:
                observation = next_obs

        # The final step's reward in ALEA acts as the overall score
        final_score = rewards[-1] if rewards else 0.0
        success = final_score >= 0.85
        rewards_str = ",".join(f"{r:.2f}" for r in rewards)

        print(f"[END] success={str(success).lower()} steps={step} score={final_score:.3f} rewards={rewards_str}", flush=True)
        return final_score


# ── CLI entrypoint ─────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ALEA baseline inference — runs an LLM agent through one episode."
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("ALEA_BASE_URL", "http://127.0.0.1:7860"),
        help="ALEA server base URL (default: http://127.0.0.1:7860)",
    )
    parser.add_argument(
        "--difficulty",
        default=None,
        choices=["easy", "medium", "hard"],
        help="Filter to a specific difficulty level.",
    )
    parser.add_argument(
        "--task-id",
        default=None,
        help="Run a specific task by ID (e.g. hard-optimization-2).",
    )
    args = parser.parse_args()

    run_episode(
        base_url=args.base_url,
        difficulty=args.difficulty,
        task_id=args.task_id,
    )


if __name__ == "__main__":
    main()
