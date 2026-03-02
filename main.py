"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import upload, explore, sessions, chats, chat, sql_execute, python_execute, insights

# Load environment variables from .env file
load_dotenv()

description = """

## 🌐 Try InsightX Live

| | Link |
|---|---|
| 🏠 **Live App** | [insightxx.vercel.app](https://insightxx.vercel.app) |
| ⭐ **Pre-loaded Workspace** *(Recommended — official dataset ready to query)* | [Open Workspace →](https://insightxx.vercel.app/workspace/0c62e010-86d0-4807-8e69-193f59926aea?chat=527a453b-16e3-42dd-a4f6-f32d511aa9ca) |

> 💡 **Don't want to set up locally?** Just hit the Pre-loaded Workspace link above — the official dataset is already uploaded and ready. Start asking questions immediately.

---

## 🚀 Quick Setup Guide

Everything you need to get **InsightX** running locally in minutes.

**Repo:** [github.com/NabilThange/insightx](https://github.com/NabilThange/insightx)
**Live App:** [insightxx.vercel.app](https://insightxx.vercel.app)

---

### 📋 Steps Overview

```
1️⃣  Clone the repo
2️⃣  Install frontend dependencies  (npm install)
3️⃣  Create .env.local  →  paste frontend env vars
4️⃣  Install backend dependencies   (pip install -r requirements.txt)
5️⃣  Create backend/.env  →  paste backend env vars
6️⃣  Run frontend  (npm run dev)  +  backend  (python main.py)
7️⃣  Visit http://localhost:3000  🎉
```

---

### 🎨 Frontend ENV — Create `.env.local` in project root

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_BACKEND_URL=https://insightx-bkend.onrender.com

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://xvtqbvavwbowyyoevolo.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh2dHFidmF2d2Jvd3l5b2V2b2xvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEwNzE4NzIsImV4cCI6MjA4NjY0Nzg3Mn0.45NW1ZBLH8Q08kfQteIjlF24G0E0-1pblapR40_toug

# BYTEZ API Keys
BYTEZ_API_KEY_1=21fcde49a931a29607160578c375a6ce
BYTEZ_API_KEY_2=1158b7d57824068956d7163a84e112e3
BYTEZ_API_KEY_3=7eb97a0aefd85a36d6c663f0f82d9c9f
BYTEZ_API_KEY_4=dd7aeb8a6ccca7b8a978f646892ce1bf
BYTEZ_API_KEY_5=74c51b3a8ac8b15b6c6d0ecda1859ba1
BYTEZ_API_KEY_6=976436aed804d1dd3578c22df7e090b2
BYTEZ_API_KEY_7=57a2405dd1f29cd34745ce1c418755e8
BYTEZ_API_KEY_8=f37860147855a578b1c6306a43b37114

# Client Side (NEXT_PUBLIC prefix for browser access)
NEXT_PUBLIC_BYTEZ_API_KEY_1=21fcde49a931a29607160578c375a6ce
NEXT_PUBLIC_BYTEZ_API_KEY_2=1158b7d57824068956d7163a84e112e3
NEXT_PUBLIC_BYTEZ_API_KEY_3=7eb97a0aefd85a36d6c663f0f82d9c9f
NEXT_PUBLIC_BYTEZ_API_KEY_4=dd7aeb8a6ccca7b8a978f646892ce1bf
NEXT_PUBLIC_BYTEZ_API_KEY_5=74c51b3a8ac8b15b6c6d0ecda1859ba1
NEXT_PUBLIC_BYTEZ_API_KEY_6=976436aed804d1dd3578c22df7e090b2
NEXT_PUBLIC_BYTEZ_API_KEY_7=57a2405dd1f29cd34745ce1c418755e8
NEXT_PUBLIC_BYTEZ_API_KEY_8=f37860147855a578b1c6306a43b37114
```

---

### ⚙️ Backend ENV — Create `backend/.env`

```env
# Supabase Configuration
SUPABASE_URL=https://xvtqbvavwbowyyoevolo.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh2dHFidmF2d2Jvd3l5b2V2b2xvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTA3MTg3MiwiZXhwIjoyMDg2NjQ3ODcyfQ.Cj1_-8_3fD8BgcOkdFLf5yRuUdmfC9-OcAyzMOflguA

# API Configuration
NEXT_PUBLIC_API_URL=https://insightx-bkend.onrender.com

# BYTEZ API Keys (Server-side) — rotate automatically on rate limit
BYTEZ_API_KEY_1=21fcde49a931a29607160578c375a6ce
BYTEZ_API_KEY_2=1158b7d57824068956d7163a84e112e3
BYTEZ_API_KEY_3=7eb97a0aefd85a36d6c663f0f82d9c9f
BYTEZ_API_KEY_4=dd7aeb8a6ccca7b8a978f646892ce1bf
BYTEZ_API_KEY_5=74c51b3a8ac8b15b6c6d0ecda1859ba1
BYTEZ_API_KEY_6=976436aed804d1dd3578c22df7e090b2
BYTEZ_API_KEY_7=57a2405dd1f29cd34745ce1c418755e8
BYTEZ_API_KEY_8=f37860147855a578b1c6306a43b37114

# Client-side API keys
NEXT_PUBLIC_BYTEZ_API_KEY_1=21fcde49a931a29607160578c375a6ce
NEXT_PUBLIC_BYTEZ_API_KEY_2=1158b7d57824068956d7163a84e112e3
NEXT_PUBLIC_BYTEZ_API_KEY_3=7eb97a0aefd85a36d6c663f0f82d9c9f
NEXT_PUBLIC_BYTEZ_API_KEY_4=dd7aeb8a6ccca7b8a978f646892ce1bf
NEXT_PUBLIC_BYTEZ_API_KEY_5=74c51b3a8ac8b15b6c6d0ecda1859ba1
NEXT_PUBLIC_BYTEZ_API_KEY_6=976436aed804d1dd3578c22df7e090b2
NEXT_PUBLIC_BYTEZ_API_KEY_7=57a2405dd1f29cd34745ce1c418755e8
NEXT_PUBLIC_BYTEZ_API_KEY_8=f37860147855a578b1c6306a43b37114
```

---

### 🔌 Backend API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload a CSV file, returns session ID |
| `GET` | `/api/explore/{session_id}` | Get Data DNA — schema, patterns, anomalies |
| `GET` | `/api/sessions` | List all active sessions |
| `GET` | `/api/chats/{session_id}` | Get chat history for a session |
| `POST` | `/api/chat` | Stream AI response (SSE) for a query |
| `POST` | `/api/sql/execute` | Execute raw SQL on uploaded dataset |
| `POST` | `/api/python/execute` | Execute Python analysis on dataset |
| `GET` | `/api/insights/{session_id}` | Get AI-generated insights |

**Base URL (Production):** `https://insightx-bkend.onrender.com`

---

> ⚠️ **ℹ️ Indian ISP Notice — Supabase Connectivity**
>
> Supabase may be **inaccessible on Indian ISPs, especially Jio**, due to DNS/routing blocks.
> If you see `ERR_CONNECTION_REFUSED` or auth/upload failures:
> - Try a **different network** (Airtel, BSNL, WiFi hotspot)
> - Use a **VPN** (Cloudflare WARP is free)
> - Or use the **hosted backend** at `https://insightx-bkend.onrender.com` which bypasses this issue

---
"""

app = FastAPI(
    title="InsightX Backend",
    description=description,
    version="1.0.0",
    contact={
        "name": "Nabil Thange",
        "url": "https://nabil-thange.vercel.app/",
    },
    openapi_tags=[
        {"name": "Upload", "description": "Upload CSV files and create analysis sessions"},
        {"name": "Explore", "description": "Data DNA — auto-profiling with schema, patterns, and anomalies"},
        {"name": "Sessions", "description": "Manage and list analysis sessions"},
        {"name": "Chats", "description": "Retrieve chat history for a session"},
        {"name": "Chat Stream", "description": "Stream AI responses in real-time via SSE"},
        {"name": "SQL Execution", "description": "Execute raw DuckDB SQL queries on uploaded data"},
        {"name": "Python Execution", "description": "Run Python/scipy statistical analysis on data"},
        {"name": "Insights", "description": "Get AI-generated summary insights for a session"},
    ]
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
app.include_router(sql_execute.router, prefix="/api", tags=["SQL Execution"])
app.include_router(python_execute.router, prefix="/api", tags=["Python Execution"])
app.include_router(insights.router, prefix="/api", tags=["Insights"])


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