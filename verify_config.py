
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.core.config import LLM_MODEL_NAME
from app.core.agents.eda_agent import EDAAgent

print(f"Loaded LLM_MODEL_NAME: {LLM_MODEL_NAME}")

if LLM_MODEL_NAME == "llama3":
    print("SUCCESS: Default/Configured model name is correct.")
else:
    print(f"WARNING: Expected 'llama3', got '{LLM_MODEL_NAME}'")

try:
    agent = EDAAgent()
    print(f"Agent initialized with model: {agent.llm.model}")
    if agent.llm.model == LLM_MODEL_NAME:
        print("SUCCESS: Agent is using the configured model.")
    else:
        print(f"FAILURE: Agent is using '{agent.llm.model}' instead of '{LLM_MODEL_NAME}'")

except Exception as e:
    print(f"Error initializing agent: {e}")
