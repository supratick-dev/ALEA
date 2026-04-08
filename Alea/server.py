from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from environment import AleaEnvironment, load_tasks
from models import ResetRequest, ResetResponse, StateResponse, StepRequest, StepResponse

app = FastAPI(
    title="ALEA — Adaptive Learning Environment for Agents",
    description=(
        "A multi-task coding environment that provides structured, multi-dimensional "
        "reward signals (syntax, correctness, quality) for training RL agents on "
        "Python code repair and optimisation tasks."
    ),
    version="1.0.0",
)
env = AleaEnvironment()


# ── Frontend GUI ───────────────────────────────────────────────────────────────

# Mount static files (css, js)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", summary="Web GUI")
def serve_gui():
    """Returns the ALEA web interface."""
    return FileResponse("static/index.html")


# ── Health check ───────────────────────────────────────────────────────────────

@app.get("/health", summary="Health check")
def health() -> Dict[str, str]:
    """Returns 200 OK — used to verify the server is alive."""
    return {"status": "ok", "service": "alea"}


# ── Task catalogue ─────────────────────────────────────────────────────────────

class TaskSummary(BaseModel):
    task_id: str
    difficulty: str
    instructions: str
    max_steps: int
    visible_tests: List[str]


@app.get("/tasks", response_model=List[TaskSummary], summary="List all available tasks")
def list_tasks() -> List[TaskSummary]:
    """Returns metadata for every registered task."""
    tasks = load_tasks()
    return [
        TaskSummary(
            task_id=tid,
            difficulty=t["difficulty"],
            instructions=t["instructions"],
            max_steps=t.get("max_steps", 3),
            visible_tests=t.get("visible_tests", []),
        )
        for tid, t in sorted(tasks.items())
    ]


# ── Core environment endpoints ─────────────────────────────────────────────────

@app.post("/reset", response_model=ResetResponse, summary="Start a new episode")
def reset(payload: ResetRequest = None) -> ResetResponse:
    """
    Initialise a new episode.
    Pass `task_id` to select a specific task, or `difficulty` to pick one at random
    from that difficulty tier.
    """
    if payload is None:
        payload = ResetRequest()
        
    try:
        observation, state = env.reset(task_id=payload.task_id, difficulty=payload.difficulty)
        return ResetResponse(observation=observation, state=state)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/step", response_model=StepResponse, summary="Submit an action")
def step(payload: StepRequest) -> StepResponse:
    """
    Submit an agent action.  Returns shaped reward (syntax + test + quality scores),
    updated state, and (if not done) the next observation.
    """
    try:
        reward, state, next_observation = env.step(payload.action)
        return StepResponse(reward=reward, state=state, next_observation=next_observation)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/state", response_model=StateResponse, summary="Current environment state")
def state() -> StateResponse:
    """Returns the current episode state without advancing it."""
    try:
        return StateResponse(state=env.state())
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
