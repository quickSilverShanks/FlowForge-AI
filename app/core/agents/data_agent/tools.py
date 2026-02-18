import pandas as pd
import os
from app.core.ml import eda_utils

def generate_eda(file_path: str) -> dict:
    """
    Generates EDA summary from a CSV file.
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        df = pd.read_csv(file_path)
        summary = eda_utils.generate_eda_summary(df)
        return summary
    except Exception as e:
        return {"error": str(e)}

def generate_report(file_path: str, summary: dict, output_dir: str) -> str:
    """
    Generates an Excel report for the EDA.
    """
    if not os.path.exists(file_path):
        return "File not found"
        
    try:
        df = pd.read_csv(file_path)
        output_path = os.path.join(output_dir, "eda_report.xlsx")
        success = eda_utils.generate_excel_report(df, summary, output_path)
        return output_path if success else "Failed to generate report"
    except Exception as e:
        return f"Error: {e}"
