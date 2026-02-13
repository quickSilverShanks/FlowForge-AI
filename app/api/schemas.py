from pydantic import BaseModel
from typing import List, Optional, Any

class ProblemDefinition(BaseModel):
    target_column: str
    problem_type: str  # classification, regression
    kpi: Optional[str] = None
    description: Optional[str] = None

class DataUploadResponse(BaseModel):
    filename: str
    filepath: str
    columns: List[str]
    message: str
