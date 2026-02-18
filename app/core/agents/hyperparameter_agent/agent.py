from typing import Dict, Any, List
import pandas as pd
import os
import json
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

from app.core.agents.base_agent import BaseAgent
from app.core.agents.hyperparameter_agent import tools as hp_tools
from app.core.config import LLM_MODEL_NAME

class HyperparameterAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="hyperparameter_agent", role="ML Engineer")
        self.llm = Ollama(base_url="http://ollama:11434", model=LLM_MODEL_NAME, temperature=0)
        
    def run(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        file_path = context.get("file_path")
        target_col = context.get("target_col")
        problem_type = context.get("problem_definition", "classification") # TODO: parse properly
        experiment_name = context.get("experiment_name", "flowforge_experiment")
        
        model_plan = context.get("model_plan", {})
        if not model_plan or "configs" not in model_plan:
            return {"status": "error", "message": "No model plan provided."}
            
        configs = model_plan["configs"]
        metric = model_plan.get("metric", "accuracy")
        
        self.log_step("starting_optimization", {"configs": configs}, "Starting Optuna studies...")
        
        status = self._execute_tool(
            hp_tools.run_optimization, 
            file_path=file_path, 
            target_col=target_col, 
            problem_type=problem_type, 
            configs=configs, 
            metric=metric, 
            experiment_name=experiment_name
        )
        
        return {
            "status": "success",
            "message": status,
            "experiment_name": experiment_name,
            "optimized_metric": metric
        }
