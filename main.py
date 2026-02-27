from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import pandas as pd
import uvicorn
import os
import json

app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- FILE PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, 'data.csv')
CONFIG_PATH = os.path.join(BASE_DIR, 'data.json')

# Login Database
USER_DB = {
    "2473A31163": "2473A31163",
    "2473A31257": "2473A31257",
    "2473A31269": "2473A31269",
    "2473A31208": "2473A31208",
    "2473A1": "2473A"
}

# --- HELPER FUNCTIONS ---
def clean_percent(value):
    """Removes % sign and converts string like '90%' or '0.9' to float 0.9"""
    if isinstance(value, str):
        clean_val = value.replace('%', '').strip()
        num = float(clean_val)
        return num / 100 if num > 1.1 else num
    return float(value)

# --- MODELS ---
class LoginRequest(BaseModel):
    userid: str
    password: str
    role: str

# --- ROUTES ---

@app.post("/login")
async def login_check(req: LoginRequest):
    if req.userid in USER_DB and USER_DB[req.userid] == req.password:
        return {"status": "success", "role": req.role}
    raise HTTPException(status_code=401, detail="Invalid ID or Password")

@app.get("/student/{roll_no}")
async def get_single_student(roll_no: str):
    try:
        if not os.path.exists(FILE_PATH):
            return {"error": f"Database file not found"}

        df = pd.read_csv(FILE_PATH)
        df.columns = df.columns.str.strip()
        df['roll no'] = df['roll no'].astype(str)
        
        student = df[df['roll no'] == roll_no]
        if student.empty:
            return {"error": "Student record not found"}
            
        row = student.iloc[0]
        p_val = clean_percent(row['full stock by python'])
        m_val = clean_percent(row['machine learning'])
        
        return {
            "name": row['name'],
            "roll": row['roll no'],
            "skills": {
                "Python": p_val,
                "ML": m_val
            }
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/match")
async def staff_match():
    try:
        # 1. Load Data & Config
        if not os.path.exists(FILE_PATH) or not os.path.exists(CONFIG_PATH):
            return {"error": "Missing data.csv or data.json file"}
            
        df = pd.read_csv(FILE_PATH)
        df.columns = df.columns.str.strip()
        
        with open(CONFIG_PATH) as f:
            config = json.load(f)

        # Accessing the Dynamic Configuration
        weights = config['weights']
        total_w = sum(weights.values())
        mastery_limit = config['thresholds']['mastery']
        min_exp_req = config['min_experience_months']
        
        results = []
        for _, row in df.iterrows():
            # 2. Extract and Clean Skills
            p_val = clean_percent(row['full stock by python'])
            m_val = clean_percent(row['machine learning'])
            
            # 3. Fairness logic: Check for experience_months column, default to 0 if missing
            # This handles the "Fairness-Aware" part of your problem statement
            exp = float(row.get('experience_months', 0))

            # 4. Weighted Scoring Calculation
            # Formula: ((Python*Weight) + (ML*Weight)) / Total Weight
            base_score = ((p_val * weights['python_weight']) + (m_val * weights['ml_weight'])) / total_w
            
            # 5. Fairness-Aware Boost (Experience Normalization)
            # Provides a max 10% boost for students with up to 2 years experience
            exp_boost = min(exp / 24, 0.1) 
            final_score = round((base_score + exp_boost) * 100, 1)

            # 6. Explainable Reasoning (XAI)
            reasons = []
            if p_val >= mastery_limit:
                reasons.append("Strong mastery in Python matches high-priority need.")
            if m_val >= mastery_limit:
                reasons.append("High ML competency provides strong technical depth.")
            if exp >= min_exp_req:
                reasons.append(f"Practical experience ({int(exp)} months) validates technical skills.")
            
            if not reasons:
                reasons = ["General competency match."]

            results.append({
                "name": row['name'],
                "roll": row['roll no'],
                "score": min(final_score, 100.0),
                "reasons": reasons
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)
    except Exception as e:
        return {"error": f"Algorithm Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)