async function runMatching() {
    const resultsDiv = document.getElementById('results-list');
    resultsDiv.innerHTML = "Processing competency matrices...";

    // Mock Data (In a real app, this comes from a database or form)
    const payload = {
        project: { required_skills: { "Python": 5, "React": 3 }, min_exp: 2 },
        candidates: [
            { name: "Alice Gupta", skills: { "Python": 5, "React": 4 }, experience: 3 },
            { name: "Bob Smith", skills: { "Python": 2, "React": 5 }, experience: 1 }
        ]
    };

    const response = await fetch('http://localhost:8000/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    const data = await response.json();
    renderResults(data);
}

function renderResults(data) {
    const resultsDiv = document.getElementById('results-list');
    resultsDiv.innerHTML = "";

    data.forEach(item => {
                resultsDiv.innerHTML += `
            <div class="card">
                <span class="score-badge">${item.score}%</span>
                <h3>${item.name}</h3>
                <div class="reasons">
                    <strong>Reasoning:</strong>
                    <ul>${item.reasons.map(r => `<li>${r}</li>`).join('')}</ul>
                </div>
            </div>
        `;
    });
}