import pandas as pd
import os
from app.core.ml.evaluator import Evaluator

def generate_shap_explanation(file_path: str, target_col: str, experiment_name: str) -> list:
    if not os.path.exists(file_path):
        return []
        
    try:
        df = pd.read_csv(file_path)
        evaluator = Evaluator()
        # Load best model from experiment
        model = evaluator.load_best_model(experiment_name=experiment_name)
        
        if not model:
            return []
            
        explanation = evaluator.generate_explanation(model, df, target_col)
        return explanation
    except Exception as e:
        return []
