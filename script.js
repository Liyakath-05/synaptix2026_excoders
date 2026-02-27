const API_BASE = "http://127.0.0.1:8002";

window.onload = async function() {
    const role = sessionStorage.getItem('userType');
    const id = sessionStorage.getItem('userId');
    const resultsDiv = document.getElementById('results-list');

    // 1. Session Guard: Redirect to login if session is empty
    if (!role || !id) {
        window.location.href = 'login.html';
        return;
    }

    if (role === 'student') {
        // --- STUDENT PROFILE VIEW ---
        document.querySelector('header h1, nav h1').innerHTML = `Student <span>Profile</span>`;
        // Hide the staff input area for students
        const inputArea = document.getElementById('staff-input-area');
        if (inputArea) inputArea.style.display = 'none';

        try {
            const res = await fetch(`${API_BASE}/student/${id}`);
            const data = await res.json();

            if (data.error) {
                resultsDiv.innerHTML = `<div class="card" style="border-color: red;">${data.error}</div>`;
            } else {
                resultsDiv.innerHTML = `
                    <div class="card" style="border-left: 5px solid #2563eb;">
                        <div class="score-ring">Hi</div>
                        <div class="details">
                            <h2>Welcome, ${data.name}</h2>
                            <p><strong>Roll No:</strong> ${data.roll}</p>
                            <div class="reasoning">
                                <strong>Your Technical Breakdown:</strong>
                                <ul>
                                    <li>Python Competency: ${Math.round(data.skills.Python * 100)}%</li>
                                    <li>ML Competency: ${Math.round(data.skills.ML * 100)}%</li>
                                </ul>
                            </div>
                        </div>
                    </div>`;
            }
        } catch (e) {
            resultsDiv.innerHTML = `<div class="card" style="border-color: red;">Error: Backend is offline on port 8002</div>`;
        }
    } else {
        // --- STAFF MATCHER VIEW ---
        const h1 = document.querySelector('header h1, nav h1');
        if (h1) h1.innerHTML = `Staff <span>Matcher</span>`;
        // Ensure input area is visible for staff
        const inputArea = document.getElementById('staff-input-area');
        if (inputArea) inputArea.style.display = 'block';
    }
};

/**
 * Staff Matcher Logic: Fetches students eligible based on workspace requirements
 */
async function runMatching() {
    const wsName = document.getElementById('ws-name').value;
    const pythonReq = document.getElementById('req-python').value;
    const mlReq = document.getElementById('req-ml').value;

    if (!wsName || !pythonReq || !mlReq) {
        alert("Please fill in all requirements!");
        return;
    }

    const resultsList = document.getElementById('results-list');
    resultsList.innerHTML = '<div class="card"><div class="loader"></div> Searching for eligible candidates...</div>';

    try {
        const response = await fetch(`${API_BASE}/match`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                workspace_name: wsName,
                python_req: parseFloat(pythonReq),
                ml_req: parseFloat(mlReq)
            })
        });

        const data = await response.json();
        resultsList.innerHTML = ""; // Clear loader

        if (data.students && data.students.length > 0) {
            resultsList.innerHTML = data.students.map(student => `
                <div class="card">
                    <div class="score-ring">${student.python_score}%</div>
                    <div class="details">
                        <h3>${student.name}</h3>
                        <p class="id">Roll No: ${student.roll}</p>
                        <p style="color: #22c55e; font-weight: bold; margin-top: 8px;">
                            ✓ ${student.message}
                        </p>
                    </div>
                </div>
            `).join('');
        } else {
            resultsList.innerHTML = '<div class="empty-state">No students met these specific requirements.</div>';
        }
    } catch (error) {
        resultsList.innerHTML = `
            <div class="card" style="border-color: #ef4444; color: #b91c1c;">
                <strong>Backend Error:</strong> Backend offline. Please ensure your FastAPI server is running.
            </div>`;
    }
}

/**
 * Logout and clear session
 */
function logout() {
    sessionStorage.clear();
    window.location.href = 'login.html';
}

/**
 * Spider-sense UI Effect
 */
(function() {
    const resultsList = document.getElementById('results-list');

    function updateCardSpiderState(card, near) {
        if (near) {
            card.setAttribute('data-spider', 'true');
            card.setAttribute('data-spider-near', 'true');
        } else {
            card.setAttribute('data-spider', 'false');
            card.setAttribute('data-spider-near', 'false');
        }
    }

    function bindCard(card) {
        updateCardSpiderState(card, false);
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const w = rect.width,
                h = rect.height;
            const thresh = Math.min(40, Math.max(20, Math.min(w, h) * 0.25));

            const near = x < thresh || (w - x) < thresh || y < thresh || (h - y) < thresh;
            updateCardSpiderState(card, near);
        });
        card.addEventListener('mouseleave', () => updateCardSpiderState(card, false));
    }

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((m) => {
            if (m.addedNodes.length) {
                m.addedNodes.forEach((node) => {
                    if (node instanceof HTMLElement) {
                        if (node.classList.contains('card')) bindCard(node);
                        node.querySelectorAll('.card').forEach(bindCard);
                    }
                });
            }
        });
    });

    if (resultsList) {
        observer.observe(resultsList, { childList: true, subtree: true });
        resultsList.querySelectorAll('.card').forEach(bindCard);
    }
})();