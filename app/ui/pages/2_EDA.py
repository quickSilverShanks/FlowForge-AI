import streamlit as st
import requests
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from app.ui.session_manager import log_event, save_page_state, get_page_state, get_current_session_id
from app.api.routers.eda import DATA_DIR

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="EDA", layout="wide")

st.set_page_config(page_title="EDA", layout="wide")

from app.ui.components.orchestrator import render_orchestrator_sidebar
render_orchestrator_sidebar()

# --- Sidebar Session Info ---
session_id = get_current_session_id()
session_name = st.session_state.get("session_name", f"Session {session_id}")
st.sidebar.info(f"**Active Session:**\n{session_name}")
# -----------------------------

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
                target = st.session_state.get("target") # Fetch from Data Upload
                
                # Pass session_id and target to backend for context and report naming
                payload = {
                    "filename": filename, 
                    "problem_definition": problem_def, 
                    "session_id": session_id,
                    "target_col": target
                }
                response = requests.post(f"{API_URL}/eda/analyze", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    saved_stats = data['stats']
                    saved_analysis = data['analysis']
                    
                    # Log event
                    log_event("eda_analysis", {
                        "filename": filename,
                        "analysis": saved_analysis,
                        "stats_summary": saved_stats,
                        "problem_definition": problem_def,
                        "target": target
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
        with st.expander("📊 Statistical Summary Tables (Cleaned Data)", expanded=False):
            
            # Duplicates Report
            dupes = saved_stats.get("duplicates", 0)
            orig_rows = saved_stats.get("rows_original", 0)
            if dupes > 0:
                st.warning(f"⚠️ **{dupes}** duplicate rows were detected and **dropped**! (Original: {orig_rows}, Cleaned: {saved_stats.get('rows_cleaned')})")
            
            # Excel Report Link
            report_path = saved_stats.get("report_path")
            if report_path and os.path.exists(report_path):
                 st.success(f"📈 Detailed Excel Report generated: `{report_path}`")
            
            # Display Tables nicely
            tabs = st.tabs(["Overview", "Missing Values", "Numerical Stats", "Categorical Stats", "Correlation Matrix"])
            
            with tabs[0]:
                st.json({k:v for k,v in saved_stats.items() if k not in ["missing_values", "numerical_stats", "categorical_stats", "correlations", "high_correlations", "column_types"]})
                
            with tabs[1]:
                 st.table(pd.DataFrame(list(saved_stats.get("missing_values", {}).items()), columns=["Column", "Missing Count"]))
                 
            with tabs[2]:
                if "numerical_stats" in saved_stats:
                    st.dataframe(pd.DataFrame(saved_stats["numerical_stats"]))
                    
            with tabs[3]:
                if "categorical_stats" in saved_stats and saved_stats["categorical_stats"]:
                    cat_data = []
                    for col, stats in saved_stats["categorical_stats"].items():
                        stats["Column"] = col
                        cat_data.append(stats)
                    st.dataframe(pd.DataFrame(cat_data).set_index("Column"))
                else:
                    st.info("No categorical features found.")
            
            with tabs[4]:
                 if "correlations" in saved_stats:
                    # Heatmap-style dataframe
                    st.dataframe(pd.DataFrame(saved_stats["correlations"]))
                 elif "high_correlations" in saved_stats:
                    st.table(pd.DataFrame(list(saved_stats.get("high_correlations", {}).items()), columns=["Pair", "Correlation"]))

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
            
            # Boolean to string for categorical plotting
            bool_cols = df.select_dtypes(include=['bool']).columns
            for col in bool_cols:
                df[col] = df[col].astype(str)
                
            # Column Selection
            all_columns = df.columns.tolist()
            selected_col = st.selectbox("Select Column to Explore", all_columns)
            
            # Toggle for Integer -> Categorical
            treat_as_cat = False
            if pd.api.types.is_integer_dtype(df[selected_col]):
                treat_as_cat = st.checkbox("Treat Integer as Categorical", value=False)
            
            if st.button(f"Explore '{selected_col}'"):
                st.markdown(f"### Analysis of **{selected_col}**")
                col_data = df[selected_col]
                
                # Visualizations
                fig, ax = plt.subplots(figsize=(10, 6)) # Larger figure to accommodate overlapping
                
                is_numeric = pd.api.types.is_numeric_dtype(col_data) and not treat_as_cat
                
                if is_numeric:
                    # Numeric: Histogram + Boxplot
                    plt.subplot(1, 2, 1)
                    sns.histplot(col_data, kde=True)
                    plt.title("Distribution")
                    plt.xticks(rotation=90)
                    
                    plt.subplot(1, 2, 2)
                    sns.boxplot(x=col_data)
                    plt.title("Boxplot")
                    plt.xticks(rotation=90)
                    
                else:
                    # Categorical: Count Plot
                    # Top 10 Categories
                    top_10 = col_data.value_counts().nlargest(10)
                    total_count = len(col_data.dropna())
                    
                    st.write(f"**Unique Categories:** {col_data.nunique()}")
                    
                    # Create plot
                    sns.barplot(x=top_10.index.astype(str), y=top_10.values, palette="viridis")
                    plt.title("Top 10 Categories")
                    plt.xlabel(selected_col)
                    plt.ylabel("Count")
                    plt.xticks(rotation=90) # Rotate X-axis labels
                    
                    # Dataframe for top 10
                    top_10_df = pd.DataFrame({
                        "Count": top_10.values,
                        "Percent": (top_10.values / total_count * 100).round(2)
                    }, index=top_10.index)
                    st.dataframe(top_10_df)

                plt.tight_layout() # Fix Overlapping
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
