import pandas as pd
import numpy as np
from scipy import stats
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")


def run_exploration(parquet_path: str) -> dict:
    """
    Runs full exploratory analysis on a Parquet file.
    Returns a structured dict (the Data DNA) ready to store in Supabase.
    """
    df = pd.read_parquet(parquet_path)

    return {
        "row_count":            int(df.shape[0]),
        "col_count":            int(df.shape[1]),
        "columns":              _column_profiles(df),
        "baselines":            _baselines(df),
        "health":               _health(df),
        "correlations":         _correlations(df),
        "datetime_info":        _datetime_info(df),
        "detected_patterns":    _detect_patterns(df),
        "suggested_queries":    _suggest_queries(df),
        "missing_summary":      _missing_summary(df),
        "outlier_summary":      _outlier_summary(df),
        "segment_breakdown":    _segment_breakdown(df),
        "accumulated_insights": [],
    }


# ── Type Detection ─────────────────────────────────────────────────────────────

def _detect_type(s: pd.Series) -> str:
    """Robustly detect the logical type of a column."""
    if pd.api.types.is_datetime64_any_dtype(s):
        return "datetime"
    if pd.api.types.is_bool_dtype(s):
        return "boolean"
    if pd.api.types.is_numeric_dtype(s):
        # Low-cardinality ints are likely categoricals (e.g. flags, ratings)
        if s.dtype in (np.int8, np.int16, np.int32, np.int64) and s.nunique() <= 15:
            return "categorical_numeric"
        return "numeric"
    if s.dtype == object:
        # Try to parse as datetime
        try:
            parsed = pd.to_datetime(s, errors="coerce", infer_datetime_format=True)
            if parsed.notna().sum() / max(len(s), 1) > 0.7:
                return "datetime"
        except Exception:
            pass
        return "categorical"
    return "categorical"


def _suggest_role(col: str, s: pd.Series) -> str:
    """Guess the analytical role of a column from its name and values."""
    c = col.lower()
    if any(w in c for w in ["status", "result", "outcome", "label", "flag", "class", "target"]):
        return "target_metric"
    if any(w in c for w in ["id", "_id", "uuid", "key", "code"]) and s.nunique() > 50:
        return "identifier"
    if any(w in c for w in ["category", "type", "group", "segment", "region", "country", "city"]):
        return "dimension"
    if any(w in c for w in ["date", "time", "at", "created", "updated", "timestamp"]):
        return "temporal"
    if pd.api.types.is_numeric_dtype(s):
        if any(w in c for w in ["amount", "price", "revenue", "cost", "fee", "total", "balance"]):
            return "financial_metric"
        if any(w in c for w in ["count", "qty", "quantity", "num", "number"]):
            return "count_metric"
        return "measure"
    if s.nunique() <= 2:
        return "binary_flag"
    return "dimension"


# ── Column Profiles ────────────────────────────────────────────────────────────

def _column_profiles(df: pd.DataFrame) -> list:
    profiles = []

    for col in df.columns:
        s = df[col]
        n_total   = len(s)
        n_missing = int(s.isna().sum())
        n_valid   = n_total - n_missing
        n_unique  = int(s.nunique(dropna=True))
        col_type  = _detect_type(s)

        profile = {
            "name":         col,
            "type":         col_type,
            "dtype":        str(s.dtype),
            "null_count":   n_missing,
            "null_pct":     round(n_missing / n_total * 100, 2) if n_total else 0.0,
            "unique_count": n_unique,
            "unique_pct":   round(n_unique / n_valid * 100, 2) if n_valid else 0.0,
            "is_constant":  bool(n_unique <= 1),
            "is_id_like":   bool(n_unique == n_valid and n_valid > 10),
            "suggested_role": _suggest_role(col, s),
        }

        if col_type == "numeric":
            profile.update(_numeric_profile(s))

        elif col_type == "categorical_numeric":
            # Treat as category but include basic numeric stats too
            profile.update(_categorical_profile(s))
            clean = s.dropna()
            if len(clean):
                profile["mean"]   = round(float(clean.mean()), 4)
                profile["median"] = round(float(clean.median()), 4)

        elif col_type in ("categorical", "boolean"):
            profile.update(_categorical_profile(s))

        elif col_type == "datetime":
            profile.update(_datetime_profile(s))

        profiles.append(profile)

    return profiles


