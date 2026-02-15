"""Insights management endpoint for agents."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from db.client import supabase

router = APIRouter()


class InsightRequest(BaseModel):
    insight: Dict[str, Any]


@router.post("/session/{session_id}/insights")
async def add_insight(session_id: str, request: InsightRequest):
    """Add new insight to session's accumulated_insights.
    
    Called by agents via tool_executor when write_context tool is used.
    """
    try:
        # Get current session
        session_result = supabase.table("sessions").select("data_dna").eq("id", session_id).execute()
        
        if not session_result.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_result.data[0]
        data_dna = session.get("data_dna") or {}
        
        # Add insight to accumulated_insights
        if "accumulated_insights" not in data_dna:
            data_dna["accumulated_insights"] = []
        
        data_dna["accumulated_insights"].append(request.insight)
        
        # Update session
        update_result = supabase.table("sessions").update({
            "data_dna": data_dna
        }).eq("id", session_id).execute()
        
        if not update_result.data:
            raise HTTPException(status_code=500, detail="Failed to update session")
        
        return {
            "success": True,
            "message": "Insight added successfully",
            "total_insights": len(data_dna["accumulated_insights"])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add insight: {str(e)}"
        )
