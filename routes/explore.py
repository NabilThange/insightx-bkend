"""Data exploration endpoint."""
import os
from fastapi import APIRouter, HTTPException
from db.client import supabase
from services.explorer import run_exploration
from services.storage import ensure_parquet_local, download_file

router = APIRouter()

@router.post("/explore/{session_id}")
async def explore_session(session_id: str):
    """Run data exploration on uploaded Parquet file.
    
    Steps:
    1. Ensure Parquet exists locally (cache-aside pattern)
    2. If not available locally, download from Supabase Storage
    3. Run exploration to generate Data DNA
    4. Update session in DB with data_dna and status='ready'
    """
    try:
        # Try to get parquet from local disk first
        parquet_path = await ensure_parquet_local(session_id)
        
        # If local file doesn't exist, download from Supabase and use temp file
        if not os.path.exists(parquet_path):
            print(f"Local file not available, downloading from Supabase Storage...")
            try:
                file_bytes = download_file(session_id, "raw.parquet")
                # Use temp file for exploration
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
                    tmp.write(file_bytes)
                    parquet_path = tmp.name
                print(f"Using temp file: {parquet_path}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Could not download Parquet: {str(e)}")
        
        # Run full exploration — returns clean dict
        data_dna = run_exploration(parquet_path)
        
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
