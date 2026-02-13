import os
from datetime import datetime

DOCS_DIR = "/app/docs"

class SessionLogger:
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.session_dir = f"{DOCS_DIR}/{session_id}"
        os.makedirs(self.session_dir, exist_ok=True)

    def log_step(self, step_name: str, content: str, user_feedback: str = None):
        """
        Logs a step to a markdown file.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"{self.session_dir}/{step_name}.md"
        
        with open(filename, "w") as f:
            f.write(f"# {step_name.replace('_', ' ').title()}\n\n")
            f.write(f"**Timestamp**: {timestamp}\n\n")
            f.write("## System Output\n")
            f.write(f"{content}\n\n")
            
            if user_feedback:
                f.write("## User Feedback\n")
                f.write(f"{user_feedback}\n\n")
                
    def get_session_content(self) -> str:
        """
        Aggregates all steps for RAG.
        """
        content = ""
        if not os.path.exists(self.session_dir):
            return "No session data found."
            
        for file in sorted(os.listdir(self.session_dir)):
            if file.endswith(".md"):
                with open(f"{self.session_dir}/{file}", "r") as f:
                    content += f.read() + "\n\n---\n\n"
        return content
