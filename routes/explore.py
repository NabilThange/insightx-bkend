"""Data exploration endpoint."""
import tempfile
import os
from fastapi import APIRouter, HTTPException
from db.client import supabase
from services.explorer import run_exploration
from services.storage import download_file

router = APIRouter()

@router.post("/explore/{session_id}")
async def explore_session(session_id: str):
    """Run data exploration on uploaded Parquet file.
    
    Steps:
    1. Download Parquet from Supabase Storage
    2. Write to temp file (delete=False so it persists)
    3. Run exploration to generate Data DNA
    4. Clean up temp file
    5. Update session in DB with data_dna and status='ready'
    """
    try:
        file_bytes = download_file(session_id, "raw.parquet")
        
        tmp = tempfile.NamedTemporaryFile(suffix=".parquet", delete=False)
        tmp.write(file_bytes)
        tmp.close()
        
        try:
            data_dna = run_exploration(tmp.name)
        finally:
            os.unlink(tmp.name)  # clean up after we're done
        
        # Save to Supabase sessions table
        result = supabase.table("sessions").update({
            "data_dna": data_dna,
            "status": "ready"
        }).eq("id", session_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "status": "ready",
            "data_dna": data_dna
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Exploration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Exploration failed: {str(e)}")
