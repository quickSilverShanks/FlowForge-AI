import streamlit as st
import json
from app.ui.session_manager import list_sessions, get_history, load_session_state, get_current_session_id

st.set_page_config(page_title="Session History", layout="wide")

from app.ui.components.orchestrator import render_orchestrator_sidebar
render_orchestrator_sidebar()

load_session_state()

# Sidebar Session Info removed (handled by orchestrator)

st.title("📜 Session History")

# Sidebar for session selection (Rename variable to avoid conflict)
all_sessions = list_sessions()
session_options = {s["name"] + f" ({s['created_at']})": s["id"] for s in all_sessions}

selected_session_name = st.selectbox("Select Session to View", list(session_options.keys()))

if selected_session_name:
    session_id = session_options[selected_session_name]
    history = get_history(session_id)
    
    st.divider()
    st.subheader(f"Session: {history.get('session_name', session_id)}")
    st.caption(f"ID: {session_id} | Created: {history.get('created_at', 'Unknown')}")
    
    st.markdown("### ⏳ Timeline")
    
    timeline = history.get("timeline", [])
    
    if not timeline:
        st.info("No events logged for this session yet.")
    
    for event in timeline:
        timestamp = event.get("timestamp", "").split("T")[1].split(".")[0] # Simple time extraction
        event_type = event.get("type", "Unknown").replace("_", " ").title()
        content = event.get("content", {})
        
        with st.chat_message("assistant" if event_type == "Eda Analysis" else "user"):
            st.write(f"**{event_type}** at {timestamp}")
            
            if event_type == "Configuration Saved":
                st.json(content)
            elif event_type == "Eda Analysis":
                with st.expander("Analysis Result"):
                    st.markdown(content.get("analysis", ""))
                st.write("Stats Summary:")
                st.json(content.get("stats_summary", {}))
            elif event_type == "User Feedback":
                st.write(f"> {content.get('content', '')}")
            else:
                st.json(content)
