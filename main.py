from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List
import pandas as pd
import uvicorn

app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Login Database based on your requirements
USER_DB = {
    "2473A31163": "2473A31163", # Student 1
    "2473A31257": "2473A31257", # Student 2
    "2473A1": "2473A"           # Staff 1
}

class LoginRequest(BaseModel):
    userid: str
    password: str
    role: str

@app.post("/login")
async def login_check(req: LoginRequest):
    if req.userid in USER_DB and USER_DB[req.userid] == req.password:
        return {"status": "success", "role": req.role}
    raise HTTPException(status_code=401, detail="Invalid ID or Password")

@app.get("/student/{roll_no}")
async def get_single_student(roll_no: str):
    try:
        # Load data and strip column whitespace
        df = pd.read_csv('students.xlsx - Sheet1.csv')
        df.columns = df.columns.str.strip()
        df['roll no'] = df['roll no'].astype(str)
        
        student = df[df['roll no'] == roll_no]
        
        if student.empty:
            return {"error": "Student record not found in CSV"}
            
        row = student.iloc[0]
        return {
            "name": row.get('name ', row.get('name', 'Unknown')),
            "roll": row['roll no'],
            "skills": {
                "Python": float(row['full stock by python']),
                "ML": float(row['machine learning'])
            }
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/match")
async def staff_match():
    try:
        df = pd.read_csv('students.xlsx - Sheet1.csv')
        df.columns = df.columns.str.strip()
        
        results = []
        for _, row in df.iterrows():
            # Weighted Scoring: Python(5) + ML(4) = Total Weight (9)
            p_val = float(row['full stock by python'])
            m_val = float(row['machine learning'])
            
            score = round(((p_val * 5 + m_val * 4) / 9) * 100, 1)
            
            results.append({
                "name": row.get('name ', row.get('name', 'Unknown')),
                "roll": row['roll no'],
                "score": score,
                "reasons": [
                    f"Python: {int(p_val*100)}% (Weight 5)",
                    f"ML: {int(m_val*100)}% (Weight 4)"
                ]
            })
        return sorted(results, key=lambda x: x['score'], reverse=True)
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Switching to 8002 to ensure a fresh start
    uvicorn.run(app, host="127.0.0.1", port=8000)