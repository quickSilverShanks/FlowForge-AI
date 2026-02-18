import streamlit as st
import json
import os
import glob
from datetime import datetime

HISTORY_DIR = "app/project_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

def get_current_session_id():
    """Returns the active session ID from state, or creates a new one if missing."""
    if "session_id" not in st.session_state:
        # If no session is active, initialize a default new one
        initialize_session() 
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
    """Creates a new session and sets it as active."""
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(HISTORY_DIR, f"session_{session_id}.json")
    
    data = {
        "session_id": session_id,
        "session_name": session_name or f"Session {session_id}",
        "created_at": datetime.now().isoformat(),
        "config": {},     # Global config (filename, target, etc.)
        "page_states": {}, # Per-page persistent state (EDA analysis, Feature Plan, etc.)
        "timeline": []    # Log of events
    }
    _save_json(filepath, data)
    
    # Reset Session State
    st.session_state.clear()
    st.session_state.session_id = session_id
    st.session_state.session_name = data["session_name"]
    st.session_state.page_states = {}
    return session_id

def load_session(session_id):
    """Loads an existing session into st.session_state."""
    filepath = os.path.join(HISTORY_DIR, f"session_{session_id}.json")
    if not os.path.exists(filepath):
        st.error(f"Session file not found: {filepath}")
        return

    data = _load_json(filepath)
    
    # Clear current state and populate with loaded data
    st.session_state.clear()
    st.session_state.session_id = data.get("session_id", session_id)
    st.session_state.session_name = data.get("session_name", f"Session {session_id}")
    
    # Load Global Config
    for k, v in data.get("config", {}).items():
        st.session_state[k] = v
        
    # Load Page States (critical for returning to tabs)
    st.session_state.page_states = data.get("page_states", {})

    st.success(f"Loaded session: {st.session_state.session_name}")
    st.rerun()

def save_page_state(page_key, state_data):
    """
    Saves the state of a specific page to the session JSON.
    page_key: Unique identifier for the page (e.g., 'EDA', 'FeatureEngineering')
    state_data: Dict containing the data to persist (e.g., {'analysis': '...', 'plot_data': ...})
    """
    session_id = get_current_session_id()
    filepath = os.path.join(HISTORY_DIR, f"session_{session_id}.json")
    
    data = _load_json(filepath)
    
    # Update page_states
    if "page_states" not in data:
        data["page_states"] = {}
    
    data["page_states"][page_key] = state_data
    
    # Sync to current runtime state
    if "page_states" not in st.session_state:
        st.session_state.page_states = {}
    st.session_state.page_states[page_key] = state_data
    
    _save_json(filepath, data)

def get_page_state(page_key):
    """Retrieves the state for a specific page."""
    if "page_states" not in st.session_state:
        st.session_state.page_states = {}
    return st.session_state.page_states.get(page_key, {})

def get_all_page_states():
    """Retrieves the state for all pages in the current session."""
    if "page_states" not in st.session_state:
        st.session_state.page_states = {}
    return st.session_state.page_states

def log_event(event_type: str, content: dict):
    """Logs an event to the session timeline and updates config if needed."""
    session_id = get_current_session_id()
    filepath = os.path.join(HISTORY_DIR, f"session_{session_id}.json")
    
    data = _load_json(filepath)
    
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
        for k, v in content.items():
            st.session_state[k] = v
            
    _save_json(filepath, data)

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
    sessions.sort(key=lambda x: x["created_at"], reverse=True)
    return sessions
