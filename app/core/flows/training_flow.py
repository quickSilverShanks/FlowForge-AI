from prefect import flow, task
from app.core.ml.trainer import ModelTrainer
import pandas as pd
from app.api.routers.eda import DATA_DIR
from app.core.utils.logger import SessionLogger

@task(name="Load Data")
def load_data(filename: str):
    filepath = f"{DATA_DIR}/{filename}"
    if filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    else:
        return pd.read_parquet(filepath)

@task(name="Run Optuna Optimization")
def run_optimization(df: pd.DataFrame, target: str, problem_type: str, configs: list, metric: str):
    trainer = ModelTrainer()
    result = trainer.run_optuna_study(df, target, problem_type, configs, metric)
    return result

@flow(name="Model Training Flow")
def run_training_flow(filename: str, target: str, problem_type: str, configs: list, metric: str, session_id: str):
    logger = SessionLogger(session_id)
    logger.log_step("Model Training", f"Started training flow for {filename} with models: {[c['model_type'] for c in configs]}")
    
    try:
        df = load_data(filename)
        result = run_optimization(df, target, problem_type, configs, metric)
        logger.log_step("Model Training Completed", f"Result: {result}")
        return result
    except Exception as e:
        logger.log_step("Model Training Failed", str(e))
        raise e
