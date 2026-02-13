import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="Data Upload", layout="wide")

st.title("📂 Data Upload & Problem Definition")

with st.expander("ℹ️ Instructions", expanded=True):
    st.write("""
    1. Upload your training dataset (CSV or Parquet).
    2. Review the first few rows.
    3. Define your target variable and problem type.
    """)

uploaded_file = st.file_uploader("Choose a file", type=["csv", "parquet"])

if uploaded_file is not None:
    # Save file to backend
    with st.spinner("Uploading..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post(f"{API_URL}/data/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                st.success(f"File '{data['filename']}' uploaded successfully!")
                
                # Display Preview
                st.subheader("Data Preview")
                filepath = data['filepath']
                # In a real app, we might need a separate endpoint to get head, 
                # but here we can't read the file from backend path directly if UI is in separate container 
                # UNLESS they share the volume. 
                # Docker Compose mounts `./app:/app`, so they share the code, BUT `./flowforge_data:/app/data` is the data volume.
                # Both attach `flowforge_data:/app/data` (check docker-compose).
                # Wait, my docker-compose:
                # Backend: volumes: - ./app:/app, - flowforge_data:/app/data
                # UI: volumes: - ./app:/app
                # The UI container DOES NOT have `flowforge_data` mounted!
                # I should mount it to UI as well if I want to read it directly, OR fetch via API.
                # Fetching via API is cleaner architecture, but mounting is faster for EDA.
                # Let's check the plan. I didn't specify mounting data to UI.
                # I'll update docker-compose to mount the data volume to UI for performance/simplicity in this local setup.
                
                # For now, I'll just rely on the response providing columns, or simple display.
                # Actually, standard streamlit `file_uploader` object `uploaded_file` is already in memory/temp. 
                # I can read it directly here for preview BEFORE upload? Or AFTER?
                # Streamlit `uploaded_file` is a BytesIO. I can read it with pandas.
                
                uploaded_file.seek(0)
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file, nrows=5)
                else:
                    df = pd.read_parquet(uploaded_file).head(5)
                
                st.dataframe(df)
                
                st.divider()
                st.subheader("Problem Definition")
                
                col1, col2 = st.columns(2)
                with col1:
                    target = st.selectbox("Select Target Column", df.columns)
                with col2:
                    problem_type = st.selectbox("Problem Type", ["Classification", "Regression"])
                
                if st.button("Save Configuration"):
                    # TODO: Save this config to backend
                    st.success("Configuration Saved! (Mock)")
                    
            else:
                st.error(f"Upload failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")
