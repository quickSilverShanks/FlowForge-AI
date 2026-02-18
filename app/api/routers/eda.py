from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import pandas as pd
import os
from app.core.ml import eda_utils
from app.core.agents.data_agent.agent import DataAgent
# from app.core.agents.eda_agent import EDAAgent # Removed
from app.core.utils.logger import SessionLogger

router = APIRouter(prefix="/eda", tags=["eda"])

DATA_DIR = "app/data"

from typing import Optional

class EDARequest(BaseModel):
    filename: str
    problem_definition: Optional[str] = None
    session_id: str = "default"
    target_col: Optional[str] = None

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
            
        # 1. Handle Duplicates (Drop and report)
        initial_rows = len(df)
        duplicates_count = df.duplicated().sum()
        
        if duplicates_count > 0:
            df.drop_duplicates(inplace=True)
            # Overwrite file with cleaned data
            if filepath.endswith('.csv'):
                df.to_csv(filepath, index=False)
            else:
                df.to_parquet(filepath, index=False)
            
        # 2. Statistical Summary (on cleaned data)
        stats = eda_utils.generate_eda_summary(df)
        stats["duplicates"] = int(duplicates_count) # Explicitly set original duplicate count
        stats["rows_original"] = int(initial_rows)
        stats["rows_cleaned"] = int(len(df))
        
        stats_text = eda_utils.format_summary_for_llm(stats)
        
        # 3. Excel Report
        history_dir = "app/project_history/reports"
        os.makedirs(history_dir, exist_ok=True)
        report_filename = f"eda_report_{request.session_id}_{os.path.basename(request.filename).split('.')[0]}.xlsx"
        report_path = os.path.join(history_dir, report_filename)
        
        eda_utils.generate_excel_report(df, stats, report_path)
        stats["report_path"] = report_path # Log location
        # Initialize DataAgent
        agent = DataAgent(session_id=request.session_id)

        # Run analysis (DataAgent.analyze_data expects file_path, problem_definition, target_col)
        # We need to map request.filepath to file_path
        
        # Note: DataAgent.analyze_data returns a specific dict structure.
        # We might need to adapt the response or just return it as is if compatible.
        
        # Construct the full file path from the filename
        file_path = f"{DATA_DIR}/{request.filename}"

        result = agent.analyze_data(
            file_path=file_path, 
            problem_definition=request.problem_definition, # Use problem_definition from request
            target_col=request.target_col # Use target_col from request
        )
        
        if result.get("status") == "error":
             raise HTTPException(status_code=500, detail=result.get("message"))

        return EDAResponse(
            stats=stats,
            analysis=result.get("analysis", "No analysis generated")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
