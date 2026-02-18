from typing import Dict, Any, List
import json
from datetime import datetime
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.agents.base_agent import BaseAgent
from app.core.config import LLM_MODEL_NAME

class OrchestratorAgent(BaseAgent):
    def __init__(self, session_id: str = "default"):
        super().__init__(name="orchestrator", role="Project Manager & Planner", session_id=session_id)
        self.llm = Ollama(base_url="http://ollama:11434", model=LLM_MODEL_NAME, temperature=0)
        self.agents_registry = {
            "data_agent": "Handles data ingestion, problem definition, and initial EDA.",
            "feature_engineering_agent": "Handles missing value imputation, encoding, scaling, and feature transformation.",
            "feature_selection_agent": "Helps select the best features based on user input or automated methods.",
            "model_build_agent": "Suggests model types and defines hyperparameter search spaces.",
            "hyperparameter_agent": "Runs hyperparameter optimization studies using Optuna/MLflow.",
            "validation_agent": "Validates the best model on hold-out data (in-sample, out-of-time, out-of-sample).",
            "documentation_agent": "Generates detailed documentation of the entire process.",
            "governance_agent": "Analyzes model fairness, interpretability (SHAP), and drift.",
            "search_agent": "Searches project logs and history to answer questions (RAG)."
        }

        template = """
        You are the Orchestrator for an advanced Auto-ML system.
        Your goal is to break down the user's request into a sequence of steps, each handled by a specific specialist agent.
        
        Available Agents:
        {agents}
        
        User Request: {user_request}
        
        Current Project Context:
        {project_context}
        
        Active Page States (Content currently visible on UI tabs):
        {active_pages}
        
        Return a JSON object with a "steps" key, containing a list of steps.
        Each step should have:
        - "agent": The name of the agent to call (must be one of the available agents).
        - "instruction": A clear instruction for that agent.
        - "reasoning": Why this step is needed.
        
        Example:
        {{
            "steps": [
                {{"agent": "data_agent", "instruction": "Load the dataset and perform initial EDA.", "reasoning": "We need to understand the data first."}},
                {{"agent": "feature_engineering_agent", "instruction": "Impute missing values and encode categorical variables.", "reasoning": "Models require clean numeric data."}}
            ]
        }}
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["user_request", "project_context", "agents", "active_pages"]
        )
        
        chain = prompt | self.llm | JsonOutputParser()
        
        # Parse context to extract active_pages if available
        # project_context might be a string, so we need to handle this carefully.
        # Ideally, 'plan' should accept a dict context, but signature is string.
        # We'll rely on the caller passing it in project_context string or we modify plan signature.
        # For now, let's assume project_context is the string representation,
        # but the run method has access to the dict context.
        # Let's see how 'plan' is called in routers/orchestrator.py:
        # steps = agent.plan(request.user_request, request.project_context)
        # request.project_context is a string.
        
        # However, we need 'active_pages' which comes from the UI.
        # The router/orchestrator.py doesn't seem to pass active_pages in the PlanRequest yet?
        # Let's check orchestrator.py again.
        # PlanRequest has project_context: str.
        # But we updated process_orchestrator_request in UI to send a context dict.
        # It calls API /orchestrator/run usually?
        # process_orchestrator_request calls process_orchestrator_request (which calls API).
        # In `app/ui/components/orchestrator.py`:
        # requests.post(f"{API_BASE_URL}/orchestrator/run", json=payload)
        # So we use `run`, not `plan`.
        
        # The `run` method calls `plan`. We should update `plan` signature to accept `active_pages`.
        
        active_pages = {}
        # This is a bit hacky if we don't change signature.
        # Let's assume we pass it via a separate argument or we extract it if possible.
        # But wait, `run` calls `plan(user_request, project_context)`.
        # We can pass `active_pages` from `run` to `plan`.
        pass
        
    def plan(self, user_request: str, project_context: str = "", active_pages: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Generates a high-level plan of agent calls based on the user request.
        """
        template = """
        You are the Orchestrator for an advanced Auto-ML system.
        Your goal is to break down the user's request into a sequence of steps, each handled by a specific specialist agent.
        
        Available Agents:
        {agents}
        
        User Request: {user_request}
        
        Current Project Context:
        {project_context}
        
        Active Page States (Content currently visible on UI tabs):
        {active_pages}
        
        Return a JSON object with a "steps" key, containing a list of steps.
        Each step should have:
        - "agent": The name of the agent to call (must be one of the available agents).
        - "instruction": A clear instruction for that agent.
        - "reasoning": Why this step is needed.
        
        Example:
        {{
            "steps": [
                {{"agent": "data_agent", "instruction": "Load the dataset and perform initial EDA.", "reasoning": "We need to understand the data first."}},
                {{"agent": "feature_engineering_agent", "instruction": "Impute missing values and encode categorical variables.", "reasoning": "Models require clean numeric data."}}
            ]
        }}
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["user_request", "project_context", "agents", "active_pages"]
        )
        
        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            response = chain.invoke({
                "user_request": user_request,
                "project_context": project_context,
                "agents": json.dumps(self.agents_registry, indent=2),
                "active_pages": json.dumps(active_pages or {}, indent=2)
            })
            
            # Log Interaction
            formatted_prompt = template.format(
                user_request=user_request, 
                project_context=project_context, 
                agents=json.dumps(self.agents_registry, indent=2),
                active_pages=json.dumps(active_pages or {}, indent=2)
            )
            self.log_interaction(formatted_prompt, json.dumps(response, indent=2))
            
            self.log_step("plan_generation", {"request": user_request}, response)
            return response.get("steps", [])
        except Exception as e:
            self.log_step("plan_error", {"request": user_request}, str(e))
            return []

    def run(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes the planning and delegation process.
        """
        project_context = context.get("project_summary", "No prior context.") if context else "No prior context."
        active_pages = context.get("active_pages", {}) if context else {}
        
        # 1. Generate Plan
        plan = self.plan(user_request, project_context, active_pages)
        
        if not plan:
            return {"status": "error", "message": "Failed to generate a plan."}
        
        self.update_memory("last_plan", plan)
        
        results = []
        
        # 2. Execute Plan (Sequential for now)
        for step in plan:
            agent_name = step.get("agent")
            instruction = step.get("instruction")
            
            self.log_step("delegating_to_agent", {"agent": agent_name, "instruction": instruction}, None)
            
            # TODO: dynamic import and execution of agents
            # For now, we return the plan so the main loop can execute it, 
            # OR we implement the dispatch here. 
            # Given the request "orchestrator agent will be the one to be called", 
            # it should verify the execution.
            
            # Ideally, we would have:
            # agent_instance = load_agent(agent_name)
            # step_result = agent_instance.run(instruction, context)
            # results.append(step_result)
            
            results.append({"agent": agent_name, "instruction": instruction, "status": "pending_execution"})

        return {
            "status": "success", 
            "plan": plan, 
            "results": results,
            "message": "Plan generated. Execution pending implementation of sub-agents."
        }