def _numeric_profile(s: pd.Series) -> dict:
    clean = s.dropna()
    if len(clean) == 0:
        return {}

    q1, q25, q50, q75, q99 = np.percentile(clean, [1, 25, 50, 75, 99])
    iqr = q75 - q25
    iqr_lo = q25 - 1.5 * iqr
    iqr_hi = q75 + 1.5 * iqr

    mean_val = float(clean.mean())
    std_val  = float(clean.std())

    outlier_count_iqr = int(((clean < iqr_lo) | (clean > iqr_hi)).sum())
    outlier_count_z   = int((np.abs(stats.zscore(clean)) > 3).sum()) if len(clean) > 2 else 0

    # Normality test (Shapiro only on a safe sample size)
    normality_p = None
    if 3 <= len(clean) <= 5000:
        _, normality_p = stats.shapiro(clean.sample(min(len(clean), 5000), random_state=42))
        normality_p = round(float(normality_p), 6)

    return {
        "mean":              round(mean_val, 4),
        "std":               round(std_val, 4),
        "cv":                round(std_val / mean_val, 4) if mean_val != 0 else None,
        "min":               round(float(clean.min()), 4),
        "p1":                round(float(q1), 4),
        "p25":               round(float(q25), 4),
        "median":            round(float(q50), 4),
        "p75":               round(float(q75), 4),
        "p99":               round(float(q99), 4),
        "max":               round(float(clean.max()), 4),
        "iqr":               round(float(iqr), 4),
        "skewness":          round(float(clean.skew()), 4),
        "kurtosis":          round(float(clean.kurtosis()), 4),
        "zeros_pct":         round((clean == 0).sum() / len(clean) * 100, 2),
        "negatives_pct":     round((clean < 0).sum() / len(clean) * 100, 2),
        "outlier_count_iqr": outlier_count_iqr,
        "outlier_count_z":   outlier_count_z,
        "outlier_pct":       round(outlier_count_iqr / len(clean) * 100, 2),
        "is_normal_p":       normality_p,              # p > 0.05 → likely normal
        "likely_normal":     bool(normality_p and normality_p > 0.05),
    }


def _categorical_profile(s: pd.Series) -> dict:
    vc      = s.value_counts(dropna=True)
    n_valid = int(s.notna().sum())

    if len(vc) == 0:
        return {}

    # Shannon entropy — higher = more balanced distribution
    probs   = vc / vc.sum()
    entropy = float(stats.entropy(probs.values))

    # Dominance: how much the top value dominates
    top_pct = round(vc.iloc[0] / n_valid * 100, 2) if n_valid else 0.0

    return {
        "top_values":    [str(v) for v in vc.head(5).index.tolist()],
        "top_value":     str(vc.index[0]),
        "top_value_count": int(vc.iloc[0]),
        "top_value_pct": top_pct,
        "rare_values":   int((vc == 1).sum()),           # values that appear only once
        "rare_pct":      round((vc == 1).sum() / len(vc) * 100, 2),
        "entropy":       round(entropy, 4),              # 0 = one value; high = balanced
        "is_dominated":  bool(top_pct > 80),             # one value covers 80%+ of data
    }


def _datetime_profile(s: pd.Series) -> dict:
    parsed = pd.to_datetime(s, errors="coerce").dropna()
    if len(parsed) == 0:
        return {}

    span_days = int((parsed.max() - parsed.min()).days)
    gaps      = parsed.sort_values().diff().dt.days.dropna()

    return {
        "min_date":          str(parsed.min()),
        "max_date":          str(parsed.max()),
        "span_days":         span_days,
        "span_years":        round(span_days / 365.25, 2),
        "peak_hour":         int(parsed.dt.hour.value_counts().idxmax()),
        "peak_day":          str(parsed.dt.day_name().value_counts().idxmax()),
        "peak_month":        int(parsed.dt.month.value_counts().idxmax()),
        "median_gap_days":   round(float(gaps.median()), 2) if len(gaps) else None,
        "max_gap_days":      round(float(gaps.max()), 2) if len(gaps) else None,
        "has_time_component": bool((parsed.dt.hour != 0).any()),
    }


# ── Baselines ──────────────────────────────────────────────────────────────────

