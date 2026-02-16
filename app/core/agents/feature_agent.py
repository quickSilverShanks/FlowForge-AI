from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Literal # Added literal import
import os

from app.core.config import LLM_MODEL_NAME

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

class TransformationStep(BaseModel):
    column: str = Field(description="The column to apply transformation to")
    operation: str = Field(description="The operation to perform: 'impute_mean', 'impute_median', 'one_hot', 'label_encode', 'standard_scale', 'minmax_scale', 'log_transform', 'drop'")
    reasoning: str = Field(description="Why this transformation is needed")

class FeaturePlan(BaseModel):
    steps: List[TransformationStep]

class FeatureEngineeringAgent:
    def __init__(self, model: str = LLM_MODEL_NAME):
        self.llm = Ollama(base_url=OLLAMA_BASE_URL, model=model, temperature=0) # Low temp for deterministic code/json
        self.parser = JsonOutputParser(pydantic_object=FeaturePlan)
        
    def propose_plan(self, summary_text: str, problem_definition: str) -> dict:
        template = """
        You are an expert Data Scientist. 
        Based on the following dataset summary and problem definition, propose a Feature Engineering Plan.
        
        Dataset Summary:
        {summary_text}
        
        Problem Definition: {problem_definition}
        
        Return a JSON object with a list of steps. 
        Supported operations: ['impute_mean', 'impute_median', 'one_hot', 'label_encode', 'standard_scale', 'minmax_scale', 'log_transform', 'drop'].
        
        {format_instructions}
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["summary_text", "problem_definition"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        chain = prompt | self.llm | self.parser
        
        try:
            return chain.invoke({
                "summary_text": summary_text,
                "problem_definition": problem_definition
            })
        except Exception as e:
            # Fallback or error handling for invalid JSON
            print(f"Error generating plan: {e}")
            return {"steps": []}
