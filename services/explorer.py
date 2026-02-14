import pandas as pd
import numpy as np
from scipy import stats
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')


def run_exploration(parquet_path: str) -> dict:
    """
    Runs full exploratory analysis on a Parquet file.
    Returns a structured dict (the Data DNA) ready to store in Supabase.
    """
    df = pd.read_parquet(parquet_path)
    
    return {
        "row_count":            _row_count(df),
        "col_count":            len(df.columns),
        "columns":              _column_profiles(df),
        "baselines":            _baselines(df),
        "health":               _health(df),
        "correlations":         _correlations(df),
        "datetime_info":        _datetime_info(df),
        "detected_patterns":    _detect_patterns(df),
        "suggested_queries":    _suggest_queries(df),
        "accumulated_insights": [],
    }


# ── Helpers ───────────────────────────────────────────────────

def _row_count(df):
    return int(df.shape[0])

def _column_profiles(df) -> list:
    profiles = []
    for col in df.columns:
        s = df[col]
        n_total   = len(s)
        n_missing = int(s.isna().sum())
        n_valid   = n_total - n_missing
        n_unique  = int(s.nunique(dropna=True))
        col_type  = _detect_type(s)
        
        profile = {
            "name":        col,
            "type":        col_type,
            "dtype":       str(s.dtype),
            "null_pct":    round(n_missing / n_total * 100, 2) if n_total else 0,
            "unique_count": n_unique,
            "is_constant": n_unique <= 1,
            "is_id_like":  n_unique == n_valid and n_valid > 10,
        }
        
        # Extra stats per type
        if col_type == "numeric":
            clean = s.dropna()
            profile.update({
                "mean":     round(float(clean.mean()), 4) if len(clean) else None,
                "std":      round(float(clean.std()), 4)  if len(clean) else None,
                "min":      round(float(clean.min()), 4)  if len(clean) else None,
                "max":      round(float(clean.max()), 4)  if len(clean) else None,
                "median":   round(float(clean.median()), 4) if len(clean) else None,
                "skewness": round(float(clean.skew()), 4)   if len(clean) else None,
                "zeros_pct": round((clean == 0).sum() / len(clean) * 100, 2) if len(clean) else 0,
                "outlier_count": int((np.abs(stats.zscore(clean)) > 3).sum()) if len(clean) > 2 else 0,
            })
        
        elif col_type in ("categorical", "boolean"):
            vc = s.value_counts()
            profile.update({
                "top_values": [str(v) for v in vc.head(5).index.tolist()],
                "top_value":  str(vc.index[0]) if len(vc) else None,
                "top_value_pct": round(vc.iloc[0] / n_valid * 100, 2) if len(vc) and n_valid else 0,
                "suggested_role": _suggest_role(col, s),
            })
        
        elif col_type == "datetime":
            parsed = pd.to_datetime(s, errors='coerce').dropna()
            if len(parsed):
                profile.update({
                    "min_date":   str(parsed.min()),
                    "max_date":   str(parsed.max()),
                    "span_days":  int((parsed.max() - parsed.min()).days),
                    "peak_hour":  int(parsed.dt.hour.value_counts().idxmax()),
                    "peak_day":   str(parsed.dt.day_name().value_counts().idxmax()),
                })
        
        profiles.append(profile)
    return profiles

