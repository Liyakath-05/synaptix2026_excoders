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
        // Hide the "Run" button for students
        const runBtn = document.querySelector('.btn-run, header button');
        if (runBtn) runBtn.style.display = 'none';

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
    }
};

/**
 * The Brain: Skill-Based Matching Algorithm
 * Fulfills: Explainable Ranking & Weighted Scoring
 */
async function runMatching() {
    const list = document.getElementById('results-list');
    list.innerHTML = "<div class='card'><div class='loader'></div> Calculating explainable Match Scores...</div>";

    try {
        const response = await fetch(`${API_BASE}/match`, { method: 'POST' });
        const data = await response.json();

        if (data.error) throw new Error(data.error);

        // Map data to the Explainable Ranking UI
        list.innerHTML = data.map(candidate => `
            <div class="card">
                <div class="score-ring">${candidate.score}%</div>
                <div class="details">
                    <h3>${candidate.name}</h3>
                    <p class="id">Roll No: ${candidate.roll}</p>
                    <div class="reasoning">
                        <strong>Match Reasoning:</strong>
                        <ul>
                            ${candidate.reasons.map(r => `<li>${r}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `).join('');

    } catch (error) {
        list.innerHTML = `
            <div class="card" style="border-color: #ef4444; color: #b91c1c;">
                <strong>Backend Error:</strong> ${error.message}. Please ensure main.py is running.
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