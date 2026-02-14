"""DuckDB query runner with local Parquet caching."""
import os
import duckdb
import pandas as pd
from services.storage import download_file

DATA_DIR = "/data"  # Railway disk cache

def ensure_parquet(session_id: str) -> str:
    """Ensure Parquet file exists locally, download from Supabase if missing.
    
    Args:
        session_id: Session UUID
        
    Returns:
        Local path to Parquet file
    """
    local_dir = os.path.join(DATA_DIR, session_id)
    local_path = os.path.join(local_dir, "raw.parquet")
    
    if not os.path.exists(local_path):
        # Download from Supabase Storage
        print(f"Parquet not found locally, downloading from Supabase Storage...")
        file_bytes = download_file(session_id, "raw.parquet")
        
        # Save to local disk
        os.makedirs(local_dir, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(file_bytes)
        print(f"Parquet cached at {local_path}")
    
    return local_path

def run_query(session_id: str, sql: str) -> pd.DataFrame:
    """Run DuckDB SQL query against session's Parquet file.
    
    Args:
        session_id: Session UUID
        sql: SQL query (can use 'dataset' as table name placeholder)
        
    Returns:
        Query result as pandas DataFrame
    """
    parquet_path = ensure_parquet(session_id)
    
    # Replace placeholder table name with actual parquet path
    sql = sql.replace("dataset", f"'{parquet_path}'")
    sql = sql.replace("FROM dataset", f"FROM '{parquet_path}'")
    
    # Run query
    conn = duckdb.connect()
    result_df = conn.execute(sql).df()
    conn.close()
    
    return result_df
