import streamlit as st
import requests
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from app.ui.session_manager import log_event, load_session_state

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="EDA", layout="wide")

# Ensure session state is loaded
load_session_state()

st.title("🔍 Exploratory Data Analysis")

# Auto-load filename from session
default_filename = st.session_state.get("filename", "")
filename = st.text_input("Filename (uploaded previously)", value=default_filename)

if not filename:
    st.warning("Please upload a file in the 'Data Upload' page first.")
    if st.button("Go to Data Upload"):
        st.switch_page("pages/1_Data_Upload.py")
else:
    if st.button("Run AI Analysis"):
        with st.spinner("Agent is analyzing your data... (This uses LLM, might take a minute)"):
            try:
                # Check for existing problem definition or feedback
                problem_def = st.session_state.get("problem_definition", "General EDA")
                
                payload = {"filename": filename, "problem_definition": problem_def}
                response = requests.post(f"{API_URL}/eda/analyze", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    stats = data['stats']
                    analysis = data['analysis']
                    
                    # Log the analysis event
                    log_event("eda_analysis", {
                        "filename": filename,
                        "stats_summary": stats, # Store summary, maybe too large?
                        "analysis": analysis,
                        "problem_definition": problem_def
                    })
                    
                    # Top Level Metrics
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Rows", stats['rows'])
                    c2.metric("Columns", stats['columns'])
                    c3.metric("Duplicates", stats['duplicates'])
                    
                    # Agent Analysis
                    st.subheader("🤖 Agent Vibe Check")
                    st.markdown(analysis)
                    
                    # Visualizations (recreating basic ones)
                    st.subheader("📊 Key Correlations")
                    if "high_correlations" in stats:
                        st.write(stats['high_correlations'])
                    else:
                        st.info("No high correlations found or not calculated.")
                        
                    # Save analysis to session state for persistence within page reload
                    st.session_state["last_eda_analysis"] = analysis
                    
                else:
                    st.error(f"Analysis failed: {response.text}")
                    
            except Exception as e:
                st.error(f"Error: {e}")

    # Display previous analysis if available (mock versioning display could go here)
    if "last_eda_analysis" in st.session_state:
        if not st.session_state.get("last_eda_analysis"): # Handle empty case
             pass 
        # (Content is already displayed if just ran, but this keeps it after reload if we tracked it properly)

    st.divider()
    st.subheader("Feedback Loop")
    feedback = st.text_area("Observations or Instructions for Feature Engineering", placeholder="e.g., 'Drop the PassengerId column', 'Handle missing Age by median'")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Save Feedback & Update"):
            if feedback:
                # Log feedback
                log_event("user_feedback", {"page": "EDA", "content": feedback})
                st.success("Feedback Logged! (Future: This would trigger re-analysis)")
                # In future: call backend with feedback to regenerate
            else:
                st.warning("Please enter feedback first.")
    
    with col2:
         if st.button("Next: Feature Engineering ➡️"):
            st.switch_page("pages/3_Feature_Engineering.py")
