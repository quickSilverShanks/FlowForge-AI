import os
import json
from typing import List, Dict

def search_project_logs(query: str, project_history_dir: str) -> str:
    """
    Simple search through agent logs. In a real system, this might use a vector DB.
    """
    results = []
    agents_dir = os.path.join(project_history_dir, "agents")
    if not os.path.exists(agents_dir):
        return "No logs found"
        
    for agent_name in os.listdir(agents_dir):
        log_path = os.path.join(agents_dir, agent_name, "logs.json")
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r') as f:
                    logs = json.load(f)
                    # Naive text search
                    for entry in logs:
                        text = str(entry)
                        if any(term in text.lower() for term in query.lower().split()):
                             results.append(f"[{agent_name}] {text[:500]}...")
            except:
                continue
                
    return "\n".join(results[:10]) if results else "No matches found"
