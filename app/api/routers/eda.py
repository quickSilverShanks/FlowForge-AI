from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import pandas as pd
import os
from app.core.ml import eda_utils
from app.core.agents.eda_agent import EDAAgent
from app.core.utils.logger import SessionLogger

router = APIRouter(prefix="/eda", tags=["eda"])

DATA_DIR = "app/data"

class EDARequest(BaseModel):
    filename: str
    problem_definition: str = None
    session_id: str = "default"

class EDAResponse(BaseModel):
    stats: dict
    analysis: str

@router.post("/analyze", response_model=EDAResponse)
async def analyze_data(request: EDARequest):
    filepath = f"{DATA_DIR}/{request.filename}"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load Data
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_parquet(filepath)
            
        # 1. Statistical Summary
        stats = eda_utils.generate_eda_summary(df)
        stats_text = eda_utils.format_summary_for_llm(stats)
        
        # 2. Agent Analysis
        agent = EDAAgent() # Uses environment variables for URL
        analysis_result = agent.analyze(stats_text, request.problem_definition)
        
        # 3. Log to Session
        logger = SessionLogger(session_id=request.session_id)
        logger.log_step("EDA", analysis_result)
        
        return EDAResponse(stats=stats, analysis=analysis_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
