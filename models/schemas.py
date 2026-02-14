"""Pydantic models for request/response validation."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class UploadResponse(BaseModel):
    session_id: str
    filename: str
    row_count: int
    status: str

class SessionResponse(BaseModel):
    id: str
    filename: str
    row_count: Optional[int]
    status: str
    data_dna: Optional[Dict[str, Any]]
    parquet_path: Optional[str]
    created_at: str

class ChatCreate(BaseModel):
    session_id: str
    title: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    session_id: str
    title: Optional[str]
    created_at: str

class MessageCreate(BaseModel):
    chat_id: str
    role: str  # "user" or "assistant"
    content: Any  # Can be text or jsonb

class MessageResponse(BaseModel):
    id: str
    chat_id: str
    role: str
    content: Any
    created_at: str

class ChatStreamRequest(BaseModel):
    chat_id: str
    session_id: str
    message: str
    history: List[Dict[str, Any]] = []
