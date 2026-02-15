"""Safe SQL execution with DuckDB."""
import re
import tempfile
import os
import duckdb
import pandas as pd
from typing import Optional, Tuple
from services.storage import download_file


# Dangerous SQL keywords that should not be allowed
DANGEROUS_KEYWORDS = {
    "INSTALL",
    "LOAD",
    "COPY",
    "EXPORT",
    "ATTACH",
    "PRAGMA",
    "CREATE",
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "CALL",
    "ALTER",
}


def validate_sql(sql: str) -> Tuple[bool, Optional[str]]:
    """Validate SQL query for safety.

    Args:
        sql: SQL query string

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for dangerous keywords
    sql_upper = sql.upper()
    for keyword in DANGEROUS_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_upper):
            return False, f"Dangerous keyword '{keyword}' not allowed"

    # Check that it's a SELECT statement
    if not re.search(r"^\s*SELECT\b", sql_upper):
        return False, "Only SELECT statements are allowed"

    return True, None


def run_sql(
    session_id: str, sql: str, limit_rows: int = 500
) -> Tuple[pd.DataFrame, str]:
    """Execute a safe SQL query against session's Parquet file.

    Args:
        session_id: Session UUID
        sql: SQL query (can use 'transactions' as table name)
        limit_rows: Maximum rows to return

    Returns:
        Tuple of (result_dataframe, execution_summary)

    Raises:
        ValueError: If SQL is invalid
        RuntimeError: If query execution fails
    """
    # Validate SQL
    is_valid, error_msg = validate_sql(sql)
    if not is_valid:
        raise ValueError(f"Invalid SQL: {error_msg}")

    # Download parquet from Supabase Storage
    try:
        file_bytes = download_file(session_id, "raw.parquet")
    except Exception as e:
        raise RuntimeError(f"Failed to download parquet file: {str(e)}")

    # Write to temp file
    tmp = tempfile.NamedTemporaryFile(suffix=".parquet", delete=False)
    tmp.write(file_bytes)
    tmp.close()

    try:
        # Replace 'transactions' placeholder with actual file path
        modified_sql = sql.replace("FROM transactions", f"FROM '{tmp.name}'")
        modified_sql = modified_sql.replace("from transactions", f"from '{tmp.name}'")

        # Execute query
        conn = duckdb.connect()
        result_df = conn.execute(modified_sql).df()
        conn.close()

        # Apply row limit
        if len(result_df) > limit_rows:
            result_df = result_df.head(limit_rows)

        # Generate summary
        summary = f"Query returned {len(result_df)} rows, {len(result_df.columns)} columns"

        return result_df, summary

    except Exception as e:
        raise RuntimeError(f"Query execution failed: {str(e)}")
    finally:
        os.unlink(tmp.name)


def ensure_parquet_local(session_id: str, base_path: str = "/data") -> str:
    """Ensure parquet file exists locally, downloading if necessary.

    Args:
        session_id: Session UUID
        base_path: Base path for local storage

    Returns:
        Path to local parquet file
    """
    local_path = f"{base_path}/{session_id}/raw.parquet"

    # If file exists locally, return it
    if os.path.exists(local_path):
        return local_path

    # Otherwise download from Supabase Storage
    try:
        file_bytes = download_file(session_id, "raw.parquet")
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(file_bytes)
        return local_path
    except Exception as e:
        raise RuntimeError(f"Failed to ensure local parquet: {str(e)}")
