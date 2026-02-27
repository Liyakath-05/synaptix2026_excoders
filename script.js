const API_BASE = "http://127.0.0.1:8002";

window.onload = async function() {
    const role = sessionStorage.getItem('userType');
    const id = sessionStorage.getItem('userId');
    const resultsDiv = document.getElementById('results-list');

    // Redirect to login if session is empty
    if (!role || !id) {
        window.location.href = 'login.html';
        return;
    }

    if (role === 'student') {
        // --- STUDENT VIEW ---
        document.querySelector('header h1').innerHTML = `Student <span>Profile</span>`;
        document.querySelector('header button').style.display = 'none';

        try {
            const res = await fetch(`${API_BASE}/student/${id}`);
            const data = await res.json();

            if (data.error) {
                resultsDiv.innerHTML = `<div class="card">${data.error}</div>`;
            } else {
                resultsDiv.innerHTML = `
                    <div class="card" style="border-left: 5px solid #28a745;">
                        <h2>Welcome, ${data.name}</h2>
                        <p><strong>Roll No:</strong> ${data.roll}</p>
                        <div class="reasons">
                            <p>Python Competency: ${Math.round(data.skills.Python * 100)}%</p>
                            <p>ML Competency: ${Math.round(data.skills.ML * 100)}%</p>
                        </div>
                    </div>`;
            }
        } catch (e) {
            resultsDiv.innerHTML = `<div class="card">Error: Backend is offline on port 8002</div>`;
        }
    } else {
        // --- STAFF VIEW ---
        document.querySelector('header h1').innerHTML = `Staff <span>Matcher</span>`;
    }
};

async function runMatching() {
    const resultsDiv = document.getElementById('results-list');
    resultsDiv.innerHTML = "<p>Algorithm is calculating weighted scores...</p>";

    try {
        // Triggering the POST /match endpoint
        const res = await fetch(`${API_BASE}/match`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();

        // Map the backend results to HTML cards
        resultsDiv.innerHTML = data.map(candidate => `
            <div class="card">
                <span class="score-badge">${candidate.score}%</span>
                <h3>${candidate.name}</h3>
                <p style="color:#666; font-size:0.85em;">ID: ${candidate.roll}</p>
                <div class="reasons">
                    <strong>Match Reasoning:</strong>
                    <ul>${candidate.reasons.map(r => `<li>${r}</li>`).join('')}</ul>
                </div>
            </div>
        `).join('');
    } catch (e) {
        alert("Failed to connect to the backend algorithm on port 8002");
    }
}