from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

class EDAAgent:
    def __init__(self, model: str = "llama3"):
        self.llm = Ollama(base_url=OLLAMA_BASE_URL, model=model)
        
    def analyze(self, summary_text: str, problem_definition: str = None):
        """
        Asks the LLM to analyze the dataset summary.
        """
        template = """
        You are an expert Data Scientist. 
        I have a dataset with the following characteristics:
        
        {summary_text}
        
        Problem Definition: {problem_definition}
        
        Please perform a "Vibe Check" and provide a detailed EDA summary.
        Include:
        1. Key Data Quality Issues (Missing values, duplicates, etc.)
        2. Potential Target Leakage or Class Imbalance (if target is known).
        3. Feature Engineering Opportunities.
        4. Risks for Modeling.
        
        Format your response in Markdown.
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        return chain.invoke({
            "summary_text": summary_text,
            "problem_definition": problem_definition or "Not specified"
        })
