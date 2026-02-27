from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# Allow Frontend to talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Project(BaseModel):
    required_skills: Dict[str, int] # Skill: Importance (1-5)
    min_exp: int

class Candidate(BaseModel):
    name: str
    skills: Dict[str, int] # Skill: Proficiency (1-5)
    experience: int

@app.post("/match")
async def match_candidates(project: Project, candidates: List[Candidate]):
    results = []
    
    for c in candidates:
        score = 0
        reasons = []
        total_weight = sum(project.required_skills.values())
        
        for skill, importance in project.required_skills.items():
            user_level = c.skills.get(skill, 0)
            
            # Weighted Scoring Formula
            contribution = (user_level / 5) * importance
            score += contribution
            
            # Generate Explainable Reasoning
            if user_level >= 4:
                reasons.append(f"Strong mastery in {skill} matches high-priority need.")
            elif user_level == 0:
                reasons.append(f"Missing {skill}, which is a required competency.")

        # Fairness-Aware Experience Normalization
        exp_boost = min(c.experience / project.min_exp, 1.1) 
        final_score = round((score / total_weight) * 100 * exp_boost, 1)

        results.append({
            "name": c.name,
            "score": min(final_score, 100),
            "reasons": reasons
        })

    return sorted(results, key=lambda x: x['score'], reverse=True)