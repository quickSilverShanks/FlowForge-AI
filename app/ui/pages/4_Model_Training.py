import streamlit as st
import requests
import os
from app.ui.session_manager import log_event, save_page_state, get_page_state, get_current_session_id

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")
PREFECT_URL = os.getenv("PREFECT_UI_URL", "http://localhost:4200")
MLFLOW_URL = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

st.set_page_config(page_title="Model Training", layout="wide")

st.set_page_config(page_title="Model Training", layout="wide")

from app.ui.components.orchestrator import render_orchestrator_sidebar
render_orchestrator_sidebar()

# --- Sidebar Session Info ---
session_id = get_current_session_id()
session_name = st.session_state.get("session_name", f"Session {session_id}")
st.sidebar.info(f"**Active Session:**\n{session_name}")
# -----------------------------

st.title("🏃 Model Training & Optimization")

filename = st.text_input("Filename", value=st.session_state.get("current_filename", "transformed_train.csv"))
target = st.text_input("Target Column", value=st.session_state.get("target", "Survived"))
problem_type = st.selectbox("Problem Type", ["Classification", "Regression"], index=0 if st.session_state.get("problem_type") == "Classification" else 1)

# Load State
page_state = get_page_state("ModelTraining")
if "training_plan" not in st.session_state:
    st.session_state.training_plan = page_state.get("plan", {})

if st.button("Propose Training Plan"):
    with st.spinner("Agent is designing model search space..."):
        try:
            payload = {"filename": filename, "problem_definition": f"{problem_type} for {target}"}
            response = requests.post(f"{API_URL}/training/propose", json=payload)
            if response.status_code == 200:
                plan = response.json()
                st.session_state.training_plan = plan
                
                # Save State
                save_page_state("ModelTraining", {"plan": plan})
                
                st.success("Plan Generated!")
                st.rerun()
            else:
                st.error(f"Failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

# Interactive Editor
if st.session_state.training_plan:
    st.subheader("Training Configuration")
    metric = st.selectbox("Optimization Metric", ["accuracy", "f1", "rmse", "r2"], index=0 if problem_type=="Classification" else 2)
    
    configs = st.session_state.training_plan.get('configs', [])
    
    # Allow user to edit configs via JSON (simplest for complex nested structures) or simple UI
    # Let's do a JSON editor for flexibility
    st.write("Edit Search Space (JSON)")
    configs_json = st.text_area("Model Configurations", value=json.dumps(configs, indent=2), height=300)
    
    if st.button("Start Training 🚀"):
        try:
            final_configs = json.loads(configs_json)
            payload = {
                "filename": filename,
                "target": target,
                "problem_type": problem_type,
                "configs": final_configs,
                "metric": metric,
                "session_id": "default"
            }
            
            response = requests.post(f"{API_URL}/training/train", json=payload)
            if response.status_code == 200:
                st.success("Training Started! 🏃‍♂️")
                data = response.json()
                st.write(f"Track Progress here: [Prefect Dashboard]({PREFECT_URL})")
                st.write(f"View Experiments here: [MLflow Dashboard]({MLFLOW_URL})")
            else:
                st.error(f"Failed to start training: {response.text}")
                
        except json.JSONDecodeError:
            st.error("Invalid JSON configuration")
        except Exception as e:
            st.error(f"Error: {e}")
