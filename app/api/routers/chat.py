from fastapi import APIRouter
from pydantic import BaseModel
from app.core.utils.logger import SessionLogger
from app.core.agents.search_agent.agent import SearchAgent

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"

@router.post("/ask")
async def ask_question(request: ChatRequest):
    logger = SessionLogger(request.session_id)
    # SearchAgent expects context as a string or maybe we should let it search?
    # The original code passed session content as context.
    # SearchAgent.answer_question(question, context) matches this signature.
    
    context = logger.get_session_content()
    
    agent = SearchAgent(session_id=request.session_id)
    answer = agent.answer_question(request.question, str(context))
    
    return {"answer": answer, "context_length": len(context)}
