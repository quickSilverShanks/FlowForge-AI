from typing import Dict, Any, List
import pandas as pd
import os
import json
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

from app.core.agents.base_agent import BaseAgent
from app.core.agents.data_agent import tools as data_tools
from app.core.config import LLM_MODEL_NAME

class DataAgent(BaseAgent):
    def __init__(self, session_id: str = "default"):
        super().__init__(name="data_agent", role="Data Scientist & Analyst", session_id=session_id)
        self.llm = Ollama(base_url="http://ollama:11434", model=LLM_MODEL_NAME)
        
    def analyze_data(self, file_path: str, problem_definition: str = None, target_col: str = None) -> Dict[str, Any]:
        """
        Main logic for Data Agent.
        """
        # 1. Generate Summary
        summary = self._execute_tool(data_tools.generate_eda, file_path=file_path)
        
        if "error" in summary:
            return {"status": "error", "message": summary["error"]}
        
        # 2. Ask LLM for Vibe Check
        summary_text = self._format_summary_for_llm(summary)
        
        template = """
        You are an expert Data Scientist. 
        I have a dataset with the following characteristics:
        
        {summary_text}
        
        Problem Definition: {problem_definition}
        Target Variable (if known): {target_col}
        
        Please perform a "Vibe Check" and provide a detailed EDA summary.
        Include:
        1. Key Data Quality Issues (Missing values, duplicates, etc.)
        2. Potential Target Leakage and specific relationship of features with the Target Variable '{target_col}'.
        3. Class Imbalance (if applicable to target).
        4. Feature Engineering Opportunities explicitly for improving prediction of '{target_col}'.
        5. Risks for Modeling.
        
        Format your response in Markdown.
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        analysis = chain.invoke({
            "summary_text": summary_text,
            "problem_definition": problem_definition or "Not specified",
            "target_col": target_col or "Not specified"
        })
        
        # Log Interaction
        formatted_prompt = template.format(
            summary_text=summary_text,
            problem_definition=problem_definition or "Not specified",
            target_col=target_col or "Not specified"
        )
        self.log_interaction(formatted_prompt, str(analysis))
        
        # 3. Generate Report
        report_path = self._execute_tool(data_tools.generate_report, file_path=file_path, summary=summary, output_dir=os.path.dirname(file_path))
        
        return {
            "status": "success",
            "eda_summary": summary,
            "analysis": analysis,
            "report_path": report_path
        }

    def _format_summary_for_llm(self, summary: dict) -> str:
        # Reusing logic from old eda_utils but within agent context or importing from utils if available
        # Since I imported eda_utils inside tools, I can't use it directly unless I expose it or duplicate.
        # Minimal implementation here for self-containment
        text = f"Dataset Shape: {summary.get('rows')} rows, {summary.get('columns')} columns.\n"
        text += f"Duplicate Rows: {summary.get('duplicates')}\n"
        text += f"Column Types: {summary.get('column_types')}\n"
        text += f"Missing Values: {summary.get('missing_values')}\n"
        return text

    def run(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        # Parse input to get file path and details
        # In a real agent, this would be an LLM call to extract params.
        # For prototype, we expect context to have the file path or extract from input if simple.
        
        file_path = context.get("file_path")
        problem_def = context.get("problem_definition")
        target_col = context.get("target_col")
        
        if not file_path:
             return {"status": "error", "message": "File path not provided in context."}
             
        return self.analyze_data(file_path, problem_def, target_col)
