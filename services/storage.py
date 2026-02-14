"""Supabase Storage helpers for file upload/download."""
from db.client import supabase

BUCKET_NAME = "datasets"

def upload_file(session_id: str, filename: str, file_bytes: bytes) -> str:
    """Upload file to Supabase Storage.
    
    Args:
        session_id: Session UUID
        filename: Name of file (e.g., 'raw.csv' or 'raw.parquet')
        file_bytes: File content as bytes
        
    Returns:
        Full path in storage: datasets/{session_id}/{filename}
    """
    path = f"{session_id}/{filename}"
    
    supabase.storage.from_(BUCKET_NAME).upload(
        path=path,
        file=file_bytes,
        file_options={"content-type": "application/octet-stream"}
    )
    
    return f"{BUCKET_NAME}/{path}"

def download_file(session_id: str, filename: str) -> bytes:
    """Download file from Supabase Storage.
    
    Args:
        session_id: Session UUID
        filename: Name of file (e.g., 'raw.parquet')
        
    Returns:
        File content as bytes
    """
    path = f"{session_id}/{filename}"
    
    response = supabase.storage.from_(BUCKET_NAME).download(path)
    
    return response
