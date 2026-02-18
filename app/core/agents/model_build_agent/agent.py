from typing import Dict, Any, List, Union
import json
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.core.agents.base_agent import BaseAgent
from app.core.config import LLM_MODEL_NAME

class HyperparameterRange(BaseModel):
    name: str
    type: str = Field(description="'int', 'float', 'categorical'")
    low: float = None
    high: float = None
    choices: List[Union[str, int, float]] = None

class ModelConfig(BaseModel):
    model_type: str = Field(description="'xgboost', 'lightgbm', 'random_forest', 'logistic_regression'")
    params: List[HyperparameterRange]

class ModelingPlan(BaseModel):
    configs: List[ModelConfig]
    metric: str = Field(description="Optimization metric e.g. 'accuracy', 'f1', 'rmse'")

class ModelBuildAgent(BaseAgent):
    def __init__(self, session_id: str = "default"):
        super().__init__(name="model_build_agent", role="Model Architect", session_id=session_id)
        self.llm = Ollama(base_url="http://ollama:11434", model=LLM_MODEL_NAME, temperature=0)
        self.parser = JsonOutputParser(pydantic_object=ModelingPlan)
        
    def propose_models(self, problem_definition: str, summary_text: str) -> dict:
        template = """
        You are an expert AutoML engineer.
        Based on the data and problem, suggest the best models and hyperparameter search spaces for Optuna.
        
        Problem: {problem_definition}
        Data Summary: {summary_text}
        
        Suggest 2-3 diverse models (e.g., XGBoost, Random Forest).
        For each, define key hyperparameters to tune.
        
        {format_instructions}
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["problem_definition", "summary_text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        chain = prompt | self.llm | self.parser
        
        try:
            plan = chain.invoke({
                "problem_definition": problem_definition,
                "summary_text": summary_text
            })
            
            # Log Interaction
            formatted_prompt = template.format(
                problem_definition=problem_definition,
                summary_text=summary_text,
                format_instructions=self.parser.get_format_instructions()
            )
            self.log_interaction(formatted_prompt, str(plan))
            
            return plan
        except Exception as e:
            self.log_step("error_generating_model_plan", {}, str(e))
            return {"configs": [], "metric": "accuracy"}

    def run(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        problem_def = context.get("problem_definition", "Not specified")
        eda_summary = context.get("eda_summary", {})
        
        plan = self.propose_models(problem_def, str(eda_summary))
        
        self.log_step("model_plan", {}, plan)
        
        return {
            "status": "success",
            "model_plan": plan
        }
