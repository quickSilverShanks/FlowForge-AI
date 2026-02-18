from typing import List, Dict

AVAILABLE_MODELS = {
    "classification": ["xgboost", "lightgbm", "random_forest", "logistic_regression"],
    "regression": ["xgboost", "lightgbm", "random_forest", "linear_regression"]
}

def get_available_models(problem_type: str) -> List[str]:
    return AVAILABLE_MODELS.get(problem_type.lower(), [])

def validate_config(config: dict) -> bool:
    # Basic validation
    return "model_type" in config and "params" in config