def _baselines(df: pd.DataFrame) -> dict:
    baselines = {}
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in num_cols:
        clean = df[col].dropna()
        if len(clean) == 0:
            continue
        baselines[col] = {
            "mean":   round(float(clean.mean()), 4),
            "median": round(float(clean.median()), 4),
            "std":    round(float(clean.std()), 4),
            "sum":    round(float(clean.sum()), 4),
            "p90":    round(float(np.percentile(clean, 90)), 4),
        }

    # Detect status/failure columns and compute all category rates
    for col in df.columns:
        col_lower = col.lower()
        if any(w in col_lower for w in ["status", "result", "outcome", "state"]):
            vc = df[col].value_counts(normalize=True)
            for val in vc.index:
                val_lower = str(val).lower()
                if any(w in val_lower for w in ["fail", "error", "decline", "reject", "cancel"]):
                    baselines[f"{col}__failure_rate"] = round(float(vc[val]) * 100, 4)
                if any(w in val_lower for w in ["success", "complete", "approved", "pass"]):
                    baselines[f"{col}__success_rate"] = round(float(vc[val]) * 100, 4)

    return baselines


# ── Health ─────────────────────────────────────────────────────────────────────

def _health(df: pd.DataFrame) -> dict:
    total_cells    = df.shape[0] * df.shape[1]
    missing_cells  = int(df.isna().sum().sum())
    dupe_rows      = int(df.duplicated().sum())
    constant_cols  = [c for c in df.columns if df[c].nunique() <= 1]
    all_null_cols  = [c for c in df.columns if df[c].isna().all()]
    high_miss_cols = [c for c in df.columns if df[c].isna().sum() / len(df) > 0.5]
    completeness   = round((total_cells - missing_cells) / total_cells * 100, 2) if total_cells else 0.0

    # Per-column missing rates (only cols with any missing)
    missing_by_col = {
        c: round(df[c].isna().sum() / len(df) * 100, 2)
        for c in df.columns if df[c].isna().any()
    }

    # Health score (0–100)
    score = 100.0
    score -= (missing_cells / total_cells * 100) * 0.5 if total_cells else 0
    score -= (dupe_rows / df.shape[0] * 100) * 0.3 if df.shape[0] else 0
    score -= len(constant_cols) * 2
    score -= len(all_null_cols) * 3
    score -= len(high_miss_cols) * 1
    score  = max(0.0, round(score, 2))

    return {
        "score":             score,
        "grade":             _health_grade(score),
        "completeness":      completeness,
        "duplicate_rows":    dupe_rows,
        "duplicate_pct":     round(dupe_rows / df.shape[0] * 100, 2) if df.shape[0] else 0.0,
        "constant_cols":     constant_cols,
        "all_null_cols":     all_null_cols,
        "high_missing_cols": high_miss_cols,
        "missing_cells":     missing_cells,
        "missing_by_col":    missing_by_col,
    }


def _health_grade(score: float) -> str:
    if score >= 90: return "A"
    if score >= 75: return "B"
    if score >= 60: return "C"
    if score >= 40: return "D"
    return "F"


# ── Correlations ───────────────────────────────────────────────────────────────

def _correlations(df: pd.DataFrame) -> list:
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) < 2:
        return []

    corr_p = df[num_cols].corr(method="pearson")
    corr_s = df[num_cols].corr(method="spearman")

    pairs = []
    for i in range(len(num_cols)):
        for j in range(i + 1, len(num_cols)):
            a, b = num_cols[i], num_cols[j]
            pr = round(float(corr_p.loc[a, b]), 4)
            sr = round(float(corr_s.loc[a, b]), 4)
            if abs(pr) < 0.25:
                continue  # skip noise

            abs_pr = abs(pr)
            pairs.append({
                "col_a":       a,
                "col_b":       b,
                "pearson_r":   pr,
                "spearman_r":  sr,
                "direction":   "positive" if pr > 0 else "negative",
                "strength":    "strong" if abs_pr >= 0.7 else "moderate" if abs_pr >= 0.4 else "weak",
                "nonlinear":   bool(abs(sr) - abs_pr > 0.15),  # spearman >> pearson → nonlinear
            })

    return sorted(pairs, key=lambda x: abs(x["pearson_r"]), reverse=True)[:15]


# ── Datetime Info ──────────────────────────────────────────────────────────────

def _datetime_info(df: pd.DataFrame) -> dict:
    for col in df.columns:
        if _detect_type(df[col]) == "datetime":
            parsed = pd.to_datetime(df[col], errors="coerce").dropna()
            if len(parsed) == 0:
                continue

            hour_dist = parsed.dt.hour.value_counts().sort_index()
            day_dist  = parsed.dt.day_name().value_counts()
            month_dist= parsed.dt.month.value_counts().sort_index()

            # Business hours check (8am–6pm = hours 8–18)
            biz_hrs_pct = round(
                hour_dist[hour_dist.index.isin(range(8, 19))].sum() / len(parsed) * 100, 2
            )

            return {
                "column":              col,
                "peak_hour":           int(parsed.dt.hour.value_counts().idxmax()),
                "peak_day":            str(parsed.dt.day_name().value_counts().idxmax()),
                "peak_month":          int(parsed.dt.month.value_counts().idxmax()),
                "span_days":           int((parsed.max() - parsed.min()).days),
                "business_hours_pct":  biz_hrs_pct,
                "has_time_component":  bool((parsed.dt.hour != 0).any()),
                "hour_distribution":   {int(k): int(v) for k, v in hour_dist.items()},
                "day_distribution":    {str(k): int(v) for k, v in day_dist.items()},
                "month_distribution":  {int(k): int(v) for k, v in month_dist.items()},
            }
    return {}


