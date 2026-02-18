import json
import os
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from app.core.config import LLM_MODEL_NAME

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, name: str, role: str, model: str = LLM_MODEL_NAME):
        self.name = name
        self.role = role
        self.model = model
        
        # Determine the root of the project to locate project_history correctly
        # Assuming this file is in app/core/agents/base_agent.py
        # root is ../../../
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.history_dir = os.path.join(self.base_dir, f"project_history/agents/{self.name}")
        
        os.makedirs(self.history_dir, exist_ok=True)
        self.memory_file = os.path.join(self.history_dir, "memory.json")
        self.logs_file = os.path.join(self.history_dir, "logs.json")
        self.memory = self._load_memory()
        
    def _load_memory(self) -> Dict[str, Any]:
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def update_memory(self, key: str, value: Any):
        self.memory[key] = value
        self._save_memory()

    def get_memory(self, key: str, default: Any = None) -> Any:
        return self.memory.get(key, default)

    def log_step(self, step_type: str, input_data: Any, output_data: Any):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step_type": step_type,
            "input": input_data,
            "output": output_data
        }
        
        logs = []
        if os.path.exists(self.logs_file):
            with open(self.logs_file, 'r') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        
        logs.append(log_entry)
        with open(self.logs_file, 'w') as f:
            json.dump(logs, f, indent=4)

    def run(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point for the agent.
        Should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement run()")

    def _execute_tool(self, tool_func: Callable, **kwargs):
        """
        Helper to execute a tool and log it.
        """
        try:
            logger.info(f"[{self.name}] Executing tool: {tool_func.__name__}")
            result = tool_func(**kwargs)
            self.log_step(f"tool_execution: {tool_func.__name__}", kwargs, str(result)[:1000] + "..." if len(str(result)) > 1000 else result)
            return result
        except Exception as e:
            logger.error(f"[{self.name}] Error executing tool {tool_func.__name__}: {e}")
            self.log_step(f"tool_error: {tool_func.__name__}", kwargs, str(e))
            raise e
