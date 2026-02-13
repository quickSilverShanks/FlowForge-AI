import optuna
import mlflow
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, StratifiedKFold, KFold
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
import os

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
mlflow.set_tracking_uri(MLFLOW_URI)

class ModelTrainer:
    def __init__(self, experiment_name: str = "flowforge_experiment"):
        mlflow.set_experiment(experiment_name)
        
    def get_model_class(self, model_type: str, is_classification: bool):
        if model_type == 'xgboost':
            return XGBClassifier if is_classification else XGBRegressor
        elif model_type == 'lightgbm':
            return LGBMClassifier if is_classification else LGBMRegressor
        elif model_type == 'random_forest':
            return RandomForestClassifier if is_classification else RandomForestRegressor
        elif model_type == 'logistic_regression':
            return LogisticRegression if is_classification else LinearRegression
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def run_optuna_study(self, df: pd.DataFrame, target_col: str, problem_type: str, configs: list, metric: str, n_trials: int = 10):
        """
        Runs an Optuna study for each model config.
        """
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        is_classification = problem_type.lower() == 'classification'
        best_run = None
        
        for config in configs:
            model_type = config['model_type']
            
            def objective(trial):
                params = {}
                for p in config['params']:
                    if p['type'] == 'int':
                        params[p['name']] = trial.suggest_int(p['name'], int(p['low']), int(p['high']))
                    elif p['type'] == 'float':
                        params[p['name']] = trial.suggest_float(p['name'], p['low'], p['high'])
                    elif p['type'] == 'categorical':
                        params[p['name']] = trial.suggest_categorical(p['name'], p['choices'])
                
                model_cls = self.get_model_class(model_type, is_classification)
                
                # Handle special params like verbosity
                if model_type in ['xgboost', 'lightgbm']:
                    params['verbosity'] = 0
                
                model = model_cls(**params)
                
                cv = StratifiedKFold(n_splits=3) if is_classification else KFold(n_splits=3)
                
                scoring = 'accuracy' if metric == 'accuracy' else 'neg_mean_squared_error'
                if metric == 'f1': scoring = 'f1_macro'
                
                scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
                return scores.mean()

            direction = "maximize" if metric in ['accuracy', 'f1'] else "minimize" # MSE needs minimize, but sklearn returns neg_mse so maximize
            
            study = optuna.create_study(direction=direction)
            
            # Integrate MLflow
            with mlflow.start_run(run_name=f"{model_type}_optuna"):
                study.optimize(objective, n_trials=n_trials)
                
                mlflow.log_params(study.best_params)
                mlflow.log_metric(f"best_{metric}", study.best_value)
                mlflow.set_tag("model_type", model_type)
                
                # Log best model
                # Re-train on full data
                best_model_cls = self.get_model_class(model_type, is_classification)
                best_model = best_model_cls(**study.best_params)
                best_model.fit(X, y)
                
                mlflow.sklearn.log_model(best_model, "model")
                
        return "Training Completed"
