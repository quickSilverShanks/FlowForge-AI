from fastapi import APIRouter
from pydantic import BaseModel
from app.core.utils.logger import SessionLogger
from app.core.agents.rag_agent import RAGAgent

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"

@router.post("/ask")
async def ask_question(request: ChatRequest):
    logger = SessionLogger(request.session_id)
    context = logger.get_session_content()
    
    agent = RAGAgent()
    answer = agent.answer_question(request.question, context)
    
    return {"answer": answer, "context_length": len(context)}
