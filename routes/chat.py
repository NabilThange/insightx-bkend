"""Chat streaming endpoint (stubbed for MVP)."""
import time
from fastapi import APIRouter, HTTPException
from db.client import supabase
from models.schemas import ChatStreamRequest, MessageResponse

router = APIRouter()

@router.post("/chat/stream")
async def chat_stream(request: ChatStreamRequest):
    """Handle chat message and return response.
    
    MVP STUB: No AI yet, just saves messages and returns hardcoded response.
    Real streaming + AI logic comes later.
    """
    try:
        # 1. Save user message
        user_message_data = {
            "chat_id": request.chat_id,
            "role": "user",
            "content": request.message
        }
        
        user_msg_result = supabase.table("messages").insert(user_message_data).execute()
        
        if not user_msg_result.data:
            raise HTTPException(status_code=500, detail="Failed to save user message")
        
        # 2. Fake thinking delay
        time.sleep(1)
        
        # 3. Generate hardcoded assistant response
        assistant_content = {
            "text": f"I received your message: '{request.message}'. This is a placeholder response. AI integration coming soon!",
            "type": "text"
        }
        
        assistant_message_data = {
            "chat_id": request.chat_id,
            "role": "assistant",
            "content": str(assistant_content)  # Convert to string for now since content is text type
        }
        
        assistant_msg_result = supabase.table("messages").insert(assistant_message_data).execute()
        
        if not assistant_msg_result.data:
            raise HTTPException(status_code=500, detail="Failed to save assistant message")
        
        created_message = assistant_msg_result.data[0]
        
        return MessageResponse(
            id=created_message["id"],
            chat_id=created_message["chat_id"],
            role=created_message["role"],
            content=created_message["content"],
            created_at=created_message["created_at"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat stream failed: {str(e)}")
