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
    def __init__(self, name: str, role: str, model: str = LLM_MODEL_NAME, session_id: str = "default"):
        self.name = name
        self.role = role
        self.model = model
        self.session_id = session_id
        
        # Determine the root and setup paths based on session_id
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # New Structure: project_history/{session_id}/agents/{name}
        self.session_dir = os.path.join(self.base_dir, "project_history", self.session_id)
        self.agent_dir = os.path.join(self.session_dir, "agents", self.name)
        
        os.makedirs(self.agent_dir, exist_ok=True)
        
        self.memory_file = os.path.join(self.agent_dir, "memory.json")
        self.logs_file = os.path.join(self.agent_dir, "logs.json")
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

    def log_interaction(self, prompt: str, response: str):
        """
        Logs the interaction to both JSON and text files within the session folder.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Text Log
        log_file_txt = os.path.join(self.session_dir, "agent_interactions.log")
        entry_txt = f"""
[{timestamp}] AGENT: {self.name}
--------------------------------------------------
INPUT PROMPT:
{prompt}

OUTPUT RESPONSE:
{response}
--------------------------------------------------
"""
        try:
            with open(log_file_txt, 'a', encoding='utf-8') as f:
                f.write(entry_txt)
        except Exception as e:
            logger.error(f"Failed to write interaction log (txt): {e}")

        # 2. JSON Log
        log_file_json = os.path.join(self.session_dir, "agent_interactions.json")
        entry_json = {
            "timestamp": timestamp,
            "session_id": self.session_id,
            "agent": self.name,
            "input": prompt,
            "output": response
        }
        
        try:
            # Read existing
            data = []
            if os.path.exists(log_file_json):
                with open(log_file_json, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = []
            
            data.append(entry_json)
            
            with open(log_file_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to write interaction log (json): {e}")

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
