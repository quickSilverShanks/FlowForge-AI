from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
import pandas as pd
import os
from app.api.routers.eda import DATA_DIR
from app.core.ml import eda_utils
from app.core.agents.modeling_agent import ModelingAgent, ModelingPlan
from app.core.flows.training_flow import run_training_flow

router = APIRouter(prefix="/training", tags=["training"])

class TrainingProposeRequest(BaseModel):
    filename: str
    problem_definition: str

class TrainingLaunchRequest(BaseModel):
    filename: str
    target: str
    problem_type: str
    configs: List[dict] # Accepting dict to match ModelingPlan schema
    metric: str
    session_id: str = "default"

@router.post("/propose", response_model=ModelingPlan)
async def propose_model(request: TrainingProposeRequest):
    filepath = f"{DATA_DIR}/{request.filename}"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load stats
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_parquet(filepath)
        
        stats = eda_utils.generate_eda_summary(df)
        stats_text = eda_utils.format_summary_for_llm(stats)
        
        agent = ModelingAgent()
        plan = agent.propose_models(request.problem_definition, stats_text)
        
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
async def start_training(request: TrainingLaunchRequest, background_tasks: BackgroundTasks):
    # Launch Prefect Flow in Background
    background_tasks.add_task(
        run_training_flow, 
        filename=request.filename,
        target=request.target,
        problem_type=request.problem_type,
        configs=request.configs,
        metric=request.metric,
        session_id=request.session_id
    )
    
    return {"message": "Training started in background", "tracking_url": os.getenv("PREFECT_UI_URL", "http://localhost:4200")}
