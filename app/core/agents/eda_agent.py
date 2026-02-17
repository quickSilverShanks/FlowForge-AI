from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import os

from app.core.config import LLM_MODEL_NAME

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

class EDAAgent:
    def __init__(self, model: str = LLM_MODEL_NAME):
        self.llm = Ollama(base_url=OLLAMA_BASE_URL, model=model)
        
    def analyze(self, summary_text: str, problem_definition: str = None, target_col: str = None):
        """
        Asks the LLM to analyze the dataset summary.
        """
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
        
        return chain.invoke({
            "summary_text": summary_text,
            "problem_definition": problem_definition or "Not specified",
            "target_col": target_col or "Not specified (Unsupervised or Unknown)"
        })
