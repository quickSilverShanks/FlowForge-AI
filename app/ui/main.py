import streamlit as st

from app.ui.session_manager import list_sessions, load_session, initialize_session, get_current_session_id

st.set_page_config(page_title="FlowForge AI", page_icon="🚀", layout="wide")

# Sidebar Session Management
st.sidebar.title("🧠 Session Manager")

# Active Session Display
current_id = get_current_session_id()
current_name = st.session_state.get("session_name", f"Session {current_id}")
st.sidebar.info(f"**Active Session:**\n{current_name}")

# New Session
if st.sidebar.button("➕ Start New Session", use_container_width=True):
    initialize_session()
    st.rerun()

# Load Session
with st.sidebar.expander("📂 Load Previous Session"):
    sessions = list_sessions()
    if sessions:
        # Create a dict for easy lookup
        session_map = {f"{s['name']} ({s['created_at'][:10]})": s['id'] for s in sessions}
        selected_name = st.selectbox("Select Session", list(session_map.keys()))
        
        if st.button("Load Session", use_container_width=True):
            selected_id = session_map[selected_name]
            load_session(selected_id)
    else:
        st.write("No previous sessions found.")

st.sidebar.divider()
st.sidebar.success("Select a page above.")

st.markdown("""
Welcome to **FlowForge AI**. This platform automates your Machine Learning lifecycle using AI Agents.

### 🚀 Workflow
1. **Data Upload**: Upload your dataset and define the problem.
2. **EDA**: thorough automated analysis and "Vibe Check".
3. **Feature Engineering**: AI-suggested transformations.
4. **Model Training**: AutoML with Optuna and MLflow tracking.
5. **Validation**: OOT evaluation and fairness checks.
6. **Monitoring**: Drift detection setup.
7. **Report**: Chat with your project to generate documentation.

**Get started by selecting 'Data Upload' from the sidebar.**
""")
