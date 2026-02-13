import streamlit as st
import requests
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="EDA", layout="wide")
st.title("🔍 Exploratory Data Analysis")

# Session State for Filename (Mock persistence or passed via query params if using simple multipage)
# In real app, might want to list files from backend
# For now, let user input filename or pick from memory if we had it
filename = st.text_input("Filename (uploaded previously)", value="train.csv") # Default for testing

if st.button("Run AI Analysis"):
    with st.spinner("Agent is analyzing your data... (This uses LLM, might take a minute)"):
        try:
            payload = {"filename": filename, "problem_definition": "User provided definition here"}
            response = requests.post(f"{API_URL}/eda/analyze", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                stats = data['stats']
                analysis = data['analysis']
                
                # Top Level Metrics
                c1, c2, c3 = st.columns(3)
                c1.metric("Rows", stats['rows'])
                c2.metric("Columns", stats['columns'])
                c3.metric("Duplicates", stats['duplicates'])
                
                # Agent Analysis
                st.subheader("🤖 Agent Vibe Check")
                st.markdown(analysis)
                
                # Visualizations (recreating basic ones)
                # Ideally we fetch the specific data needed for plots, or just use the summary
                st.subheader("📊 Key Correlations")
                if "high_correlations" in stats:
                    st.write(stats['high_correlations'])
                else:
                    st.info("No high correlations found or not calculated.")
                
            else:
                st.error(f"Analysis failed: {response.text}")
                
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.subheader("Feedback Loop")
feedback = st.text_area("Observations or Instructions for Feature Engineering", placeholder="e.g., 'Drop the PassengerId column', 'Handle missing Age by median'")
if st.button("Save Feedback"):
    # TODO: Log this feedback to SessionLogger via an endpoint
    st.success("Feedback Saved!")
