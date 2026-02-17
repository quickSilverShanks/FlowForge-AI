import streamlit as st
import json
import os
import glob
from datetime import datetime

HISTORY_DIR = "app/project_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

def get_current_session_id():
    if "session_id" not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    return st.session_state.session_id

def _load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def _save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def initialize_session(session_name=None):
    """Initializes the session file with metadata if it doesn't exist."""
    session_id = get_current_session_id()
    filepath = os.path.join(HISTORY_DIR, f"session_{session_id}.json")
    
    if not os.path.exists(filepath):
        data = {
            "session_id": session_id,
            "session_name": session_name or f"Session {session_id}",
            "created_at": datetime.now().isoformat(),
            "config": {},
            "timeline": []
        }
        _save_json(filepath, data)
        
    # Also load into session state if needed, or ensuring session name is set
    if session_name:
         st.session_state.session_name = session_name

def log_event(event_type: str, content: dict):
    """
    Logs an event to the session timeline.
    content: dict containing details of the event.
    """
    session_id = get_current_session_id()
    filepath = os.path.join(HISTORY_DIR, f"session_{session_id}.json")
    
    data = _load_json(filepath)
    
    # Ensure structure exists if file was created by older version
    if "timeline" not in data: data["timeline"] = []
    
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "content": content
    }
    
    data["timeline"].append(event)
    
    # Update global config if this is a config event
    if event_type == "configuration_saved":
        data["config"] = content
        # Sync to session state for easy access in other tabs
        for k, v in content.items():
            st.session_state[k] = v
            
    _save_json(filepath, data)

def get_history(session_id=None):
    """Returns the full history dict for a session."""
    if not session_id:
        session_id = get_current_session_id()
        
    filepath = os.path.join(HISTORY_DIR, f"session_{session_id}.json")
    return _load_json(filepath)

def list_sessions():
    """Returns a list of available session files."""
    files = glob.glob(os.path.join(HISTORY_DIR, "session_*.json"))
    sessions = []
    for f in files:
        data = _load_json(f)
        sessions.append({
            "id": data.get("session_id", os.path.basename(f).replace("session_", "").replace(".json", "")),
            "name": data.get("session_name", "Untitled Session"),
            "created_at": data.get("created_at", "")
        })
    # Sort by created_at desc
    sessions.sort(key=lambda x: x["created_at"], reverse=True)
    return sessions

def load_session_state():
    """Loads critical config from current session file into st.session_state on app load."""
    history = get_history()
    if "config" in history:
        for k, v in history["config"].items():
            st.session_state[k] = v
