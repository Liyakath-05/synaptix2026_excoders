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
        try:
            num = float(clean_val)
            return num / 100 if num > 1.1 else num
        except ValueError:
            return 0.0
    return float(value)

# --- MODELS ---
class LoginRequest(BaseModel):
    userid: str
    password: str
    role: str

class RequirementRequest(BaseModel):
    workspace_name: str
    python_req: float
    ml_req: float

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
async def staff_match(req: RequirementRequest):
    """
    Filters students based on staff-defined internship requirements.
    Students are eligible if their percentages are >= the staff requirements.
    """
    try:
        if not os.path.exists(FILE_PATH):
            return {"error": "Missing data.csv file"}
            
        df = pd.read_csv(FILE_PATH)
        df.columns = df.columns.str.strip()
        
        eligible_students = []
        
        # Convert input percentages (e.g., 80) to decimal (0.8) for comparison
        req_p = req.python_req / 100
        req_m = req.ml_req / 100

        for _, row in df.iterrows():
            # Extract and Clean Student Skills
            p_val = clean_percent(row['full stock by python'])
            m_val = clean_percent(row['machine learning'])
            
            # Comparison Logic: Must be greater than or equal to staff requirement
            if p_val >= req_p and m_val >= req_m:
                eligible_students.append({
                    "name": row['name'],
                    "roll": row['roll no'],
                    "python_score": round(p_val * 100, 1),
                    "ml_score": round(m_val * 100, 1),
                    "message": f"Eligible for {req.workspace_name} Internship"
                })
            
        return {
            "workspace": req.workspace_name,
            "count": len(eligible_students),
            "students": sorted(eligible_students, key=lambda x: x['python_score'], reverse=True)
        }
    except Exception as e:
        return {"error": f"Filtering Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)