from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import os
from app.api.routers.eda import DATA_DIR
from app.core.ml import eda_utils
from app.core.agents.feature_engineering_agent.agent import FeatureEngineeringAgent, TransformationStep
from app.core.agents.feature_selection_agent.agent import FeatureSelectionAgent
# from app.core.agents.feature_agent import FeatureEngineeringAgent, TransformationStep
from app.core.ml.feature_engine import FeatureEngine
from app.core.utils.logger import SessionLogger

router = APIRouter(prefix="/features", tags=["features"])

class FeatureProposalRequest(BaseModel):
    filename: str
    problem_definition: str

class FeatureProposalResponse(BaseModel):
    steps: List[TransformationStep]

class ApplyFeaturesRequest(BaseModel):
    filename: str
    steps: List[TransformationStep]
    session_id: str = "default"

class FeatureRequest(BaseModel):
    filepath: str
    problem_definition: str

@router.post("/propose", response_model=FeatureProposalResponse)
async def propose_features(request: FeatureProposalRequest):
    filepath = f"{DATA_DIR}/{request.filename}"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load small sample for stats
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_parquet(filepath)
            
        stats = eda_utils.generate_eda_summary(df)
        stats_text = eda_utils.format_summary_for_llm(stats)
        
        agent = FeatureEngineeringAgent(session_id="default")
        plan = agent.propose_plan(stats_text, request.problem_definition)
        
        return FeatureProposalResponse(steps=plan.get('steps', []))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/engineer")
async def engineer_features(request: FeatureRequest):
    """
    Generates and applies feature engineering steps using FeatureEngineeringAgent.
    """
    try:
        # Initialize FeatureEngineeringAgent
        # Assuming request has session_id, if not we might need to add it to FeatureRequest schema
        # Current FeatureRequest: filepath, problem_definition. Missing session_id.
        # We can default to 'default' or update schema. Let's use 'default' for now as schema change is larger.
        agent = FeatureEngineeringAgent(session_id="default")

        # Run (We might need summary context, but for now passing basic info)
        # Ideally, we should fetch summary from previous steps or re-generate.
        # For this quick fix, we'll let the agent verify or error if missing context.
        # FeatureEngineeringAgent.run signature: run(input_text, context)
        
        context = {
            "file_path": request.filepath,
            "problem_definition": request.problem_definition,
            "eda_summary": {} # Warning: Missing summary might affect performance
        }
        
        result = agent.run("Engineer features", context)
        
        if result.get("status") == "error":
             raise HTTPException(status_code=500, detail=result.get("message"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply")
async def apply_features(request: ApplyFeaturesRequest):
    filepath = f"{DATA_DIR}/{request.filename}"
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_parquet(filepath)
        
        # Apply Logic
        engine = FeatureEngine()
        # Convert steps objects to dicts for the engine
        plan = {"steps": [step.dict() for step in request.steps]}
        
        transformed_df = engine.apply_plan(df, plan)
        
        # Save new file
        new_filename = f"transformed_{request.filename}"
        new_filepath = f"{DATA_DIR}/{new_filename}"
        
        if filepath.endswith('.csv'):
            transformed_df.to_csv(new_filepath, index=False)
        else:
            transformed_df.to_parquet(new_filepath, index=False)
            
        # Log to Session
        logger = SessionLogger(session_id=request.session_id)
        logger.log_step("Feature Engineering", f"Applied steps: {plan['steps']}", f"User approved plan for {request.filename}")
        
        return {
            "message": "Features applied successfully",
            "new_filename": new_filename,
            "new_filepath": new_filepath,
            "columns": transformed_df.columns.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
