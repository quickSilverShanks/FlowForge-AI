from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
from app.api.routers.eda import DATA_DIR
from app.core.ml.evaluator import Evaluator

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

class EvaluationRequest(BaseModel):
    filename: str
    target: str
    sensitive_column: str = None
    metric: str = "accuracy"

@router.post("/fairness")
async def evaluate_fairness(request: EvaluationRequest):
    filepath = f"{DATA_DIR}/{request.filename}"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_parquet(filepath)
            
        evaluator = Evaluator()
        model = evaluator.load_best_model(metric=request.metric)
        
        if not model:
            raise HTTPException(status_code=404, detail="No trained model found")
            
        if request.sensitive_column and request.sensitive_column in df.columns:
            # Simple imputation for fairness check if needed, or assume preprocessed
            pass
        else:
            return {"message": "Sensitive column not found or not provided"}

        fairness_metrics = evaluator.evaluate_fairness(model, df, request.target, request.sensitive_column)
        return fairness_metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain")
async def explain_model(request: EvaluationRequest):
    filepath = f"{DATA_DIR}/{request.filename}"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_parquet(filepath)
            
        evaluator = Evaluator()
        model = evaluator.load_best_model(metric=request.metric)
        if not model:
            raise HTTPException(status_code=404, detail="No trained model found")
            
        explanation = evaluator.generate_explanation(model, df, request.target)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
