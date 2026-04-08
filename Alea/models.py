from typing import List, Optional

from pydantic import BaseModel, Field


class Observation(BaseModel):
    task_id: str
    difficulty: str = Field(..., description="easy | medium | hard")
    code_snippet: str
    instructions: str
    test_cases: List[str] = Field(default_factory=list)
    step_count: int = 0
    previous_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class Action(BaseModel):
    revised_code: str
    explanation: Optional[str] = None


class Reward(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    syntax_score: float = Field(..., ge=0.0, le=1.0)
    test_score: float = Field(..., ge=0.0, le=1.0)
    quality_score: float = Field(..., ge=0.0, le=1.0)
    feedback: str
    done: bool


class EnvironmentState(BaseModel):
    task_id: str
    difficulty: str
    step_count: int = 0
    max_steps: int = 3
    current_score: float = Field(default=0.0, ge=0.0, le=1.0)
    done: bool = False


class ResetRequest(BaseModel):
    task_id: Optional[str] = None
    difficulty: Optional[str] = Field(default=None, description="easy | medium | hard")


class ResetResponse(BaseModel):
    observation: Observation
    state: EnvironmentState


class StepRequest(BaseModel):
    action: Action


class StepResponse(BaseModel):
    reward: Reward
    state: EnvironmentState
    next_observation: Optional[Observation] = None


class StateResponse(BaseModel):
    state: EnvironmentState
