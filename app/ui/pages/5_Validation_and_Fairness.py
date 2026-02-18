import streamlit as st
import requests
import os
import pandas as pd

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="Validation & Fairness", layout="wide")
st.set_page_config(page_title="Validation & Fairness", layout="wide")

from app.ui.components.orchestrator import render_orchestrator_sidebar
render_orchestrator_sidebar()

st.title("⚖️ Validation & Fairness")

filename = st.text_input("Validation Dataset", value=st.session_state.get("current_filename", "transformed_train.csv"))
target = st.text_input("Target Column", value="Survived")
sensitive = st.text_input("Sensitive Column (for Fairness)", placeholder="Sex")

if st.button("Run Fairness Assessment"):
    if not sensitive:
        st.error("Please specify a sensitive column.")
    else:
        with st.spinner("Evaluating Fairness..."):
            try:
                payload = {
                    "filename": filename,
                    "target": target,
                    "sensitive_column": sensitive
                }
                response = requests.post(f"{API_URL}/evaluation/fairness", json=payload)
                
                if response.status_code == 200:
                    metrics = response.json()
                    st.success("Analysis Completed!")
                    
                    st.subheader("Overall Metrics")
                    st.json(metrics['overall'])
                    
                    st.subheader("Metrics by Group")
                    st.table(pd.DataFrame(metrics['by_group']))
                    
                    st.subheader("Demographic Parity (Ratio)")
                    st.json(metrics['ratio'])
                    
                else:
                    st.error(f"Failed: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.subheader("🕵️ Model Explainability (SHAP)")

if st.button("Generate Feature Importance"):
    with st.spinner("Calculating SHAP values..."):
        try:
            payload = {
                "filename": filename,
                "target": target,
                "metric": "accuracy" # Todo: dynamic
            }
            response = requests.post(f"{API_URL}/evaluation/explain", json=payload)
            
            if response.status_code == 200:
                importance = response.json()
                st.success("Analysis Completed!")
                
                df_imp = pd.DataFrame(importance)
                st.bar_chart(df_imp.set_index("col_name"))
                
            else:
                st.error(f"Failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")
