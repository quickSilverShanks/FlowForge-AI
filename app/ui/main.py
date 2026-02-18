import streamlit as st

from app.ui.session_manager import list_sessions, load_session, initialize_session, get_current_session_id
from app.ui.components.orchestrator import render_orchestrator_sidebar

st.set_page_config(page_title="FlowForge AI", page_icon="🚀", layout="wide")

render_orchestrator_sidebar()

# Sidebar is handled by render_orchestrator_sidebar()
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
