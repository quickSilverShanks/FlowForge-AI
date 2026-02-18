from typing import Dict, Any, List
import json
import os
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

from app.core.agents.base_agent import BaseAgent
from app.core.agents.documentation_agent import tools as doc_tools
from app.core.config import LLM_MODEL_NAME

class DocumentationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="documentation_agent", role="Technical Writer")
        self.llm = Ollama(base_url="http://ollama:11434", model=LLM_MODEL_NAME, temperature=0)
        
    def generate_report(self, logs: Dict[str, List[dict]]) -> str:
        # Simplify logs for LLM to avoid token overflow
        summary_logs = {}
        for agent, entries in logs.items():
            summary_logs[agent] = []
            for e in entries:
                # Keep only key info
                summary_logs[agent].append({
                    "step": e.get("step_type"),
                    "input": str(e.get("input"))[:200], # Trupoint
                    "output": str(e.get("output"))[:200]
                })

        template = """
        You are a Technical Writer documenting an ML project.
        Based on the following execution logs from different agents, generate a concise project report.
        
        Logs:
        {logs}
        
        Structure the report as:
        1. Executive Summary
        2. Data Analysis (Data Agent)
        3. Feature Engineering (Feature Agent)
        4. Modeling Strategy (Model Agent)
        5. Results (Validation & Governance)
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        report = chain.invoke({"logs": json.dumps(summary_logs)})
        
        # Log Interaction
        formatted_prompt = template.format(logs=json.dumps(summary_logs))
        self.log_interaction(formatted_prompt, str(report))
        
        return report

    def run(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        # Need to know where project history is. BaseAgent knows its own history dir, but we need the root project_history.
        # BaseAgent.history_dir is .../project_history/agents/{name}
        # So we go up 2 levels from self.history_dir
        
        project_history_dir = os.path.dirname(os.path.dirname(self.history_dir))
        
        logs = self._execute_tool(doc_tools.read_all_logs, project_history_dir=project_history_dir)
        report = self.generate_report(logs)
        
        # Save report
        report_path = os.path.join(project_history_dir, "final_report.md")
        with open(report_path, 'w') as f:
            f.write(report)
            
        return {
            "status": "success",
            "report_path": report_path
        }
