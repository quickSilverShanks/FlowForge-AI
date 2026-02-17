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
        "categorical_stats": {}
    }
    
    # Categorical Stats
    cat_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns
    for col in cat_cols:
        summary["categorical_stats"][col] = {
            "unique": int(df[col].nunique()),
            "missing": int(df[col].isnull().sum()),
            "top": str(df[col].mode().iloc[0]) if not df[col].mode().empty else "N/A",
            "freq": int(df[col].value_counts().iloc[0]) if not df[col].empty else 0
        }

    # Convert numpy types to native python types for serialization
    for key, value in summary["missing_values"].items():
        summary["missing_values"][key] = int(value)
        
    # Correlations (Full Matrix for numeric)
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty and len(numeric_df.columns) > 1:
        corr_matrix = numeric_df.corr().round(4)
        # Convert to dict of dicts for JSON serialization
        summary["correlations"] = corr_matrix.to_dict()
        
    return summary

def format_summary_for_llm(summary: dict) -> str:
    """
    Converts the summary dict to a readable string for the prompt.
    """
    text = f"Dataset Shape: {summary['rows']} rows, {summary['columns']} columns.\n\n"
    text += "Column Types:\n" + str(summary['column_types']) + "\n\n"
    text += "Missing Values:\n" + str(summary['missing_values']) + "\n\n"
    text += "Duplicates: " + str(summary['duplicates']) + "\n\n"
    
    if summary["categorical_stats"]:
        text += "Categorical Statistics (Unique, Missing, Top, Freq):\n" + str(summary['categorical_stats']) + "\n\n"
    
    # For LLM, we might not want the FULL correlation matrix if it's huge, 
    # but we can provide high correlations still or a summary.
    # Let's extract high correlations manually for the text prompt to avoid token limit overflow
    if "correlations" in summary:
        high_corrs = []
        corr_dict = summary["correlations"]
        for col1, values in corr_dict.items():
            for col2, val in values.items():
                if col1 != col2 and abs(val) > 0.7:
                     # Avoid duplicates (col1-col2 and col2-col1)
                     if col1 < col2: 
                        high_corrs.append(f"{col1} - {col2}: {val}")
        
        if high_corrs:
            text += "High Correlations (>0.7):\n" + str(high_corrs[:20]) + "\n\n" # Limit to top 20 for prompt
        
    return text

def generate_excel_report(df: pd.DataFrame, summary: dict, output_path: str):
    """
    Saves the EDA summary and raw data samples to an Excel file with multiple sheets.
    """
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: General Summary
            general_data = {
                "Metric": ["Rows", "Columns", "Duplicates (Checked)", "Missing Values Total"],
                "Value": [summary["rows"], summary["columns"], summary["duplicates"], sum(summary["missing_values"].values())]
            }
            pd.DataFrame(general_data).to_excel(writer, sheet_name="Overview", index=False)
            
            # Sheet 2: Column Types
            pd.DataFrame(list(summary["column_types"].items()), columns=["Column", "Type"]).to_excel(writer, sheet_name="Column Types", index=False)
            
            # Sheet 3: Missing Values
            pd.DataFrame(list(summary["missing_values"].items()), columns=["Column", "Missing Count"]).to_excel(writer, sheet_name="Missing Values", index=False)
            
            # Sheet 4: Numerical Stats
            if "numerical_stats" in summary:
                pd.DataFrame(summary["numerical_stats"]).to_excel(writer, sheet_name="Numerical Stats")

            # Sheet 5: Categorical Stats
            if "categorical_stats" in summary and summary["categorical_stats"]:
                 cat_report = []
                 for col, stats in summary["categorical_stats"].items():
                     stats["Column"] = col
                     cat_report.append(stats)
                 pd.DataFrame(cat_report).set_index("Column").to_excel(writer, sheet_name="Categorical Stats")
                
            # Sheet 6: Correlations (Full Matrix)
            if "correlations" in summary:
                 pd.DataFrame(summary["correlations"]).to_excel(writer, sheet_name="Correlation Matrix")
                 
            # Sheet 7: Data Sample
            df.head(20).to_excel(writer, sheet_name="Data Sample (First 20)", index=False)
            
        return True
    except Exception as e:
        print(f"Error generating Excel report: {e}")
        return False
