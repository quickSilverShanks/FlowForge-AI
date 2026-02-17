import streamlit as st
import requests
import pandas as pd
import os
from app.ui.session_manager import log_event, initialize_session, load_session_state

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="Data Upload", layout="wide")

# Ensure session state is loaded
load_session_state()

st.title("📂 Data Upload & Problem Definition")

with st.expander("ℹ️ Instructions", expanded=True):
    st.write("""
    1. Upload your training dataset (CSV or Parquet).
    2. Review the first few rows.
    3. Define your target variable and problem type.
    """)

# Session Naming
session_name = st.text_input("Session Name (Optional)", value=st.session_state.get("session_name", ""), placeholder="e.g., Credit Fraud Detection")
if session_name:
    initialize_session(session_name)

uploaded_file = st.file_uploader("Choose a file", type=["csv", "parquet"])

if uploaded_file is not None:
    # Save file to backend
    with st.spinner("Uploading..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post(f"{API_URL}/data/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                st.success(f"File '{data['filename']}' uploaded successfully!")
                
                # Display Preview
                st.subheader("Data Preview")
                filepath = data['filepath']
                
                uploaded_file.seek(0)
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file, nrows=5)
                else:
                    df = pd.read_parquet(uploaded_file).head(5)
                
                st.dataframe(df)
                
                st.divider()
                st.subheader("Problem Definition")
                
                col1, col2 = st.columns(2)
                with col1:
                    target = st.selectbox("Select Target Column", df.columns, index=0 if "target" not in st.session_state else list(df.columns).index(st.session_state.get("target")) if st.session_state.get("target") in df.columns else 0)
                with col2:
                    problem_type = st.selectbox("Problem Type", ["Classification", "Regression"], index=0 if "problem_type" not in st.session_state else ["Classification", "Regression"].index(st.session_state.get("problem_type")))
                
                if st.button("Save Configuration"):
                    config_data = {
                        "filename": data['filename'],
                        "target": target,
                        "problem_type": problem_type,
                        "session_name": session_name
                    }
                    log_event("configuration_saved", config_data)
                    st.success("Configuration Saved! You can now proceed to EDA.")
                    
                if st.button("Next: EDA ➡️"):
                     st.switch_page("pages/2_EDA.py")
                    
            else:
                st.error(f"Upload failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")
