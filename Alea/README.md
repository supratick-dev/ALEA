# ALEA — Adaptive Learning Environment for Agents

ALEA is an **OpenEnv-compatible coding environment** designed for training and evaluating RL agents on Python code repair and optimisation tasks.

Unlike environments that return a single binary reward, ALEA decomposes every reward into **three independent sub-scores** — syntax, correctness, and quality — giving agents a rich, informative signal at every step of a trajectory.

---

## Design Philosophy

### Multi-Dimensional Reward Signal

Every call to `/step` returns a `Reward` object with four fields:

| Field | Weight | What it measures |
|-------|--------|-----------------|
| `syntax_score` | 0.30 | AST parse success + pyflakes clean |
| `test_score` | 0.50 | Hidden test suite pass rate |
| `quality_score` | 0.20 | Cyclomatic complexity (radon) + explanation keyword coverage |
| `score` | — | Weighted composite with step-efficiency penalty |

### Step-Penalty Reward Shaping

The composite reward is shaped to encourage solving tasks in fewer steps:

```
raw    = 0.30 × syntax + 0.50 × tests + 0.20 × quality
shaped = max(0.0, raw − 0.05 × max(0, step_count − 1))
```

This means the reward function provides learning signal **across the full trajectory**, not just at the final step.

---

## Task Difficulties

### Easy — Syntax & Style Fixes (max 3 steps)

| Task ID | Problem |
|---------|---------|
| `easy-syntax-1` | Wrong operator (`-` instead of `+`) |
| `easy-syntax-2` | Missing colon + bad indentation |
| `easy-style-3` | Unused import + PEP 8 violations |

Expected baseline score: **~0.85**

### Medium — Logic Bug Detection (max 5 steps)

| Task ID | Bug |
|---------|-----|
| `medium-bugfix-1` | Inverted condition in first non-repeating character |
| `medium-bugfix-2` | Off-by-one in binary search loop condition |
| `medium-bugfix-3` | Missing base case in recursive Fibonacci |

Expected baseline score: **~0.55**

### Hard — Performance Optimisation (max 7 steps)

| Task ID | Optimisation |
|---------|-------------|
| `hard-optimization-1` | Duplicate detection O(n²) → O(n) via set |
| `hard-optimization-2` | Recursive list flatten → iterative stack |
| `hard-optimization-3` | Top-k word frequency sort → min-heap |

Expected baseline score: **~0.35**

---

## Architecture

```text
alea/
├── environment.py          # Core AleaEnvironment class (reset / step / state)
├── tasks/
│   ├── easy.py             # 3 syntax & style fix tasks
│   ├── medium.py           # 3 logic bug tasks
│   └── hard.py             # 3 optimisation tasks
├── graders/
│   ├── syntax_grader.py    # ast.parse() + pyflakes
│   ├── test_grader.py      # pytest subprocess runner
│   └── quality_grader.py   # radon CC + explanation keyword coverage
├── models.py               # Pydantic: Observation, Action, Reward, ...
├── server.py               # FastAPI: /reset /step /state /tasks /
├── inference.py            # OpenAI-compatible baseline agent
├── openenv.yaml            # OpenEnv spec manifest
├── Dockerfile
└── requirements.txt
```

---

## API Reference

### `GET /`
Health check. Returns `{"status": "ok"}`. Used by HF Spaces uptime monitoring.

### `GET /tasks`
Lists all registered tasks with IDs, difficulty, instructions, and visible tests.

### `POST /reset`
Start a new episode.

**Request body:**
```json
{ "task_id": "hard-optimization-2" }
```
or
```json
{ "difficulty": "medium" }
```

**Response:** `{ "observation": {...}, "state": {...} }`

### `POST /step`
Submit an agent action.

**Request body:**
```json
{
  "action": {
    "revised_code": "def add(a, b):\n    return a + b\n",
    "explanation": "Changed subtraction to addition."
  }
}
```

**Response:** `{ "reward": {...}, "state": {...}, "next_observation": {...} }`

### `GET /state`
Returns current episode state without advancing it.

---

## Running Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the server
```bash
uvicorn server:app --host 0.0.0.0 --port 7860 --reload
```

### 3. Smoke-test endpoints
```bash
# Health check
curl http://localhost:7860/

# List tasks
curl http://localhost:7860/tasks

# Start an episode
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}'

# Submit a step
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"revised_code": "def add(a, b):\n    return a + b\n", "explanation": "Fixed operator"}}'
```

---

## Running the Baseline Agent

The `inference.py` script runs an LLM through one episode and prints the mandatory evaluation log format.

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HF_TOKEN` | Yes | API key for the LLM endpoint |
| `API_BASE_URL` | Yes | OpenAI-compatible base URL |
| `MODEL_NAME` | Yes | Model identifier |
| `ALEA_BASE_URL` | No | ALEA server URL (default: `http://127.0.0.1:7860`) |

### Usage
```bash
export HF_TOKEN=hf_...
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct

# Run one episode (auto-picks an easy task)
python inference.py --difficulty easy

# Run a specific task
python inference.py --task-id hard-optimization-1
```

### Log format (validated by auto-evaluator)
```
[START] task_id=easy-syntax-1 difficulty=easy
[STEP] step=1 score=0.9500 done=True
[END] task_id=easy-syntax-1 total_reward=0.9500 steps=1
```

---

## Docker

### Build
```bash
docker build -t alea-env .
```

### Run
```bash
docker run -p 7860:7860 alea-env
```

The container exposes port 7860 and starts the FastAPI server automatically.

---

## Pydantic Models

```python
class Observation(BaseModel):
    task_id: str
    difficulty: str           # "easy" | "medium" | "hard"
    code_snippet: str
    instructions: str
    test_cases: List[str]     # visible tests (subset of hidden suite)
    step_count: int
    previous_score: Optional[float]

class Action(BaseModel):
    revised_code: str
    explanation: Optional[str] = None

class Reward(BaseModel):
    score: float              # shaped composite reward 0.0–1.0
    syntax_score: float
    test_score: float
    quality_score: float
    feedback: str             # human-readable per-grader feedback
    done: bool
```
