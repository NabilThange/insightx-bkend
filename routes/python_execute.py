"""Python execution endpoint for agents."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.python_executor import run_python, create_safe_python_wrapper
import pandas as pd

router = APIRouter()


class PythonExecuteRequest(BaseModel):
    session_id: str
    code: str
    timeout: int = 10


@router.post("/python/execute")
async def execute_python(request: PythonExecuteRequest):
    """Execute Python code for statistical analysis.
    
    Called by agents via tool_executor.
    Note: result_df is not provided here - Python code should work standalone
    or SQL results should be embedded in the code by the agent.
    """
    try:
        # Wrap code for safe execution
        wrapped_code = create_safe_python_wrapper(request.code)
        
        # Execute (passing empty dataframe as result_df)
        result, summary = run_python(
            code=wrapped_code,
            df=pd.DataFrame(),  # Empty df - agent should include data in code
            timeout_s=request.timeout
        )
        
        return {
            "success": True,
            "data": result,
            "summary": summary,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Python execution failed: {str(e)}"
        )
