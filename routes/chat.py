"""Chat streaming endpoint with multi-agent orchestration."""
import json
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from db.client import supabase
from models.schemas import ChatStreamRequest

router = APIRouter()


@router.post("/chat/stream")
async def chat_stream(request: ChatStreamRequest):
    """Handle chat message with multi-agent orchestration and SSE streaming.

    Streams orchestration steps, SQL execution, Python analysis, and final response.
    """
    try:
        # 1. Save user message
        user_message_data = {
            "chat_id": request.chat_id,
            "role": "user",
            "content": request.message,
        }

        user_msg_result = supabase.table("messages").insert(user_message_data).execute()

        if not user_msg_result.data:
            raise HTTPException(status_code=500, detail="Failed to save user message")

        # 2. Check if Bytez API keys are configured
        bytez_key_1 = os.getenv("BYTEZ_API_KEY_1")
        if not bytez_key_1:
            # Fallback: return error event
            async def error_generator():
                yield f"data: {json.dumps({{'type': 'error', 'message': 'Bytez API keys not configured. Please add BYTEZ_API_KEY_1 to .env and restart the server.'}})}\n\n"

            return StreamingResponse(
                error_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                },
            )

        # 3. Get orchestrator and stream response
        try:
            from services.orchestrator import get_orchestrator
            orchestrator = await get_orchestrator()
        except Exception as e:
            async def error_generator():
                yield f"data: {json.dumps({{'type': 'error', 'message': f'Failed to initialize orchestrator: {str(e)}'}})}\n\n"

            return StreamingResponse(
                error_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                },
            )

        async def event_generator():
            """Generate SSE events from orchestrator."""
            try:
                async for event in orchestrator.stream_chat(
                    chat_id=request.chat_id,
                    session_id=request.session_id,
                    message=request.message,
                    history=request.history,
                ):
                    # Format as SSE
                    yield f"data: {json.dumps(event)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({{'type': 'error', 'message': f'Stream error: {str(e)}'}})}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat stream failed: {str(e)}")
