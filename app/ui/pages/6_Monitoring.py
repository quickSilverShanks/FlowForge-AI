import streamlit as st
import json

st.set_page_config(page_title="Monitoring", layout="wide")
st.title("📡 Monitoring & Governance")

st.info("Define monitoring thresholds for your deployed model.")

with st.expander("Drift Detection Settings", expanded=True):
    col1, col2 = st.columns(2)
    method = col1.selectbox("Drift Method", ["alibi-detect", "evidently", "ks-test"])
    threshold = col2.slider("P-Value Threshold", 0.01, 0.10, 0.05)
    
    features_to_monitor = st.multiselect("Features to Monitor", ["Age", "Fare", "Sex", "Pclass", "SibSp"], default=["Age", "Fare"])

with st.expander("Performance Decay", expanded=True):
    metric = st.selectbox("Metric", ["Accuracy", "F1", "RMSE"])
    decay_threshold = st.number_input("Trigger Retraining if drops below", 0.0, 1.0, 0.8)

if st.button("Generate Monitoring Plan"):
    plan = {
        "drift": {
            "method": method,
            "threshold": threshold,
            "features": features_to_monitor
        },
        "performance": {
            "metric": metric,
            "threshold": decay_threshold
        }
    }
    
    st.success("Plan Generated")
    st.json(plan)
    
    st.download_button("Download Config", json.dumps(plan, indent=2), "monitoring_config.json")