# ── Missing Data Summary ───────────────────────────────────────────────────────

def _missing_summary(df: pd.DataFrame) -> dict:
    missing_cols = [c for c in df.columns if df[c].isna().any()]

    if not missing_cols:
        return {"has_missing": False, "affected_columns": 0, "affected_rows": 0}

    rows_with_any_missing = int(df[missing_cols].isna().any(axis=1).sum())
    rows_all_missing      = int(df.isna().all(axis=1).sum())

    # Co-occurrence (top pairs that go missing together)
    co_pairs = []
    miss_df  = df[missing_cols].isna().astype(int)
    seen     = set()
    for a in missing_cols:
        for b in missing_cols:
            if a == b or (b, a) in seen:
                continue
            seen.add((a, b))
            both = int((miss_df[a] & miss_df[b]).sum())
            if both > 0:
                co_pairs.append({"col_a": a, "col_b": b, "co_missing_count": both})

    co_pairs.sort(key=lambda x: -x["co_missing_count"])

    return {
        "has_missing":         True,
        "affected_columns":    len(missing_cols),
        "affected_column_names": missing_cols,
        "affected_rows":       rows_with_any_missing,
        "affected_rows_pct":   round(rows_with_any_missing / len(df) * 100, 2),
        "fully_empty_rows":    rows_all_missing,
        "co_missing_pairs":    co_pairs[:5],
    }


# ── Outlier Summary ────────────────────────────────────────────────────────────

def _outlier_summary(df: pd.DataFrame) -> list:
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    summary  = []

    for col in num_cols:
        clean = df[col].dropna()
        if len(clean) < 4:
            continue

        q25, q75 = np.percentile(clean, [25, 75])
        iqr      = q75 - q25
        lo, hi   = q25 - 1.5 * iqr, q75 + 1.5 * iqr

        iqr_mask     = (clean < lo) | (clean > hi)
        iqr_count    = int(iqr_mask.sum())
        extreme_mask = np.abs(stats.zscore(clean)) > 3
        extreme_count= int(extreme_mask.sum())

        if iqr_count == 0:
            continue

        summary.append({
            "column":           col,
            "iqr_outliers":     iqr_count,
            "iqr_outlier_pct":  round(iqr_count / len(clean) * 100, 2),
            "extreme_outliers": extreme_count,    # |z| > 3
            "lower_fence":      round(float(lo), 4),
            "upper_fence":      round(float(hi), 4),
            "min_outlier":      round(float(clean[iqr_mask].min()), 4) if iqr_count else None,
            "max_outlier":      round(float(clean[iqr_mask].max()), 4) if iqr_count else None,
        })

    return sorted(summary, key=lambda x: -x["iqr_outlier_pct"])


# ── Segment Breakdown ──────────────────────────────────────────────────────────

def _segment_breakdown(df: pd.DataFrame) -> list:
    """
    For each categorical column that looks like a dimension (≤25 unique values),
    compute numeric aggregations grouped by that column.
    This powers 'X by category' queries automatically.
    """
    cat_cols = [
        c for c in df.columns
        if _detect_type(df[c]) in ("categorical", "boolean")
        and df[c].nunique() <= 25
        and df[c].nunique() >= 2
    ]
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not cat_cols or not num_cols:
        return []

    breakdowns = []

    for cat_col in cat_cols[:4]:       # cap: 4 dimension columns
        for num_col in num_cols[:3]:   # cap: 3 numeric columns per dimension
            try:
                grp = df.groupby(cat_col, observed=True)[num_col].agg(
                    count="count",
                    mean="mean",
                    median="median",
                    std="std",
                    total="sum",
                ).dropna(how="all")

                grp = grp.round(4)
                grp.index = grp.index.astype(str)

                breakdowns.append({
                    "dimension": cat_col,
                    "metric":    num_col,
                    "data":      grp.reset_index().to_dict("records"),
                })
            except Exception:
                continue

    return breakdowns[:8]   # cap total segments returned


