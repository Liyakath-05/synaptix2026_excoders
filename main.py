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
    "2473A31269": "2473A31269",
    "2473A31208": "2473A31208",
    "2473A1": "2473A"
}

# --- HELPER FUNCTIONS ---
def clean_percent(value):
    """Removes % sign and converts string like '90%' or '0.9' to float 0.9"""
    if value is None:
        return 0.0
    if isinstance(value, str):
        clean_val = value.replace('%', '').strip()
        try:
            num = float(clean_val)
            # Normalize: if user input 90, it becomes 0.9.
            return num / 100 if num > 1.1 else num
        except ValueError:
            return 0.0
    return float(value)

# --- MODELS ---
class LoginRequest(BaseModel):
    userid: str
    password: str
    role: str

class InternshipRequirement(BaseModel):
    workspace_name: str
    min_python_percent: float  
    min_ml_percent: float      

# --- ROUTES ---

@app.post("/login")
async def login_check(req: LoginRequest):
    if req.userid in USER_DB and USER_DB[req.userid] == req.password:
        return {"status": "success", "role": req.role}
    raise HTTPException(status_code=401, detail="Invalid ID or Password")

@app.get("/student/{roll_no}")
async def get_single_student(roll_no: str):
    """Fetches full details for a specific student by Roll Number"""
    try:
        if not os.path.exists(FILE_PATH):
            return {"error": "Database file not found"}

        df = pd.read_csv(FILE_PATH)
        # Normalize headers to handle hidden spaces or case issues
        df.columns = df.columns.str.strip().str.lower()
        df['roll no'] = df['roll no'].astype(str)
        
        student = df[df['roll no'] == roll_no]
        if student.empty:
            return {"error": "Student record not found"}
            
        row = student.iloc[0]
        
        # Returns all fields including Dept and Phone for the 'Full Info' view
        return {
            "name": row.get('name', 'Unknown'),
            "roll": row.get('roll no', roll_no),
            "dept": row.get('dept', 'N/A'),
            "phone": str(row.get('ph.no', 'N/A')),
            "skills": {
                "Python": row.get('full stock by python', '0%'),
                "ML": row.get('machine learning', '0%')
            }
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/match")
async def staff_match(req: InternshipRequirement):
    """Filters students based on staff criteria and returns matching candidates"""
    try:
        if not os.path.exists(FILE_PATH):
            return {"error": "data.csv not found"}
            
        df = pd.read_csv(FILE_PATH)
        df.columns = df.columns.str.strip().str.lower()
        
        eligible_students = []
        
        # Convert user criteria (e.g. 80) to float (0.8)
        req_p = req.min_python_percent / 100
        req_m = req.min_ml_percent / 100

        for _, row in df.iterrows():
            p_val = clean_percent(row.get('full stock by python', 0))
            m_val = clean_percent(row.get('machine learning', 0))
            
            if p_val >= req_p and m_val >= req_m:
                eligible_students.append({
                    "name": row.get('name', 'Unknown'),
                    "roll": str(row.get('roll no', '000')),
                    "dept": row.get('dept', 'N/A'),           # Captured for full info
                    "phone": str(row.get('ph.no', 'N/A')),    # Captured for full info
                    "python_score": row.get('full stock by python', '0%'),
                    "ml_score": row.get('machine learning', '0%'),
                    "workspace": req.workspace_name
                })
        
        # Sort by Python score descending
        sorted_students = sorted(eligible_students, 
                                 key=lambda x: clean_percent(x['python_score']), 
                                 reverse=True)
        
        return {"students": sorted_students}
    except Exception as e:
        return {"error": f"Filter Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)