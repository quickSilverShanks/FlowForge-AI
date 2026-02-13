import pandas as pd
import numpy as np
import mlflow
import shap
import matplotlib.pyplot as plt
from fairlearn.metrics import MetricFrame, selection_rate, false_positive_rate, false_negative_rate
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import os

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
mlflow.set_tracking_uri(MLFLOW_URI)

class Evaluator:
    def load_best_model(self, experiment_name: str = "flowforge_experiment", metric: str = "accuracy"):
        # Find best run
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if not experiment:
                return None
            
            order_by = f"metrics.best_{metric} DESC" if metric in ['accuracy', 'f1'] else f"metrics.best_{metric} ASC"
            
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=[order_by],
                max_results=1
            )
            
            if runs.empty:
                return None
                
            run_id = runs.iloc[0].run_id
            model_uri = f"runs:/{run_id}/model"
            return mlflow.sklearn.load_model(model_uri)
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def evaluate_fairness(self, model, df: pd.DataFrame, target: str, sensitive_col: str):
        X = df.drop(columns=[target])
        y = df[target]
        sensitive_features = df[sensitive_col]
        
        y_pred = model.predict(X)
        
        # Define metrics
        metrics = {
            'accuracy': accuracy_score,
            'precision': precision_score,
            'recall': recall_score,
            'selection_rate': selection_rate
        }
        
        mf = MetricFrame(
            metrics=metrics,
            y_true=y,
            y_pred=y_pred,
            sensitive_features=sensitive_features
        )
        
        return {
            "overall": mf.overall.to_dict(),
            "by_group": mf.by_group.to_dict(),
            "difference": mf.difference().to_dict(),
            "ratio": mf.ratio().to_dict()
        }

    def generate_explanation(self, model, df: pd.DataFrame, target: str):
        """
        Generates SHAP values.
        """
        X = df.drop(columns=[target])
        # Use a sample for speed
        X_sample = X.sample(min(100, len(X)))
        
        # KernelExplainer works for any model, TreeExplainer is faster for Trees
        # Try TreeExplainer first if available (XGB, LightGBM, RF)
        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_sample)
        except:
            # Fallback to KernelExplainer (slow)
            explainer = shap.KernelExplainer(model.predict, X_sample)
            shap_values = explainer.shap_values(X_sample)
            
        # Return summary plot data or figure?
        # Returning raw values might be heavy. 
        # For simplicity, we can't easily send plot objects via API.
        # We'll save plot to static file or return feature importance dict.
        
        if isinstance(shap_values, list): # For classification
            vals = np.abs(shap_values[1]).mean(0)
        else:
            vals = np.abs(shap_values).mean(0)
            
        feature_importance = pd.DataFrame(list(zip(X.columns, vals)), columns=['col_name','feature_importance_vals'])
        feature_importance.sort_values(by=['feature_importance_vals'], ascending=False, inplace=True)
        
        return feature_importance.head(20).to_dict(orient='records')
