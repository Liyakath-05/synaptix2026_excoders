const API_BASE = "http://127.0.0.1:8000";

window.onload = async function() {
    const role = sessionStorage.getItem('userType');
    const id = sessionStorage.getItem('userId');
    const resultsDiv = document.getElementById('results-list');

    if (!role || !id) {
        if (!window.location.href.includes('login.html')) {
            window.location.href = 'login.html';
        }
        return;
    }

    if (role === 'student') {
        document.querySelector('header h1').innerHTML = `Student <span>Profile</span>`;
        const btn = document.querySelector('header button');
        if (btn) btn.style.display = 'none';

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
                            <p>Python Proficiency: ${Math.round(data.skills.Python * 100)}%</p>
                            <p>ML Proficiency: ${Math.round(data.skills.ML * 100)}%</p>
                        </div>
                    </div>`;
            }
        } catch (e) {
            resultsDiv.innerHTML = `<div class="card">Error: Backend is offline on port 8001</div>`;
        }
    } else {
        document.querySelector('header h1').innerHTML = `Staff <span>Matcher</span>`;
    }
};

async function runMatching() {
    const resultsDiv = document.getElementById('results-list');
    resultsDiv.innerHTML = "<p>Calculating Weighted Scores...</p>";

    try {
        const res = await fetch(`${API_BASE}/match`, { method: 'POST' });
        const data = await res.json();

        resultsDiv.innerHTML = data.map(s => `
            <div class="card">
                <span class="score-badge">${s.score}%</span>
                <h3>${s.name}</h3>
                <p style="color:#666; font-size:0.85em;">ID: ${s.roll}</p>
                <div class="reasons">
                    <strong>Explainable Factors:</strong>
                    <ul>${s.reasons.map(r => `<li>${r}</li>`).join('')}</ul>
                </div>
            </div>
        `).join('');
    } catch (e) {
        alert("Failed to connect to backend on port 8002");
    }
}