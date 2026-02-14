"""Chat and message management endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List
from db.client import supabase
from models.schemas import (
    ChatCreate, ChatResponse,
    MessageCreate, MessageResponse
)

router = APIRouter()

@router.post("/chats", response_model=ChatResponse)
async def create_chat(chat: ChatCreate):
    """Create a new chat for a session."""
    try:
        chat_data = {
            "session_id": chat.session_id,
            "title": chat.title or "New Chat"
        }
        
        result = supabase.table("chats").insert(chat_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create chat")
        
        created_chat = result.data[0]
        
        return ChatResponse(
            id=created_chat["id"],
            session_id=created_chat["session_id"],
            title=created_chat.get("title"),
            created_at=created_chat["created_at"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat: {str(e)}")

@router.get("/chats/{session_id}", response_model=List[ChatResponse])
async def get_chats(session_id: str):
    """Get all chats for a session, ordered by created_at desc."""
    try:
        result = supabase.table("chats")\
            .select("*")\
            .eq("session_id", session_id)\
            .order("created_at", desc=True)\
            .execute()
        
        chats = [
            ChatResponse(
                id=chat["id"],
                session_id=chat["session_id"],
                title=chat.get("title"),
                created_at=chat["created_at"]
            )
            for chat in result.data
        ]
        
        return chats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chats: {str(e)}")

@router.post("/messages", response_model=MessageResponse)
async def create_message(message: MessageCreate):
    """Create a new message in a chat."""
    try:
        message_data = {
            "chat_id": message.chat_id,
            "role": message.role,
            "content": message.content
        }
        
        result = supabase.table("messages").insert(message_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create message")
        
        created_message = result.data[0]
        
        return MessageResponse(
            id=created_message["id"],
            chat_id=created_message["chat_id"],
            role=created_message["role"],
            content=created_message["content"],
            created_at=created_message["created_at"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create message: {str(e)}")

@router.get("/messages/{chat_id}", response_model=List[MessageResponse])
async def get_messages(chat_id: str):
    """Get all messages for a chat, ordered by created_at asc."""
    try:
        result = supabase.table("messages")\
            .select("*")\
            .eq("chat_id", chat_id)\
            .order("created_at", desc=False)\
            .execute()
        
        messages = [
            MessageResponse(
                id=msg["id"],
                chat_id=msg["chat_id"],
                role=msg["role"],
                content=msg["content"],
                created_at=msg["created_at"]
            )
            for msg in result.data
        ]
        
        return messages
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")
