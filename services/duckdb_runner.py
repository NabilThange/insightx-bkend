"""DuckDB query runner with Supabase Storage."""
import tempfile
import os
import duckdb
import pandas as pd
from services.storage import download_file

def run_query(session_id: str, sql: str) -> pd.DataFrame:
    """Run DuckDB SQL query against session's Parquet file.
    
    Args:
        session_id: Session UUID
        sql: SQL query (can use 'transactions' as table name placeholder)
        
    Returns:
        Query result as pandas DataFrame
    """
    file_bytes = download_file(session_id, "raw.parquet")
    
    tmp = tempfile.NamedTemporaryFile(suffix=".parquet", delete=False)
    tmp.write(file_bytes)
    tmp.close()
    
    try:
        conn = duckdb.connect()
        result_df = conn.execute(sql.replace("FROM transactions", f"FROM '{tmp.name}'")).df()
        conn.close()
        return result_df
    finally:
        os.unlink(tmp.name)  # clean up after we're done
