from typing import Dict, Any, List
import pandas as pd
import os
import json
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.core.agents.base_agent import BaseAgent
from app.core.agents.feature_engineering_agent import tools as fe_tools
from app.core.config import LLM_MODEL_NAME

class TransformationStep(BaseModel):
    column: str = Field(description="The column to apply transformation to")
    operation: str = Field(description="The operation to perform: 'impute_mean', 'impute_median', 'one_hot', 'label_encode', 'standard_scale', 'minmax_scale', 'log_transform', 'drop'")
    reasoning: str = Field(description="Why this transformation is needed")

class FeaturePlan(BaseModel):
    steps: List[TransformationStep]

class FeatureEngineeringAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="feature_engineering_agent", role="Feature Engineer")
        self.llm = Ollama(base_url="http://ollama:11434", model=LLM_MODEL_NAME, temperature=0)
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
            self.log_step("error_generating_plan", {}, str(e))
            return {"steps": []}

    def run(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        file_path = context.get("file_path")
        problem_def = context.get("problem_definition", "Not specified")
        eda_summary = context.get("eda_summary", {})
        
        # Format summary for LLM
        summary_text = str(eda_summary) # Ideally reuse format_summary_for_llm logic or pass it ready-made
        
        # 1. Propose Plan
        plan = self.propose_plan(summary_text, problem_def)
        
        if not plan or not plan.get("steps"):
            return {"status": "warning", "message": "No feature engineering steps proposed."}

        self.log_step("proposed_plan", {"summary": summary_text}, plan)
        
        # 2. Execute Plan (In a real interactive app, we might ask for user confirmation here)
        # For now, we auto-execute based on the plan
        output_path = file_path.replace(".csv", "_processed.csv")
        result_path = self._execute_tool(fe_tools.apply_feature_plan, file_path=file_path, plan=plan, output_path=output_path)
        
        return {
            "status": "success",
            "plan": plan,
            "processed_file_path": result_path
        }
