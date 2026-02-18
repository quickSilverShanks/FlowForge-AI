from typing import Dict, Any, List
import json
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

from app.core.agents.base_agent import BaseAgent
from app.core.agents.governance_agent import tools as gov_tools
from app.core.config import LLM_MODEL_NAME

class GovernanceAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="governance_agent", role="AI Ethicist & Auditor")
        self.llm = Ollama(base_url="http://ollama:11434", model=LLM_MODEL_NAME, temperature=0)
        
    def interpret_model(self, explanation: list) -> str:
        template = """
        You are an Explainable AI expert.
        Analyze the following feature importance (SHAP values):
        {explanation}
        
        Explain which features are driving the model's predictions.
        Highlight any potential biases or surprising factors.
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        return chain.invoke({"explanation": str(explanation)})

    def run(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        file_path = context.get("file_path")
        target_col = context.get("target_col")
        experiment_name = context.get("experiment_name", "flowforge_experiment")
        
        if not file_path or not target_col:
            return {"status": "error", "message": "Missing context"}
            
        # 1. Generate SHAP
        explanation = self._execute_tool(
            gov_tools.generate_shap_explanation,
            file_path=file_path,
            target_col=target_col,
            experiment_name=experiment_name
        )
        
        # 2. Interpret
        interpretation = self.interpret_model(explanation)
        
        return {
            "status": "success",
            "feature_importance": explanation,
            "interpretation": interpretation
        }
