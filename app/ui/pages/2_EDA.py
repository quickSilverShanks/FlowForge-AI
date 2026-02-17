import streamlit as st
import requests
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from app.ui.session_manager import log_event, save_page_state, get_page_state
from app.api.routers.eda import DATA_DIR # Ensure correct path import

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="EDA", layout="wide")

st.title("🔍 Exploratory Data Analysis")

# Auto-load filename from session
default_filename = st.session_state.get("filename", "")
filename = st.text_input("Filename (uploaded previously)", value=default_filename)

if not filename:
    st.warning("Please upload a file in the 'Data Upload' page first.")
    if st.button("Go to Data Upload"):
        st.switch_page("pages/1_Data_Upload.py")
else:
    # --- 1. AI Analysis & Stats (Persisted) ---
    st.subheader("🤖 Automated Analysis")
    
    # Load Page State
    page_state = get_page_state("EDA")
    saved_analysis = page_state.get("analysis", "")
    saved_stats = page_state.get("stats", {})

    # Action Button
    if st.button("Run AI Analysis" if not saved_analysis else "Regenerate Analysis"):
        with st.spinner("Agent is analyzing your data..."):
            try:
                problem_def = st.session_state.get("problem_definition", "General EDA")
                payload = {"filename": filename, "problem_definition": problem_def}
                response = requests.post(f"{API_URL}/eda/analyze", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    saved_stats = data['stats']
                    saved_analysis = data['analysis']
                    
                    # Log event
                    log_event("eda_analysis", {
                        "filename": filename,
                        "analysis": saved_analysis,
                        "problem_definition": problem_def
                    })
                    
                    # Save Page State
                    save_page_state("EDA", {
                        "analysis": saved_analysis,
                        "stats": saved_stats,
                        "timestamp": pd.Timestamp.now().isoformat()
                    })
                    st.rerun()
                else:
                    st.error(f"Analysis failed: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")

    # Display Persisted Content (Collapsible)
    if saved_analysis:
        with st.expander("📄 AI Vibe Check & Analysis", expanded=True):
            st.markdown(saved_analysis)

    if saved_stats:
        with st.expander("📊 Statistical Summary Table", expanded=False):
            st.json(saved_stats) # Using JSON for now as stats structure varies

    st.divider()

    # --- 2. Interactive Exploration (Transient) ---
    st.subheader("🕵️ Interactive Data Exploration")
    
    # Load Data Directly (Read-only, for plotting)
    try:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_parquet(filepath)
            
            # Column Selection
            all_columns = df.columns.tolist()
            selected_col = st.selectbox("Select Column to Explore", all_columns)
            
            if st.button(f"Explore '{selected_col}'"):
                st.markdown(f"### Analysis of **{selected_col}**")
                col_data = df[selected_col]
                
                # Basic Stats
                c1, c2, c3 = st.columns(3)
                dtype = str(col_data.dtype)
                missing = col_data.isnull().sum()
                non_missing = col_data.count()
                
                c1.metric("Type", dtype)
                c2.metric("Missing", f"{missing} ({missing/len(df):.1%})")
                c3.metric("Non-Missing", non_missing)
                
                # Visualizations
                fig, ax = plt.subplots(figsize=(10, 4))
                
                if pd.api.types.is_numeric_dtype(col_data):
                    # Numeric: Histogram + Boxplot
                    plt.subplot(1, 2, 1)
                    sns.histplot(col_data, kde=True)
                    plt.title("Distribution")
                    
                    plt.subplot(1, 2, 2)
                    sns.boxplot(x=col_data)
                    plt.title("Boxplot")
                    
                else:
                    # Categorical: Count Plot
                    # Top 10 Categories
                    top_10 = col_data.value_counts().nlargest(10)
                    total_count = len(col_data.dropna())
                    
                    st.write(f"**Unique Categories:** {col_data.nunique()}")
                    
                    sns.barplot(x=top_10.values, y=top_10.index, hue=top_10.index, legend=False)
                    plt.title("Top 10 Categories")
                    plt.xlabel("Count")
                    
                    # Dataframe for top 10
                    top_10_df = pd.DataFrame({
                        "Count": top_10.values,
                        "Percent": (top_10.values / total_count * 100).round(2)
                    }, index=top_10.index)
                    st.dataframe(top_10_df)

                st.pyplot(fig)
                
        else:
            st.error(f"File not found on server: {filepath}")
            
    except Exception as e:
        st.error(f"Could not load file for exploration: {e}")

    st.divider()

    # --- 3. Feedback Loop ---
    st.subheader("Feedback Loop")
    feedback = st.text_area("Observations or Instructions for Feature Engineering", placeholder="e.g., 'Drop the PassengerId column', 'Handle missing Age by median'")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Save Feedback"):
            if feedback:
                log_event("user_feedback", {"page": "EDA", "content": feedback})
                st.success("Feedback Logged!")
            else:
                st.warning("Please enter feedback first.")
    
    with col2:
         if st.button("Next: Feature Engineering ➡️"):
            st.switch_page("pages/3_Feature_Engineering.py")
