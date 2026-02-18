import pandas as pd
import os
from app.core.ml.trainer import ModelTrainer

def run_optimization(file_path: str, target_col: str, problem_type: str, configs: list, metric: str, experiment_name: str) -> str:
    if not os.path.exists(file_path):
        return "File not found"
        
    try:
        df = pd.read_csv(file_path)
        trainer = ModelTrainer(experiment_name=experiment_name)
        status = trainer.run_optuna_study(df, target_col, problem_type, configs, metric)
        return status
    except Exception as e:
        return f"Error: {e}"
