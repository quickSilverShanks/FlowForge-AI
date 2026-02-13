from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Union, Any
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

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

class ModelingAgent:
    def __init__(self, model: str = "llama3"):
        self.llm = Ollama(base_url=OLLAMA_BASE_URL, model=model, temperature=0)
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
            return chain.invoke({
                "problem_definition": problem_definition,
                "summary_text": summary_text
            })
        except Exception as e:
            print(f"Error generating model plan: {e}")
            return {"configs": [], "metric": "accuracy"}
