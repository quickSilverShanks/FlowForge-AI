import sys
import os
import streamlit as st
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

# Mock Streamlit session state for testing
class MockSessionState(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

# Initialize mock session
if not hasattr(st, "session_state"):
    st.session_state = MockSessionState()

from app.ui.session_manager import initialize_session, save_page_state, get_all_page_states

def verify_context_retrieval():
    print("1. Initializing Dummy Session...")
    session_id = initialize_session(session_name="Test Context Session")
    print(f"   Session ID: {session_id}")
    
    print("\n2. Saving Mock Page States...")
    # Mock EDA State
    eda_state = {
        "analysis": "Data has 3 clusters.",
        "columns": ["age", "salary", "score"]
    }
    save_page_state("EDA", eda_state)
    print("   Saved EDA state.")
    
    # Mock Feature Engineering State
    mp_state = {
        "plan": ["Impute Age", "Scale Salary"],
        "status": "Draft"
    }
    save_page_state("FeatureEngineering", mp_state)
    print("   Saved FeatureEngineering state.")
    
    print("\n3. Retrieving All Page States...")
    active_pages = get_all_page_states()
    
    print(f"   Retrieved States: {active_pages.keys()}")
    
    if "EDA" in active_pages and "FeatureEngineering" in active_pages:
        print("\nSUCCESS: All page states retrieved correctly.")
        print("EDA Content:", active_pages["EDA"]["analysis"])
        print("Feature Plan:", active_pages["FeatureEngineering"]["plan"])
    else:
        print("\nFAILURE: Missing page states.")

if __name__ == "__main__":
    verify_context_retrieval()
