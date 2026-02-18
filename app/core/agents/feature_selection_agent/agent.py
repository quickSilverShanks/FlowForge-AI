from typing import Dict, Any, List
import pandas as pd
import os
import json
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.agents.base_agent import BaseAgent
from app.core.agents.feature_selection_agent import tools as fs_tools
from app.core.config import LLM_MODEL_NAME

class FeatureSelectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="feature_selection_agent", role="Feature Selector")
        self.llm = Ollama(base_url="http://ollama:11434", model=LLM_MODEL_NAME, temperature=0)
        
    def suggest_features(self, columns: List[str], problem_definition: str, target_col: str, summary_text: str) -> Dict[str, Any]:
        """
        Asks LLM to suggest which features to keep/drop.
        """
        template = """
        You are an expert Data Scientist.
        We have a dataset with the following columns: {columns}
        
        Problem Definition: {problem_definition}
        Target Variable: {target_col}
        Dataset Summary: {summary_text}
        
        Suggest which features are likely important and which can be dropped (e.g., IDs, high cardinality low info, leakage).
        
        Return a JSON object with:
        "metrics": {{ "reasoning": "...", "recommended_features": ["col1", "col2"] }}
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["columns", "problem_definition", "target_col", "summary_text"]
        )
        
        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            suggestion = chain.invoke({
                "columns": str(columns),
                "problem_definition": problem_definition,
                "target_col": target_col,
                "summary_text": summary_text
            })
            
            # Log Interaction
            formatted_prompt = template.format(
                columns=str(columns),
                problem_definition=problem_definition,
                target_col=target_col,
                summary_text=summary_text
            )
            self.log_interaction(formatted_prompt, str(suggestion))
            
            return suggestion
        except Exception as e:
            self.log_step("error_suggesting_features", {}, str(e))
            return {"recommended_features": columns}

    def run(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        file_path = context.get("file_path")
        target_col = context.get("target_col")
        problem_def = context.get("problem_definition", "Not specified")
        eda_summary = context.get("eda_summary", {}) # Passed from Data Agent if available
        
        # 1. Get current columns
        current_cols = self._execute_tool(fs_tools.get_columns, file_path=file_path)
        
        if not current_cols:
            return {"status": "error", "message": "Could not read columns."}
            
        # 2. Suggest features
        suggestion = self.suggest_features(current_cols, problem_def, target_col, str(eda_summary))
        recommended = suggestion.get("recommended_features", current_cols)
        
        self.log_step("feature_suggestion", {"current": current_cols}, suggestion)
        
        # 3. Apply selection (Auto-select recommended for now)
        output_path = file_path.replace(".csv", "_selected.csv")
        result_path = self._execute_tool(fs_tools.save_selected_features, file_path=file_path, selected_features=recommended, output_path=output_path)
        
        return {
            "status": "success",
            "original_columns": current_cols,
            "selected_columns": recommended,
            "selected_file_path": result_path
        }
