import streamlit as st
import requests
import os
import json
from app.ui.session_manager import log_event, save_page_state, get_page_state, get_current_session_id

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="Feature Engineering", layout="wide")

st.set_page_config(page_title="Feature Engineering", layout="wide")

from app.ui.components.orchestrator import render_orchestrator_sidebar
render_orchestrator_sidebar()

# --- Sidebar Session Info ---
session_id = get_current_session_id()
session_name = st.session_state.get("session_name", f"Session {session_id}")
st.sidebar.info(f"**Active Session:**\n{session_name}")
# -----------------------------

st.title("🛠️ Feature Engineering")

filename = st.text_input("Filename", value=st.session_state.get("current_filename", "train.csv"))
problem_definition = st.text_area("Problem Definition", value=st.session_state.get("problem_definition", "Predict survival on Titanic"), height=70)

# Load State
page_state = get_page_state("FeatureEngineering")
if "feature_plan" not in st.session_state:
    st.session_state.feature_plan = page_state.get("plan", [])

if st.button("Generate Feature Plan"):
    with st.spinner("Agent is designing features..."):
        try:
            payload = {"filename": filename, "problem_definition": problem_definition}
            response = requests.post(f"{API_URL}/features/propose", json=payload)
            if response.status_code == 200:
                plan = response.json()['steps']
                st.session_state.feature_plan = plan
                
                # Save State
                save_page_state("FeatureEngineering", {"plan": plan})
                
                st.success("Plan Generated!")
                st.rerun()
            else:
                st.error(f"Failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

# Interactive Plan Editor
if st.session_state.feature_plan:
    st.subheader("Proposed Plan")
    st.info("Review and modify the steps below.")
    
    updated_plan = []
    for i, step in enumerate(st.session_state.feature_plan):
        with st.expander(f"Step {i+1}: {step['operation']} on {step['column']}", expanded=True):
            col1, col2 = st.columns(2)
            new_op = col1.selectbox("Operation", 
                                  ['impute_mean', 'impute_median', 'one_hot', 'label_encode', 'standard_scale', 'minmax_scale', 'log_transform', 'drop'],
                                  index=['impute_mean', 'impute_median', 'one_hot', 'label_encode', 'standard_scale', 'minmax_scale', 'log_transform', 'drop'].index(step['operation']) if step['operation'] in ['impute_mean', 'impute_median', 'one_hot', 'label_encode', 'standard_scale', 'minmax_scale', 'log_transform', 'drop'] else 0,
                                  key=f"op_{i}")
            new_col = col2.text_input("Column", value=step['column'], key=f"col_{i}")
            reason = st.text_area("Reasoning", value=step['reasoning'], key=f"reason_{i}")
            
            if not st.checkbox("Remove Step", key=f"del_{i}"):
                updated_plan.append({"column": new_col, "operation": new_op, "reasoning": reason})

    if st.button("Apply Transformations"):
        with st.spinner("Applying changes..."):
            try:
                payload = {
                    "filename": filename,
                    "steps": updated_plan,
                    "session_id": "default" # TODO: Dynamic ID
                }
                response = requests.post(f"{API_URL}/features/apply", json=payload)
                if response.status_code == 200:
                    res = response.json()
                    st.success(f"Success! New file: {res['new_filename']}")
                    st.write(f"New Columns: {res['columns']}")
                    # Update filename for next steps
                    st.session_state.current_filename = res['new_filename']
                else:
                    st.error(f"Failed: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
