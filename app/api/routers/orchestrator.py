from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List

from app.core.agents.orchestrator.agent import OrchestratorAgent

router = APIRouter(prefix="/orchestrator", tags=["Orchestrator"])

class PlanRequest(BaseModel):
    user_request: str
    project_context: str = ""

class RunRequest(BaseModel):
    user_request: str
    context: Dict[str, Any] = None

class PlanResponse(BaseModel):
    steps: List[Dict[str, Any]]

class RunResponse(BaseModel):
    status: str
    plan: List[Dict[str, Any]]
    results: List[Dict[str, Any]]
    message: str

@router.post("/plan", response_model=PlanResponse)
async def generate_plan(request: PlanRequest):
    try:
        # PlanRequest doesn't have session_id, use default or infer from context string if possible
        agent = OrchestratorAgent(session_id="default")
        steps = agent.plan(request.user_request, request.project_context)
        return {"steps": steps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run", response_model=RunResponse)
async def run_orchestrator(request: RunRequest):
    try:
        session_id = request.context.get("session_id", "default") if request.context else "default"
        agent = OrchestratorAgent(session_id=session_id)
        result = agent.run(request.user_request, request.context or {})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
