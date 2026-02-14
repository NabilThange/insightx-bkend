"""Session management endpoints."""
from fastapi import APIRouter, HTTPException
from db.client import supabase
from models.schemas import SessionResponse

router = APIRouter()

@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details including Data DNA."""
    try:
        result = supabase.table("sessions").select("*").eq("id", session_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = result.data[0]
        
        return SessionResponse(
            id=session["id"],
            filename=session["filename"],
            row_count=session.get("row_count"),
            status=session["status"],
            data_dna=session.get("data_dna"),
            parquet_path=session.get("parquet_path"),
            created_at=session["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch session: {str(e)}")
