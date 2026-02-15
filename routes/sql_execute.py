"""SQL execution endpoint for agents."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.sql_executor import run_sql

router = APIRouter()


class SQLExecuteRequest(BaseModel):
    session_id: str
    sql: str
    limit: int = 500


@router.post("/sql/execute")
async def execute_sql(request: SQLExecuteRequest):
    """Execute SQL query on session's dataset.
    
    Called by agents via tool_executor.
    """
    try:
        result_df, summary = run_sql(
            session_id=request.session_id,
            sql=request.sql,
            limit_rows=request.limit
        )
        
        return {
            "success": True,
            "data": {
                "rows": len(result_df),
                "columns": list(result_df.columns),
                "records": result_df.to_dict("records"),
            },
            "summary": summary,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SQL execution failed: {str(e)}"
        )
