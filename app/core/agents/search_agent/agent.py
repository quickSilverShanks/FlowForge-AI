from typing import Dict, Any, List
import os
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

from app.core.agents.base_agent import BaseAgent
from app.core.agents.search_agent import tools as search_tools
from app.core.config import LLM_MODEL_NAME

class SearchAgent(BaseAgent):
    def __init__(self, session_id: str = "default"):
        super().__init__(name="search_agent", role="Knowledge Assistant", session_id=session_id)
        self.llm = Ollama(base_url="http://ollama:11434", model=LLM_MODEL_NAME, temperature=0)
        
    def answer_question(self, question: str, context: str) -> str:
        template = """
        You are an AI assistant helping a user understand their ML project history.
        Based on the following logs and context, answer the user's question.
        
        Logs/Context:
        {context}
        
        Question: {question}
        
        Answer based on facts in the logs. If you don't know, say so.
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        answer = chain.invoke({
            "question": question,
            "context": context
        })
        
        # Log Interaction
        formatted_prompt = template.format(question=question, context=context)
        self.log_interaction(formatted_prompt, str(answer))
        
        return answer

    def run(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        # Similar logic to Documentation Agent to find project root
        project_history_dir = os.path.dirname(os.path.dirname(self.history_dir))
        
        # 1. Search logs
        search_results = self._execute_tool(search_tools.search_project_logs, query=input_text, project_history_dir=project_history_dir)
        
        # 2. Answer question
        answer = self.answer_question(input_text, search_results)
        
        return {
            "status": "success",
            "search_results": search_results,
            "answer": answer
        }
