"""Data exploration service - generates Data DNA from Parquet files."""
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

def run_exploration(parquet_path: str) -> Dict[str, Any]:
    """Run pandas profiling on Parquet file and generate Data DNA.
    
    Args:
        parquet_path: Path to local Parquet file
        
    Returns:
        Data DNA dictionary with columns, baselines, patterns, etc.
    """
    df = pd.read_parquet(parquet_path)
    
    # 1. Schema Profiling
    columns = []
    for col in df.columns:
        col_info = {
            "name": col,
            "null_pct": round(df[col].isnull().sum() / len(df) * 100, 2),
            "unique_count": int(df[col].nunique())
        }
        
        # Detect type and add type-specific stats
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info["type"] = "numeric"
            col_info["min"] = float(df[col].min()) if not df[col].isnull().all() else None
            col_info["max"] = float(df[col].max()) if not df[col].isnull().all() else None
            col_info["mean"] = float(df[col].mean()) if not df[col].isnull().all() else None
            col_info["std"] = float(df[col].std()) if not df[col].isnull().all() else None
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            col_info["type"] = "datetime"
            if not df[col].isnull().all():
                col_info["min_date"] = str(df[col].min())
                col_info["max_date"] = str(df[col].max())
        elif pd.api.types.is_bool_dtype(df[col]):
            col_info["type"] = "boolean"
            col_info["true_count"] = int(df[col].sum())
            col_info["false_count"] = int((~df[col]).sum())
        else:
            col_info["type"] = "categorical"
            top_values = df[col].value_counts().head(5).to_dict()
            col_info["top_values"] = {str(k): int(v) for k, v in top_values.items()}
        
        columns.append(col_info)
    
    # 2. Statistical Baselines
    baselines = {
        "total_rows": len(df),
        "total_columns": len(df.columns)
    }
    
    # Add numeric column averages
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if not df[col].isnull().all():
            baselines[f"avg_{col}"] = float(df[col].mean())
    
    # 3. Pattern Detection
    detected_patterns = []
    
    # Check for datetime columns
    datetime_cols = df.select_dtypes(include=['datetime64']).columns
    if len(datetime_cols) > 0:
        detected_patterns.append(f"Time-series data detected with {len(datetime_cols)} datetime column(s)")
    
    # Check for high null columns
    high_null_cols = [col for col in df.columns if df[col].isnull().sum() / len(df) > 0.3]
    if high_null_cols:
        detected_patterns.append(f"{len(high_null_cols)} column(s) with >30% missing values")
    
    # Check for low cardinality categoricals (good for GROUP BY)
    categorical_cols = df.select_dtypes(include=['object']).columns
    low_card_cols = [col for col in categorical_cols if df[col].nunique() < 20]
    if low_card_cols:
        detected_patterns.append(f"{len(low_card_cols)} categorical column(s) suitable for grouping")
    
    # 4. Suggested Queries
    suggested_queries = []
    
    if len(numeric_cols) > 0:
        suggested_queries.append(f"What is the distribution of {numeric_cols[0]}?")
    
    if len(low_card_cols) > 0:
        suggested_queries.append(f"Show breakdown by {low_card_cols[0]}")
    
    if len(datetime_cols) > 0:
        suggested_queries.append(f"Show trends over time")
    
    if len(numeric_cols) > 1:
        suggested_queries.append(f"What is the correlation between {numeric_cols[0]} and {numeric_cols[1]}?")
    
    suggested_queries.append("Show summary statistics")
    
    # 5. Assemble Data DNA
    data_dna = {
        "columns": columns,
        "baselines": baselines,
        "detected_patterns": detected_patterns,
        "suggested_queries": suggested_queries[:5],  # Limit to 5
        "accumulated_insights": [],
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    return data_dna
