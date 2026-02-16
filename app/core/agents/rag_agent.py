from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import os

from app.core.config import LLM_MODEL_NAME

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

class RAGAgent:
    def __init__(self, model: str = LLM_MODEL_NAME):
        self.llm = Ollama(base_url=OLLAMA_BASE_URL, model=model)
        
    def answer_question(self, question: str, context: str):
        template = """
        You are the AI Assistant for this ML Project.
        You have access to the session history/documentation below.
        
        Session History:
        {context}
        
        User Question: {question}
        
        Answer the question based on the history. If you don't know, say so.
        Provide citations to the specific step if possible.
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        return chain.invoke({
            "question": question,
            "context": context
        })
