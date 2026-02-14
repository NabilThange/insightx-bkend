"""Data exploration endpoint."""
from fastapi import APIRouter, HTTPException
from db.client import supabase
from services.explorer import run_exploration
from services.storage import ensure_parquet_local

router = APIRouter()

@router.post("/explore/{session_id}")
async def explore_session(session_id: str):
    """Run data exploration on uploaded Parquet file.
    
    Steps:
    1. Ensure Parquet exists locally (cache-aside pattern)
    2. Run exploration to generate Data DNA
    3. Update session in DB with data_dna and status='ready'
    """
    try:
        # Make sure parquet is on local disk (downloads from Supabase Storage if missing)
        parquet_path = await ensure_parquet_local(session_id)
        
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exploration failed: {str(e)}")