# ── Pattern Detection ──────────────────────────────────────────────────────────

def _detect_patterns(df: pd.DataFrame) -> list:
    patterns = []

    # Temporal patterns
    for col in df.columns:
        if _detect_type(df[col]) == "datetime":
            parsed = pd.to_datetime(df[col], errors="coerce").dropna()
            if len(parsed):
                peak_hour = parsed.dt.hour.value_counts().idxmax()
                patterns.append(f"Peak activity at {peak_hour}:00 hrs")
                peak_day = parsed.dt.day_name().value_counts().idxmax()
                patterns.append(f"Highest volume on {peak_day}s")

    # Failure / success rate patterns
    for col in df.columns:
        col_lower = col.lower()
        if any(w in col_lower for w in ["status", "result", "outcome"]):
            vc = df[col].value_counts(normalize=True)
            for val in vc.index:
                val_s = str(val)
                pct   = round(vc[val] * 100, 1)
                if any(w in val_s.lower() for w in ["fail", "error", "decline", "reject"]):
                    patterns.append(f"{pct}% '{val}' rate in '{col}'")
                if any(w in val_s.lower() for w in ["success", "complete", "approved"]):
                    patterns.append(f"{pct}% '{val}' rate in '{col}'")

    # Missing data patterns
    heavy_miss = [c for c in df.columns if df[c].isna().sum() / len(df) > 0.3]
    for col in heavy_miss:
        pct = round(df[col].isna().sum() / len(df) * 100, 1)
        patterns.append(f"'{col}' is {pct}% missing — may need imputation or removal")

    # High cardinality
    for col in df.select_dtypes(include="object").columns:
        uniq = df[col].nunique()
        if uniq > 100:
            patterns.append(f"'{col}' has very high cardinality ({uniq:,} unique values) — likely an ID or free-text field")

    # Skewed numerics
    for col in df.select_dtypes(include=[np.number]).columns:
        skew = df[col].skew()
        if abs(skew) > 2:
            direction = "right" if skew > 0 else "left"
            patterns.append(f"'{col}' is heavily {direction}-skewed (skewness={round(skew,2)}) — consider log transform")

    # Strong correlations
    for c in _correlations(df):
        if c["strength"] == "strong":
            note = " (possibly nonlinear)" if c.get("nonlinear") else ""
            patterns.append(
                f"Strong {c['direction']} correlation: '{c['col_a']}' ↔ '{c['col_b']}' (r={c['pearson_r']}){note}"
            )

    # Constant columns
    const = [c for c in df.columns if df[c].nunique() <= 1]
    if const:
        patterns.append(f"{len(const)} column(s) have no variance and can be dropped: {const}")

    # Duplicate rows
    dupes = int(df.duplicated().sum())
    if dupes > 0:
        patterns.append(f"{dupes:,} duplicate rows detected ({round(dupes/len(df)*100,1)}% of data)")

    return patterns[:10]   # cap at 10


# ── Suggested Queries ──────────────────────────────────────────────────────────

def _suggest_queries(df: pd.DataFrame) -> list:
    """Generate context-aware suggested queries based on what's actually in the dataset."""
    queries = []
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [
        c for c in df.columns
        if _detect_type(df[c]) in ("categorical", "boolean") and df[c].nunique() <= 25
    ]
    has_datetime = any(_detect_type(df[c]) == "datetime" for c in df.columns)

    # Status/outcome queries
    for col in df.columns:
        col_lower = col.lower()
        if any(w in col_lower for w in ["status", "result", "outcome"]):
            queries.append(f"What is the breakdown of {col}?")
            if cat_cols:
                queries.append(f"Which {cat_cols[0]} has the highest failure rate?")
            break

    # Numeric distribution + trend
    if num_cols:
        queries.append(f"Show the distribution of {num_cols[0]}")
        if len(num_cols) > 1:
            queries.append(f"What is the average {num_cols[0]} by category?")
        if len(num_cols) >= 2:
            queries.append(f"Is there a relationship between {num_cols[0]} and {num_cols[1]}?")

    # Datetime queries
    if has_datetime:
        queries.append("Show volume trends over time")
        queries.append("What are the peak activity hours?")

    # Outlier / anomaly
    for col in num_cols[:2]:
        queries.append(f"Are there outliers in {col}?")

    # Segment comparison
    if cat_cols and num_cols:
        queries.append(f"Compare {num_cols[0]} across {cat_cols[0]} segments")

    return queries[:6]   # cap at 6