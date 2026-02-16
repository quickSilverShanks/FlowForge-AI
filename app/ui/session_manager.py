import streamlit as st
import json
import os
from datetime import datetime

HISTORY_DIR = "project_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

def get_current_session_id():
    if "session_id" not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    return st.session_state.session_id

def save_session_history(key, value):
    """
    Saves a key-value pair to the current session's history file.
    Also updates st.session_state.
    """
    st.session_state[key] = value
    
    session_id = get_current_session_id()
    filepath = os.path.join(HISTORY_DIR, f"session_{session_id}.json")
    
    history = {}
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                pass
    
    history[key] = value
    
    with open(filepath, "w") as f:
        json.dump(history, f, indent=4)

def load_session_history():
    """
    Loads history from file into st.session_state if not already present.
    """
    session_id = get_current_session_id()
    filepath = os.path.join(HISTORY_DIR, f"session_{session_id}.json")
    
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                history = json.load(f)
                for k, v in history.items():
                    if k not in st.session_state:
                        st.session_state[k] = v
            except json.JSONDecodeError:
                pass
