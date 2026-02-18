from typing import Dict, Any, List
import json
from langchain_community.llms import Ollama

from app.core.agents.base_agent import BaseAgent
from app.core.agents.validation_agent import tools as val_tools
from app.core.config import LLM_MODEL_NAME

class ValidationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="validation_agent", role="QA Engineer")
        self.llm = Ollama(base_url="http://ollama:11434", model=LLM_MODEL_NAME, temperature=0)
        
    def run(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        file_path = context.get("file_path") # Should be validation/test set
        target_col = context.get("target_col")
        experiment_name = context.get("experiment_name", "flowforge_experiment")
        metric = context.get("optimized_metric", "accuracy")
        
        if not file_path or not target_col:
            return {"status": "error", "message": "Missing file_path or target_col"}
            
        evaluation = self._execute_tool(
            val_tools.evaluate_best_model,
            file_path=file_path,
            target_col=target_col,
            experiment_name=experiment_name,
            metric=metric
        )
        
        return {
            "status": "success",
            "evaluation": evaluation
        }
