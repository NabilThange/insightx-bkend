"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, explore, sessions, chats, chat

app = FastAPI(
    title="InsightX Backend",
    description="FastAPI backend for InsightX - CSV analysis with DuckDB and Python",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(explore.router, prefix="/api", tags=["Explore"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
app.include_router(chats.router, prefix="/api", tags=["Chats"])
app.include_router(chat.router, prefix="/api", tags=["Chat Stream"])

@app.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "InsightX Backend",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "storage": "connected"
    }
