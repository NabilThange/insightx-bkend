"""File upload endpoint."""
import io
import os
import tempfile
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd

from db.client import supabase
from models.schemas import UploadResponse
from services.storage import upload_file

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV, convert to Parquet, store in Supabase Storage.
    
    Steps:
    1. Read CSV into pandas
    2. Generate session_id
    3. Convert to Parquet
    4. Upload both CSV and Parquet to Supabase Storage
    5. Try to save Parquet to local disk (optional, for caching)
    6. Create session row in DB
    """
    try:
        # Read file
        file_bytes = await file.read()
        
        # Load into pandas
        df = pd.read_csv(io.BytesIO(file_bytes))
        row_count = len(df)
        
        # Generate session ID
        session_id = str(uuid4())
        
        # Convert to Parquet
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_bytes = parquet_buffer.getvalue()
        
        # Upload CSV to Supabase Storage
        upload_file(session_id, "raw.csv", file_bytes)
        
        # Upload Parquet to Supabase Storage
        parquet_path = upload_file(session_id, "raw.parquet", parquet_bytes)
        
        # Try to save Parquet to local disk (Railway cache) - optional
        # If it fails (permission denied), that's OK - we have it in Supabase Storage
        try:
            data_dir = os.getenv("DATA_DIR", "/data")
            local_dir = os.path.join(data_dir, session_id)
            os.makedirs(local_dir, exist_ok=True)
            local_parquet_path = os.path.join(local_dir, "raw.parquet")
            with open(local_parquet_path, "wb") as f:
                f.write(parquet_bytes)
            print(f"✓ Cached Parquet locally at {local_parquet_path}")
        except (PermissionError, OSError) as e:
            print(f"⚠ Could not cache Parquet locally: {e}")
            print(f"  This is OK - will download from Supabase Storage when needed")
        
        # Create session in Supabase DB
        session_data = {
            "id": session_id,
            "filename": file.filename,
            "row_count": row_count,
            "status": "exploring",
            "parquet_path": parquet_path
        }
        
        result = supabase.table("sessions").insert(session_data).execute()
        
        return UploadResponse(
            session_id=session_id,
            filename=file.filename,
            row_count=row_count,
            status="exploring"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
