let currentTaskId = null;
let currentTaskDifficulty = null;

// DOM Elements
const taskListEl = document.getElementById('taskList');
const currentTaskTitle = document.getElementById('currentTaskTitle');
const difficultyBadge = document.getElementById('difficultyBadge');
const instructionsText = document.getElementById('instructionsText');
const visibleTestsCode = document.getElementById('visibleTestsCode');
const codeEditor = document.getElementById('codeEditor');
const explanationEditor = document.getElementById('explanationEditor');

const btnReset = document.getElementById('resetBtn');
const btnStep = document.getElementById('stepBtn');

const valStepCount = document.getElementById('valStepCount');
const valTotalScore = document.getElementById('valTotalScore');
const valStatus = document.getElementById('valStatus');
const valFeedback = document.getElementById('valFeedback');
const subScores = document.getElementById('subScores');
const valSyntax = document.getElementById('valSyntax');
const valTests = document.getElementById('valTests');
const valQuality = document.getElementById('valQuality');

// Fetch Tasks on Load
async function fetchTasks() {
    try {
        const res = await fetch('/tasks');
        const tasks = await res.json();
        renderTaskList(tasks);
    } catch (e) {
        taskListEl.innerHTML = '<div class="text-dim">Error loading tasks. Is the server running?</div>';
    }
}

function renderTaskList(tasks) {
    taskListEl.innerHTML = '';
    tasks.forEach(task => {
        const div = document.createElement('div');
        div.className = 'task-item';
        div.innerHTML = `
            <span class="task-id">${task.task_id}</span>
            <span class="badge ${task.difficulty}">${task.difficulty}</span>
        `;
        div.onclick = () => selectTask(task, div);
        taskListEl.appendChild(div);
    });
}

function selectTask(task, element) {
    // Update active styling
    document.querySelectorAll('.task-item').forEach(el => el.classList.remove('active'));
    element.classList.add('active');

    // Update state
    currentTaskId = task.task_id;
    currentTaskDifficulty = task.difficulty;

    // Update UI headers
    currentTaskTitle.textContent = task.task_id;
    difficultyBadge.textContent = task.difficulty;
    difficultyBadge.className = `badge ${task.difficulty}`;
    instructionsText.textContent = task.instructions;
    visibleTestsCode.textContent = task.visible_tests.join('\n');

    // Enable reset
    btnReset.disabled = false;
    btnStep.disabled = true;

    // Auto-reset when clicking a new task
    resetEpisode();
}

async function resetEpisode() {
    if (!currentTaskId) return;

    btnReset.textContent = 'Resetting...';
    btnReset.disabled = true;
    btnStep.disabled = true;

    try {
        const res = await fetch('/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: currentTaskId })
        });
        const data = await res.json();
        
        // Update UI with starting observation
        codeEditor.value = data.observation.code_snippet;
        explanationEditor.value = '';
        
        // Reset Dashboard
        valStepCount.textContent = '0';
        valTotalScore.textContent = '0.0000';
        valTotalScore.style.color = '';
        valStatus.textContent = 'In Progress';
        valFeedback.textContent = 'Episode started. Awaiting first step.';
        subScores.style.display = 'none';

        btnStep.disabled = false;
    } catch (e) {
        valFeedback.textContent = 'Error resetting environment.';
    } finally {
        btnReset.textContent = 'Reset Episode';
        btnReset.disabled = false;
    }
}

async function submitStep() {
    if (!currentTaskId) return;

    const revisedCode = codeEditor.value;
    const explanation = explanationEditor.value;

    btnStep.textContent = 'Evaluating...';
    btnStep.disabled = true;

    try {
        const res = await fetch('/step', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: {
                    revised_code: revisedCode,
                    explanation: explanation
                }
            })
        });
        
        if (!res.ok) {
            const errBody = await res.json();
            throw new Error(errBody.detail || 'Step failed');
        }

        const data = await res.json();
        const rw = data.reward;
        
        // Update Dashboard
        valStepCount.textContent = data.state.step_count;
        valTotalScore.textContent = rw.score.toFixed(4);
        
        if (rw.score >= 0.95) valTotalScore.style.color = 'var(--diff-easy)';
        else if (rw.score >= 0.5) valTotalScore.style.color = 'var(--diff-medium)';
        else valTotalScore.style.color = 'var(--diff-hard)';

        valStatus.textContent = rw.done ? 'Finished (Done)' : 'In Progress';
        valFeedback.textContent = rw.feedback;

        // Subscores
        subScores.style.display = 'block';
        valSyntax.textContent = rw.syntax_score.toFixed(2);
        valTests.textContent = rw.test_score.toFixed(2);
        valQuality.textContent = rw.quality_score.toFixed(2);

        // Update Observation if not done
        if (!rw.done && data.next_observation) {
            codeEditor.value = data.next_observation.code_snippet;
        }

        btnStep.disabled = rw.done;
    } catch (e) {
        valFeedback.textContent = `Error: ${e.message}`;
        btnStep.disabled = false;
    } finally {
        btnStep.textContent = 'Submit Step';
    }
}

// Bind Events
btnReset.addEventListener('click', resetEpisode);
btnStep.addEventListener('click', submitStep);

// Init
fetchTasks();
