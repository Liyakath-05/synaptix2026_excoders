from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import pandas as pd
import uvicorn
import os

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

# Login Database
USER_DB = {
    "2473A31163": "2473A31163",
    "2473A31257": "2473A31257",
    "2473A1": "2473A"
}

# --- HELPER FUNCTIONS ---
def clean_percent(value):
    """Removes % sign and converts string like '90%' or '0.9' to float 0.9"""
    if isinstance(value, str):
        clean_val = value.replace('%', '').strip()
        num = float(clean_val)
        # If the number is like 90, convert to 0.9. If it's already 0.9, keep it.
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
            return {"error": f"Database file not found at {FILE_PATH}"}

        df = pd.read_csv(FILE_PATH)
        df.columns = df.columns.str.strip() # Remove hidden spaces
        df['roll no'] = df['roll no'].astype(str)
        
        student = df[df['roll no'] == roll_no]
        if student.empty:
            return {"error": "Student record not found"}
            
        row = student.iloc[0]
        p_val = clean_percent(row['full stock by python'])
        m_val = clean_percent(row['machine learning'])
        
        return {
            "name": row['name'], # Now using cleaned column name
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
        if not os.path.exists(FILE_PATH):
            return {"error": "File not found"}
            
        df = pd.read_csv(FILE_PATH)
        # This line removes all hidden spaces from your Excel column headers
        df.columns = df.columns.str.strip() 
        
        results = []
        for _, row in df.iterrows():
            # Data Cleaning
            p_val = clean_percent(row['full stock by python'])
            m_val = clean_percent(row['machine learning'])
            
            # Weighted Scoring (Python: 5, ML: 4)
            weighted_score = (p_val * 5) + (m_val * 4)
            final_score = round((weighted_score / 9) * 100, 1)
            
            # Explainable AI Logic
            reasons = []
            if p_val >= 0.8:
                reasons.append("Strong mastery in Python matches high-priority need.")
            if m_val >= 0.8:
                reasons.append("High ML competency provides strong technical depth.")
            
            # Fallback if no specific logic triggers
            if not reasons:
                reasons = [f"Python Score: {int(p_val*100)}%", f"ML Score: {int(m_val*100)}%"]

            results.append({
                "name": row['name'], # Correctly targets the student's name
                "roll": row['roll no'],
                "score": min(final_score, 100),
                "reasons": reasons
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)
    except Exception as e:
        return {"error": f"Display Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)