import os
import json
from typing import Dict, List

def read_all_logs(project_history_dir: str) -> Dict[str, List[dict]]:
    """
    Reads logs from all agents.
    """
    agents_dir = os.path.join(project_history_dir, "agents")
    if not os.path.exists(agents_dir):
        return {}
        
    all_logs = {}
    for agent_name in os.listdir(agents_dir):
        log_path = os.path.join(agents_dir, agent_name, "logs.json")
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r') as f:
                    all_logs[agent_name] = json.load(f)
            except:
                continue
    return all_logs
