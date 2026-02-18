import streamlit as st
import requests
import os

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="Final Report", layout="wide")

from app.ui.components.orchestrator import render_orchestrator_sidebar
render_orchestrator_sidebar()

st.title("📑 Final Documentation & RAG Chat")

st.markdown("""
### Project Complete! 
You can now chat with your project history to generate reports or answer questions.
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat Interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about your model development (e.g., 'Why did we remove the Cabin column?')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(f"{API_URL}/chat/ask", json={"question": prompt})
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer provided.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    err = f"Error: {response.text}"
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})
            except Exception as e:
                st.error(f"Error: {e}")

# Next Button
st.divider()
col_next = st.columns([6, 1])[1]
with col_next:
    if st.button("Next: Session History ➡", type="primary"):
        st.switch_page("pages/9_History.py")
