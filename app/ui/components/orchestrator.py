import streamlit as st
import requests
import json
import os
from app.ui.session_manager import get_current_session_id, log_event

API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

def render_orchestrator_sidebar():
    """
    Renders the Orchestrator chat interface in the sidebar.
    """
    with st.sidebar:
        st.divider()
        st.title("🤖 Orchestrator")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Chat History Display
        # Using an expander to keep it tidy, or a container
        with st.container(height=300, border=True):
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Input Area
        # Using a form to group input and button
        with st.form(key="orchestrator_form", clear_on_submit=True):
            prompt = st.text_area("Tell me what to do:", height=100, placeholder="e.g., Load data.csv and perform EDA...")
            submitted = st.form_submit_button("Run 🚀")
            
        if submitted and prompt:
            # Displays user message immediately
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

        # Check if we need to process the last message
        # If the last message is from user, it means we just submitted and reran, 
        # so now we need to generate response.
        # But we need to be careful not to re-process on every rerun if not new.
        # We can use a session state flag 'processing'
        
    # Logic to process - must be outside the form to allow UI updates
    # Actually, simpler logic:
    # If the last message is USER, we trigger the API call.
    # BUT Streamlit reruns the whole script. 
    # Let's do the processing inside the `if submitted:` block? 
    # No, `st.rerun` stops execution.
    
    # Better approach for sidebar form:
    # We can run the logic *after* the form if submitted.
    # But to update the history inside the container we just drew, we'd need to redraw it 
    # or rely on the next rerun.
    
    # Let's adjust:
    # 1. User submits.
    # 2. We append User Msg to state.
    # 3. We Call API.
    # 4. We append Assistant Msg to state.
    # 5. We rerun to show everything.
    
    if submitted and prompt:
        # 1. Add User Message (already done above conceptually, but let's do it here purely)
        # Note: We append to state, but we haven't drawn it yet in this run (or we drew old state).
        # We need to run the API *before* the final rerun.
        
        # Re-adding to ensure it's in history before API call logic (though we just appended it inside the form block above? No, I removed it to keep logic linear here)
        # st.session_state.messages.append({"role": "user", "content": prompt}) # Duplicate if I did it above.
        
        # Let's stick to: 
        # Inside form: just submit.
        # Outside form: process `prompt`? No, `prompt` is local to form.
        
        pass 
        # The variables `submitted` and `prompt` are available here.
        
        # Add User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Prepare context
        session_id = get_current_session_id()
        context = {
            "session_id": session_id,
            "project_summary": f"Session ID: {session_id}"
        }
        
        # Call API
        try:
            with st.spinner("Orchestrator is planning..."):
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
                error_msg = f"Error: {response.text}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
        except Exception as e:
            error_msg = f"Connection Error: {e}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
        st.rerun()
