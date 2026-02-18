import pandas as pd
import os

def get_columns(file_path: str) -> list:
    if not os.path.exists(file_path):
        return []
    df = pd.read_csv(file_path, nrows=0)
    return df.columns.tolist()

def save_selected_features(file_path: str, selected_features: list, output_path: str) -> str:
    if not os.path.exists(file_path):
        return "File not found"
        
    try:
        df = pd.read_csv(file_path)
        # Ensure all selected features exist
        valid_features = [f for f in selected_features if f in df.columns]
        if not valid_features:
            return "No valid features selected"
            
        df_selected = df[valid_features]
        df_selected.to_csv(output_path, index=False)
        return output_path
    except Exception as e:
        return f"Error: {e}"
