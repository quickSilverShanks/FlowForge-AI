import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, LabelEncoder, FunctionTransformer
from sklearn.pipeline import Pipeline

class FeatureEngine:
    def apply_plan(self, df: pd.DataFrame, plan: dict) -> pd.DataFrame:
        """
        Applies the transformation plan to the dataframe.
        This is a simplified implementation. Real-world would use Sklearn Pipelines properly to persist state.
        For this prototype, we'll apply transformations directly/step-by-step or build a composite pipeline.
        
        To allow OOT validation later, we MUST return a fitted pipeline.
        But for the interactive UI, we often just want the transformed data.
        
        Hybrid approach:
        We will build a ColumnTransformer based on the plan.
        """
        transformers = []
        
        # Group by operation to build ColumnTransformer
        # Note: This simple logic assumes non-conflicting steps (e.g. impute then scale on same col is hard with just one ColumnTransformer without chaining).
        # A more robust way is to use a Pipeline for each column, but that's verbose.
        # Let's simple apply manually for the "Interactive" aspect, and just log the steps for the final pipeline.
        
        df_transformed = df.copy()
        
        for step in plan['steps']:
            col = step['column']
            op = step['operation']
            
            if col not in df_transformed.columns and op != 'drop':
                continue
                
            if op == 'drop':
                if col in df_transformed.columns:
                    df_transformed.drop(columns=[col], inplace=True)
            
            elif op == 'impute_mean':
                df_transformed[col] = df_transformed[col].fillna(df_transformed[col].mean())
            
            elif op == 'impute_median':
                df_transformed[col] = df_transformed[col].fillna(df_transformed[col].median())
                
            elif op == 'log_transform':
                 # Handle zeros/negatives
                 if (df_transformed[col] > 0).all():
                     df_transformed[col] = np.log1p(df_transformed[col])
                     
            elif op == 'one_hot':
                # Pandas get_dummies is easier for interactive view than OneHotEncoder
                dummies = pd.get_dummies(df_transformed[col], prefix=col, drop_first=True)
                df_transformed = pd.concat([df_transformed, dummies], axis=1)
                df_transformed.drop(columns=[col], inplace=True)
                
            elif op == 'label_encode':
                le = LabelEncoder()
                # Handle NaNs before encoding if not imputed
                df_transformed[col] = df_transformed[col].astype(str)
                df_transformed[col] = le.fit_transform(df_transformed[col])
                
            elif op == 'standard_scale':
                scaler = StandardScaler()
                df_transformed[[col]] = scaler.fit_transform(df_transformed[[col]])
            
            elif op == 'minmax_scale':
                scaler = MinMaxScaler()
                df_transformed[[col]] = scaler.fit_transform(df_transformed[[col]])
                
        return df_transformed
