const API_BASE = "http://127.0.0.1:8002";



window.onload = async function() {

    const role = sessionStorage.getItem('userType');

    const id = sessionStorage.getItem('userId');

    const resultsDiv = document.getElementById('results-list');



    // 1. Session Guard

    if (!role || !id) {

        window.location.href = 'login.html';

        return;

    }



    // Interactive Input Logic: Makes the text boxes glow when active

    const inputs = document.querySelectorAll('input');

    inputs.forEach(input => {

        input.addEventListener('focus', () => {

            input.style.boxShadow = "0 0 15px rgba(0, 242, 254, 0.4)";

            input.style.borderColor = "#00f2fe";

        });

        input.addEventListener('blur', () => {

            input.style.boxShadow = "none";

            input.style.borderColor = "rgba(255, 255, 255, 0.1)";

        });

    });



    if (role === 'student') {

        const navH1 = document.querySelector('nav h1');

        if (navH1) navH1.innerHTML = `Student <span>Profile</span>`;



        const inputArea = document.getElementById('staff-input-area');

        if (inputArea) inputArea.style.display = 'none';



        try {

            const res = await fetch(`${API_BASE}/student/${id}`);

            const data = await res.json();



            if (data.error) {

                resultsDiv.innerHTML = `<div class="card" style="border-color: #ef4444;">${data.error}</div>`;

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

<li>Python Competency: ${Math.round(data.skills.Python)}%</li>

<li>ML Competency: ${Math.round(data.skills.ML)}%</li>

</ul>

</div>

</div>

</div>`;



                const profileCard = resultsDiv.querySelector('.card');

                addInteractiveEffect(profileCard);

            }

        } catch (e) {

            resultsDiv.innerHTML = `<div class="card" style="border-color: #ef4444;">Error: Backend offline</div>`;

        }

    } else {

        const navH1 = document.querySelector('nav h1');

        if (navH1) navH1.innerHTML = `Staff <span>Matcher</span>`;

        const inputArea = document.getElementById('staff-input-area');

        if (inputArea) inputArea.style.display = 'block';

    }

};



/**

* Enhanced Visual Feedback for Cards (3D Tilt & Glow)

*/

function addInteractiveEffect(card) {

    card.addEventListener('mousemove', (e) => {

        const rect = card.getBoundingClientRect();

        const x = e.clientX - rect.left;

        const y = e.clientY - rect.top;



        card.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,0.12) 0%, transparent 80%)`;

        const angle = (Math.atan2(y - rect.height / 2, x - rect.width / 2) * 180 / Math.PI);

        card.style.setProperty('--angle', `${angle}deg`);



        // Slight 3D Tilt effect

        const rotateY = ((x - rect.width / 2) / rect.width) * 10;

        const rotateX = ((y - rect.height / 2) / rect.height) * -10;

        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;

    });



    card.addEventListener('mouseleave', () => {

        card.style.background = "rgba(255, 255, 255, 0.05)";

        card.style.setProperty('--angle', `0deg`);

        card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)`;

    });

}



/**

* Staff Matcher Logic (Improved Capturing & Validation)

*/

async function runMatching() {

    // 1. Capture the values

    const wsName = document.getElementById('ws-name').value;

    const pythonReq = document.getElementById('req-python').value;

    const mlReq = document.getElementById('req-ml').value;



    // DEBUG: Check your browser console (F12) to see if these show up

    console.log("Attempting Match:", { wsName, pythonReq, mlReq });



    // 2. Validation

    if (!wsName || pythonReq === "" || mlReq === "") {

        alert("Please fill in all three fields.");

        return;

    }



    const resultsList = document.getElementById('results-list');

    resultsList.innerHTML = '<div class="card"><div class="loader"></div> Processing...</div>';



    try {

        const response = await fetch(`${API_BASE}/match`, {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({

                workspace_name: wsName,

                min_python_percent: parseFloat(pythonReq),

                min_ml_percent: parseFloat(mlReq)

            })

        });



        const data = await response.json();

        resultsList.innerHTML = "";



        if (data.students && data.students.length > 0) {

            data.students.forEach(student => {

                const card = document.createElement('div');

                card.className = 'card';

                card.innerHTML = `

<div class="score-ring">✓</div>

<div class="details">

<h3>${student.name}</h3>

<p>Roll: ${student.roll}</p>

<p style="background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 0.85rem; margin-top: 5px; font-weight: 800;">

ELIGIBLE

</p>

<button onclick="viewStudentProfile('${student.roll}')" class="secondary" style="margin-top:10px; width: auto; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);">

View Full Info

</button>

</div>`;

                addInteractiveEffect(card);

                resultsList.appendChild(card);

            });

        } else {

            resultsList.innerHTML = '<div class="empty-state">No students found.</div>';

        }

    } catch (error) {

        console.error("Fetch Error:", error);

        alert("Connection Error. Check if backend is running on 8002.");

    }

}



async function viewStudentProfile(rollNo) {

    try {

        const res = await fetch(`${API_BASE}/student/${rollNo}`);

        const data = await res.json();

        if (data.error) alert(data.error);

        else alert(`NAME: ${data.name}\nROLL: ${data.roll}\nPYTHON: ${data.skills.Python}%\nML: ${data.skills.ML}%`);

    } catch (e) {

        alert("Data Fetch Error.");

    }

}



function logout() {

    sessionStorage.clear();

    window.location.href = 'login.html';

}