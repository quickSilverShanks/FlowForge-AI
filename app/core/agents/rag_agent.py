from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import os

from app.core.config import LLM_MODEL_NAME

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

class RAGAgent:
    def __init__(self, model: str = LLM_MODEL_NAME):
        self.llm = Ollama(base_url=OLLAMA_BASE_URL, model=model)
        
    def answer_question(self, question: str, history_context: list | dict):
        """
        Answers a question using the provided session history.
        history_context: The raw JSON list/dict from session_manager.
        """
        
        # Format the history into a readable string
        formatted_context = ""
        
        if isinstance(history_context, dict):
             # Handle timeline format
             timeline = history_context.get("timeline", [])
             config = history_context.get("config", {})
             
             formatted_context += f"Project Configuration: {config}\n\n"
             formatted_context += "Timeline of Events:\n"
             
             for event in timeline:
                 timestamp = event.get("timestamp", "")
                 etype = event.get("type", "")
                 content = event.get("content", "")
                 formatted_context += f"- [{timestamp}] {etype}: {content}\n"
                 
        else:
            # Fallback for simple string or list
            formatted_context = str(history_context)

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
            "context": formatted_context
        })
