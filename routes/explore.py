"""Data exploration endpoint."""
import os
from fastapi import APIRouter, HTTPException
from db.client import supabase
from services.explorer import run_exploration
from services.duckdb_runner import ensure_parquet

router = APIRouter()

@router.post("/explore/{session_id}")
async def explore_session(session_id: str):
    """Run data exploration on uploaded Parquet file.
    
    Steps:
    1. Ensure Parquet exists locally
    2. Run exploration to generate Data DNA
    3. Update session in DB with data_dna and status='ready'
    """
    try:
        # Ensure parquet exists locally
        parquet_path = ensure_parquet(session_id)
        
        # Run exploration
        data_dna = run_exploration(parquet_path)
        
        # Update session in Supabase
        result = supabase.table("sessions").update({
            "data_dna": data_dna,
            "status": "ready"
        }).eq("id", session_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "status": "ready",
            "data_dna": data_dna
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exploration failed: {str(e)}")
