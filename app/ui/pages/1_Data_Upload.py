import streamlit as st
import requests
import pandas as pd
import os
from app.ui.session_manager import log_event, initialize_session, save_page_state, get_page_state, get_current_session_id

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="Data Upload", layout="wide")

from app.ui.components.orchestrator import render_orchestrator_sidebar
render_orchestrator_sidebar()

# --- Sidebar Session Info ---
session_id = get_current_session_id()
session_name_display = st.session_state.get("session_name", f"Session {session_id}")
st.sidebar.info(f"**Active Session:**\n{session_name_display}")
# -----------------------------


st.title("📂 Data Upload & Problem Definition")

# Load Page State
page_state = get_page_state("DataUpload")
saved_filename = page_state.get("filename")
saved_columns = page_state.get("columns", [])
saved_shape = page_state.get("shape", (0, 0))

with st.expander("ℹ️ Instructions", expanded=True):
    st.write("""
    1. Upload your training dataset (CSV or Parquet).
    2. Review the first few rows.
    3. Define your target variable and problem type.
    """)

# Session Naming
session_name = st.text_input("Session Name (Optional)", value=st.session_state.get("session_name", ""), placeholder="e.g., Credit Fraud Detection")
if session_name and session_name != st.session_state.get("session_name"):
    initialize_session(session_name)

# File Uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "parquet"])

df_preview = None
columns = []

# Logic: New Upload OR Existing State
if uploaded_file is not None:
    # --- New File Upload ---
    with st.spinner("Uploading..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post(f"{API_URL}/data/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                filepath = data['filepath']
                
                # Read for Preview & Stats
                uploaded_file.seek(0)
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file) # Read full to get shape? Might be slow for huge files. 
                    # Optimization: Just read header for cols, and shape if separate metadata provided?
                    # For this scale, reading it is fine or user 'head' logic.
                    # Start with full read to get shape as requested.
                else:
                    df = pd.read_parquet(uploaded_file)
                
                shape = df.shape
                columns = df.columns.tolist()
                df_preview = df.head(5)
                
                # DISPLAY SUCCESS WITH STATS
                st.success(f"File '{data['filename']}' uploaded successfully! (Rows: {shape[0]}, Columns: {shape[1]})")
                
                # Save State
                save_page_state("DataUpload", {
                    "filename": data['filename'],
                    "filepath": filepath,
                    "columns": columns,
                    "shape": shape
                })
                # Update Global Session
                st.session_state["filename"] = data['filename']
                
                saved_filename = data['filename'] # Update local var for SelectBox below
                
            else:
                st.error(f"Upload failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

elif saved_filename:
    # --- Restored State ---
    st.info(f"✅ Using active file: **{saved_filename}** ({saved_shape[0]} Rows, {saved_shape[1]} Columns)")
    columns = saved_columns
    # We don't preview data here to avoid re-reading from disk (unless we fetch head(5) from backend again)
    # Could imply "Preview not available (re-upload to view)" or fetch from API.
    # For now, just show persistence.

# PROBLEM DEFINITION SECTION
if columns: # Only show if we have active data
    st.divider()
    st.subheader("Problem Definition")
    
    col1, col2 = st.columns(2)
    with col1:
        # Restore target from session state if available
        current_target = st.session_state.get("target")
        target_index = columns.index(current_target) if current_target in columns else 0
        target = st.selectbox("Select Target Column", columns, index=target_index)
        
    with col2:
        current_prob = st.session_state.get("problem_type")
        prob_index = ["Classification", "Regression"].index(current_prob) if current_prob in ["Classification", "Regression"] else 0
        problem_type = st.selectbox("Problem Type", ["Classification", "Regression"], index=prob_index)
    
    if st.button("Save Configuration"):
        config_data = {
            "filename": saved_filename,
            "target": target,
            "problem_type": problem_type,
            "session_name": session_name
        }
        log_event("configuration_saved", config_data)
        st.success("Configuration Saved! You can now proceed to EDA.")
        
    if st.button("Next: EDA ➡️"):
         st.switch_page("pages/2_EDA.py")
