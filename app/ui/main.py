import streamlit as st

st.set_page_config(page_title="FlowForge AI", page_icon="🚀", layout="wide")

st.title("FlowForge AI 🚀")
st.markdown("### Agentic MLflow Model Development & Governance Platform")

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
