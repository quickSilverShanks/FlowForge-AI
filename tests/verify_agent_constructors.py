import sys
import os
import inspect

# Add project root to path
sys.path.append(os.getcwd())

def verify_agent(agent_class, name):
    print(f"\nVerifying {name}...")
    sig = inspect.signature(agent_class.__init__)
    if "session_id" in sig.parameters:
        print(f"   MATCH: {name} accepts session_id.")
        try:
            agent = agent_class(session_id="test_verification")
            print(f"   SUCCESS: Instantiated {name} with session_id. Log dir: {agent.session_dir}")
        except Exception as e:
            # Some agents might fail init if LLM/Ollama is not reachable, which is fine for this signature check so long as it's not TypeError
            print(f"   WARNING: Instantiation failed (might be expected without LLM): {e}") 
    else:
        print(f"   ERROR: {name} does NOT accept session_id.")

try:
    from app.core.agents.base_agent import BaseAgent
    from app.core.agents.data_agent.agent import DataAgent
    from app.core.agents.feature_engineering_agent.agent import FeatureEngineeringAgent
    from app.core.agents.model_build_agent.agent import ModelBuildAgent
    from app.core.agents.orchestrator.agent import OrchestratorAgent
    from app.core.agents.search_agent.agent import SearchAgent

    verify_agent(BaseAgent, "BaseAgent")
    verify_agent(DataAgent, "DataAgent")
    verify_agent(FeatureEngineeringAgent, "FeatureEngineeringAgent")
    verify_agent(ModelBuildAgent, "ModelBuildAgent")
    verify_agent(OrchestratorAgent, "OrchestratorAgent")
    verify_agent(SearchAgent, "SearchAgent")

except ImportError as e:
    print(f"CRITICAL ERROR: Import failed - {e}")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
