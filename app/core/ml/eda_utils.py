import pandas as pd
import numpy as np
import io

def generate_eda_summary(df: pd.DataFrame) -> dict:
    """
    Generates a statistical summary of the dataframe for the LLM.
    """
    summary = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_types": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(), # Series to dict int64 -> int
        "duplicates": int(df.duplicated().sum()),
        "numerical_stats": df.describe().to_dict(),
        # "categorical_stats": {col: df[col].value_counts().head(5).to_dict() for col in df.select_dtypes(include=['object', 'category']).columns}
    }
    
    # Convert numpy types to native python types for serialization
    for key, value in summary["missing_values"].items():
        summary["missing_values"][key] = int(value)
        
    # Add correlation for numerical columns (simplified)
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty and len(numeric_df.columns) > 1:
        corr = numeric_df.corr().abs().unstack()
        # Filter self-correlation and duplicates
        pairs = corr.sort_values(ascending=False)
        # Filter out self-correlation (1.0) and keep top 10
        pairs = pairs[pairs < 1.0] 
        high_corr = pairs[pairs > 0.8].head(10).to_dict()
        
        # Convert tuple keys to string and values to float
        summary["high_correlations"] = {str(k): float(v) for k, v in high_corr.items()}
        
    return summary

def format_summary_for_llm(summary: dict) -> str:
    """
    Converts the summary dict to a readable string for the prompt.
    """
    text = f"Dataset Shape: {summary['rows']} rows, {summary['columns']} columns.\n\n"
    text += "Column Types:\n" + str(summary['column_types']) + "\n\n"
    text += "Missing Values:\n" + str(summary['missing_values']) + "\n\n"
    text += "Duplicates: " + str(summary['duplicates']) + "\n\n"
    
    if "high_correlations" in summary:
        text += "High Correlations (>0.8):\n" + str(summary['high_correlations']) + "\n\n"
        
    return text
