import pandas as pd
import numpy as np
from app.core.ml.feature_engine import FeatureEngine
from typing import List, Dict

def apply_feature_plan(file_path: str, plan: dict, output_path: str) -> str:
    """
    Applies the feature engineering plan to the dataset.
    Plan format: {"steps": [{"column": "col_name", "operation": "op_name", "reasoning": "..."}]}
    """
    if not os.path.exists(file_path):
        return "File not found"
        
    try:
        df = pd.read_csv(file_path)
        fe = FeatureEngine()
        df_transformed = fe.apply_plan(df, plan)
        
        df_transformed.to_csv(output_path, index=False)
        return output_path
    except Exception as e:
        return f"Error: {e}"

import os