def _detect_type(s: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(s):
        return "datetime"
    if pd.api.types.is_bool_dtype(s):
        return "boolean"
    if pd.api.types.is_numeric_dtype(s):
        return "numeric"
    # Check if object column looks like datetime
    if s.dtype == object:
        try:
            parsed = pd.to_datetime(s, errors='coerce', infer_datetime_format=True)
            if parsed.notna().sum() / len(s) > 0.7:
                return "datetime"
        except:
            pass
    return "categorical"

def _suggest_role(col: str, s: pd.Series) -> str:
    col_lower = col.lower()
    if any(w in col_lower for w in ["status", "result", "outcome", "label", "flag"]):
        return "target_metric"
    if any(w in col_lower for w in ["category", "type", "group", "segment"]):
        return "dimension"
    if s.nunique() <= 2:
        return "binary_flag"
    return "dimension"

def _baselines(df) -> dict:
    baselines = {}
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in num_cols:
        clean = df[col].dropna()
        if len(clean):
            baselines[col] = {
                "mean":   round(float(clean.mean()), 4),
                "median": round(float(clean.median()), 4),
                "std":    round(float(clean.std()), 4),
            }
    
    # Detect status/failure columns and compute rates
    for col in df.columns:
        col_lower = col.lower()
        if "status" in col_lower or "result" in col_lower:
            vc = df[col].value_counts(normalize=True)
            for val in vc.index:
                val_lower = str(val).lower()
                if any(w in val_lower for w in ["fail", "error", "decline", "reject"]):
                    baselines[f"{col}_failure_rate"] = round(float(vc[val]) * 100, 4)
    
    return baselines

def _health(df) -> dict:
    total_cells   = df.shape[0] * df.shape[1]
    missing_cells = int(df.isna().sum().sum())
    dupe_rows     = int(df.duplicated().sum())
    constant_cols = [c for c in df.columns if df[c].nunique() <= 1]
    
    completeness = round((total_cells - missing_cells) / total_cells * 100, 2) if total_cells else 0
    
    # Simple health score
    score = 100
    score -= (missing_cells / total_cells * 100) * 0.5 if total_cells else 0
    score -= (dupe_rows / df.shape[0] * 100) * 0.3 if df.shape[0] else 0
    score -= len(constant_cols) * 2
    score = max(0.0, round(score, 2))
    
    return {
        "score":          score,
        "completeness":   completeness,
        "duplicate_rows": dupe_rows,
        "duplicate_pct":  round(dupe_rows / df.shape[0] * 100, 2) if df.shape[0] else 0,
        "constant_cols":  constant_cols,
        "missing_cells":  missing_cells,
    }

def _correlations(df) -> list:
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) < 2:
        return []
    
    corr = df[num_cols].corr(method='pearson')
    pairs = []
    
    for i in range(len(num_cols)):
        for j in range(i + 1, len(num_cols)):
            a, b = num_cols[i], num_cols[j]
            r = round(float(corr.loc[a, b]), 4)
            if abs(r) >= 0.3:   # only meaningful correlations
                pairs.append({
                    "col_a":     a,
                    "col_b":     b,
                    "pearson_r": r,
                    "strength":  "strong" if abs(r) >= 0.7 else "moderate",
                })
    
    return sorted(pairs, key=lambda x: abs(x["pearson_r"]), reverse=True)[:10]

def _datetime_info(df) -> dict:
    for col in df.columns:
        s = df[col]
        col_type = _detect_type(s)
        if col_type == "datetime":
            parsed = pd.to_datetime(s, errors='coerce').dropna()
            if len(parsed):
                return {
                    "column":     col,
                    "peak_hour":  int(parsed.dt.hour.value_counts().idxmax()),
                    "peak_day":   str(parsed.dt.day_name().value_counts().idxmax()),
                    "span_days":  int((parsed.max() - parsed.min()).days),
                    "hour_distribution": parsed.dt.hour.value_counts().sort_index().to_dict(),
                    "day_distribution":  parsed.dt.day_name().value_counts().to_dict(),
                }
    return {}

def _detect_patterns(df) -> list:
    patterns = []
    
    # Peak hour pattern
    for col in df.columns:
        if _detect_type(df[col]) == "datetime":
            parsed = pd.to_datetime(df[col], errors='coerce').dropna()
            if len(parsed):
                peak = parsed.dt.hour.value_counts().idxmax()
                patterns.append(f"Peak activity at {peak}:00 hrs")
    
    # Failure rate pattern
    for col in df.columns:
        if any(w in col.lower() for w in ["status", "result"]):
            vc = df[col].value_counts(normalize=True)
            for val in vc.index:
                if any(w in str(val).lower() for w in ["fail", "error", "decline"]):
                    pct = round(vc[val] * 100, 1)
                    patterns.append(f"{pct}% {val} rate detected in '{col}'")
    
    # High cardinality
    for col in df.select_dtypes(include='object').columns:
        if df[col].nunique() > 100:
            patterns.append(f"'{col}' has high cardinality ({df[col].nunique()} unique values)")
    
    # Skewed numerics
    for col in df.select_dtypes(include=[np.number]).columns:
        skew = df[col].skew()
        if abs(skew) > 2:
            patterns.append(f"'{col}' is heavily skewed (skewness: {round(skew, 2)})")
    
    # Strong correlations
    corrs = _correlations(df)
    for c in corrs[:2]:
        if c["strength"] == "strong":
            patterns.append(
                f"Strong correlation between '{c['col_a']}' and '{c['col_b']}' (r={c['pearson_r']})"
            )
    
    return patterns[:8]   # cap at 8

def _suggest_queries(df) -> list:
    queries = []
    col_names = [c.lower() for c in df.columns]
    
    # Status/failure based
    for col in df.columns:
        if any(w in col.lower() for w in ["status", "result", "outcome"]):
            queries.append(f"What is the overall {col} breakdown?")
            queries.append(f"Which category has the highest failure rate?")
            break
    
    # Numeric aggregations
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols:
        queries.append(f"Show the distribution of {num_cols[0]}")
        if len(num_cols) > 1:
            queries.append(f"What is the average {num_cols[0]} by category?")
    
    # Datetime trends
    for col in df.columns:
        if _detect_type(df[col]) == "datetime":
            queries.append("Show trends over time")
            queries.append("What are the peak activity hours?")
            break
    
    # Outliers
    for col in num_cols[:2]:
        queries.append(f"Are there any outliers in {col}?")
    
    return queries[:5]   # cap at 5
