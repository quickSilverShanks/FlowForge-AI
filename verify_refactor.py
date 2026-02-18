import sys
import os
import inspect

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("1. Verifying BaseAgent...")
    from app.core.agents.base_agent import BaseAgent
    sig = inspect.signature(BaseAgent.__init__)
    if "session_id" in sig.parameters:
        print("   MATCH: BaseAgent accepts session_id.")
    else:
        print("   ERROR: BaseAgent does NOT accept session_id.")

    print("\n2. Verifying Routers (Import Check)...")
    from app.api.routers import eda, features, training, chat, orchestrator
    print("   MATCH: All routers imported successfully.")

    print("\n3. Verifying OrchestratorAgent...")
    from app.core.agents.orchestrator.agent import OrchestratorAgent
    try:
        agent = OrchestratorAgent(session_id="test_verification")
        print(f"   MATCH: OrchestratorAgent instantiated with session_id. Log dir: {agent.session_dir}")
    except TypeError as e:
         print(f"   ERROR: OrchestratorAgent failed instantiation: {e}")

except ImportError as e:
    print(f"CRITICAL ERROR: Import failed - {e}")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
