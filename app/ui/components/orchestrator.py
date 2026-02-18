import streamlit as st
import requests
import json
import os
from app.ui.session_manager import get_current_session_id, log_event

API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")
from app.ui.session_manager import list_sessions, load_session, initialize_session

def process_orchestrator_request(prompt: str, extra_context: dict = None):
    """
    Processes a user request via the Orchestrator API.
    Updates st.session_state.messages with the interaction.
    """
    # 1. Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Prepare Context
    session_id = get_current_session_id()
    context = {
        "session_id": session_id,
        "project_summary": f"Session ID: {session_id}",
        # Add current page state if needed
        "current_page": st.session_state.get("current_page", "Unknown")
    }
    
    if extra_context:
        context.update(extra_context)
    
    # 3. Call API
    try:
        with st.spinner("🤖 Orchestrator is planning and executing..."):
            response = requests.post(
                f"{API_BASE_URL}/orchestrator/run",
                json={"user_request": prompt, "context": context}
            )
        
        if response.status_code == 200:
            result = response.json()
            
            # Format Output
            plan = result.get("plan", [])
            results = result.get("results", [])
            
            output_text = "### 📋 Plan\n"
            for i, step in enumerate(plan):
                output_text += f"{i+1}. **{step.get('agent')}**: {step.get('instruction')}\n"
            
            output_text += "\n### 🚀 Execution Results\n"
            for res in results:
                status = res.get("status", "unknown")
                output_text += f"- **{res.get('agent')}**: {status}\n"
                if "message" in res:
                    output_text += f"  - {res['message']}\n"
            
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            log_event("orchestrator_command", {"prompt": prompt, "result": result})
            
        else:
            error_msg = f"❌ Error: {response.text}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
    except Exception as e:
        error_msg = f"❌ Connection Error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})


def render_orchestrator_sidebar():
    """
    Renders the Orchestrator chat interface in the sidebar.
    """
    with st.sidebar:
        st.title("🧠 Session Manager")
        
        # Active Session Display
        current_id = get_current_session_id()
        current_name = st.session_state.get("session_name", f"Session {current_id}")
        st.info(f"**Active Session:**\n{current_name}")
        
        # New Session
        if st.button("➕ Start New Session", key="new_session_btn", use_container_width=True):
            initialize_session()
            st.rerun()

        # Load Session
        with st.expander("📂 Load Previous Session"):
            sessions = list_sessions()
            if sessions:
                # Create a dict for easy lookup
                session_map = {f"{s['name']} ({s['created_at'][:10]})": s['id'] for s in sessions}
                selected_name = st.selectbox("Select Session", list(session_map.keys()), key="load_session_select")
                
                if st.button("Load Session", key="load_session_btn", use_container_width=True):
                    selected_id = session_map[selected_name]
                    load_session(selected_id)
            else:
                st.write("No previous sessions found.")
        
        st.divider()
        st.title("🤖 Orchestrator")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Chat History Display
        messages_container = st.container(height=400, border=True)
        with messages_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Input Area
        with st.form(key="orchestrator_form", clear_on_submit=True):
            prompt = st.text_area("Tell me what to do:", height=100, placeholder="e.g., Load data.csv and perform EDA...")
            submitted = st.form_submit_button("Run 🚀")
            
        if submitted and prompt:
            process_orchestrator_request(prompt)
            st.rerun()
