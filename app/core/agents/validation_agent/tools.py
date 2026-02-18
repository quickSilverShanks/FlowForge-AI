import pandas as pd
import os
from app.core.ml.evaluator import Evaluator

def evaluate_best_model(file_path: str, target_col: str, experiment_name: str, metric: str) -> dict:
    if not os.path.exists(file_path):
        return {"error": "File not found"}
        
    try:
        df = pd.read_csv(file_path)
        evaluator = Evaluator()
        model = evaluator.load_best_model(experiment_name=experiment_name, metric=metric)
        
        if not model:
            return {"error": "No model found in experiment"}
            
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        # Simple evaluation (In-sample if passed training data, or hold-out if passed separate validation data)
        # Assuming classification for simplicity, need to handle regression
        score = model.score(X, y)
        
        return {
            "metric": metric,
            "score": score,
            "dataset_rows": len(df)
        }
    except Exception as e:
        return {"error": str(e)}
