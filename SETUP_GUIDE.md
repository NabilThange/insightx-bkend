# InsightX Backend - Complete Setup Guide

## Prerequisites

- Python 3.9 or higher
- Supabase account with project created
- Git (optional)

## Step-by-Step Setup

### 1. Get Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to: **Settings** → **API**
3. Copy these values:
   - **Project URL** (e.g., `https://xvtqbvavwbowyyoevolo.supabase.co`)
   - **service_role key** (NOT the anon key - this is important!)

### 2. Create .env File

```bash
cd backend
copy .env.example .env    # Windows
# or
cp .env.example .env      # Mac/Linux
```

Edit `.env` and paste your credentials:

```
SUPABASE_URL=https://xvtqbvavwbowyyoevolo.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

### 3. Install Dependencies

**Option A: Using run script (recommended)**

Windows:
```bash
run.bat
```

Mac/Linux:
```bash
chmod +x run.sh
./run.sh
```

**Option B: Manual setup**

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

### 4. Verify Server is Running

Open browser to: `http://localhost:8000`

You should see:
```json
{
  "status": "ok",
  "service": "InsightX Backend",
  "version": "1.0.0"
}
```

### 5. Test API Endpoints

Open: `http://localhost:8000/docs`

This is the interactive API documentation (Swagger UI). You can test all endpoints here.

## Testing the Complete Flow

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "storage": "connected"
}
```

### Test 2: Upload CSV

Using the Swagger UI at `/docs`:

1. Click on **POST /api/upload**
2. Click **Try it out**
3. Click **Choose File** and select `sample_data.csv`
4. Click **Execute**

Expected response:
```json
{
  "session_id": "abc-123-def-456",
  "filename": "sample_data.csv",
  "row_count": 15,
  "status": "exploring"
}
```

**Save the `session_id` - you'll need it for next steps!**

### Test 3: Run Exploration

1. Click on **POST /api/explore/{session_id}**
2. Click **Try it out**
3. Paste your `session_id`
4. Click **Execute**

Expected response includes:
```json
{
  "session_id": "abc-123-def-456",
  "status": "ready",
  "data_dna": {
    "columns": [...],
    "baselines": {...},
    "detected_patterns": [...],
    "suggested_queries": [...]
  }
}
```

### Test 4: Get Session

1. Click on **GET /api/session/{session_id}**
2. Click **Try it out**
3. Paste your `session_id`
4. Click **Execute**

You should see the full session with Data DNA.

### Test 5: Create Chat

1. Click on **POST /api/chats**
2. Click **Try it out**
3. Use this JSON:
```json
{
  "session_id": "your-session-id-here",
  "title": "Test Chat"
}
```
4. Click **Execute**

**Save the `chat_id` from the response!**

### Test 6: Send Message

1. Click on **POST /api/messages**
2. Click **Try it out**
3. Use this JSON:
```json
{
  "chat_id": "your-chat-id-here",
  "role": "user",
  "content": "What are the key insights?"
}
```
4. Click **Execute**

### Test 7: Chat Stream (Stubbed)

1. Click on **POST /api/chat/stream**
2. Click **Try it out**
3. Use this JSON:
```json
{
  "chat_id": "your-chat-id-here",
  "session_id": "your-session-id-here",
  "message": "Show me transaction trends",
  "history": []
}
```
4. Click **Execute**

You should get a hardcoded response (AI not integrated yet).

## Verify in Supabase

1. Go to Supabase Dashboard → **Table Editor**
2. Check these tables:
   - `sessions` - should have your uploaded session
   - `chats` - should have your test chat
   - `messages` - should have your messages

3. Go to **Storage** → `datasets` bucket
   - You should see a folder with your `session_id`
   - Inside: `raw.csv` and `raw.parquet`

## Common Issues

### Issue: "SUPABASE_URL must be set"

**Solution:** Make sure `.env` file exists and has correct values.

### Issue: "Failed to upload to storage"

**Solution:** 
1. Check that `datasets` bucket exists in Supabase Storage
2. Make sure bucket is set to **private** (not public)
3. Verify you're using the **service_role** key, not anon key

### Issue: "Module not found"

**Solution:** Make sure virtual environment is activated and dependencies installed:
```bash
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### Issue: Port 8000 already in use

**Solution:** Kill the existing process or use a different port:
```bash
uvicorn main:app --reload --port 8001
```

## Next Steps

Once all tests pass:

1. ✅ All 9 endpoints working
2. ✅ Files uploading to Supabase Storage
3. ✅ Data DNA generating correctly
4. ✅ Chats and messages saving to DB

You're ready to:
- Connect the frontend to these endpoints
- Deploy to Railway
- Add AI/LLM integration
- Implement real streaming

## Project Structure Reference

```
backend/
├── main.py                 # FastAPI app
├── requirements.txt        # Dependencies
├── .env                    # Your credentials (create this!)
├── .env.example           # Template
├── run.bat / run.sh       # Quick start scripts
├── sample_data.csv        # Test data
│
├── db/
│   └── client.py          # Supabase client
│
├── models/
│   └── schemas.py         # Pydantic models
│
├── routes/
│   ├── upload.py          # File upload
│   ├── explore.py         # Data exploration
│   ├── sessions.py        # Session management
│   ├── chats.py           # Chat/message CRUD
│   └── chat.py            # Chat streaming (stub)
│
└── services/
    ├── storage.py         # Supabase Storage helpers
    ├── explorer.py        # Data DNA generation
    └── duckdb_runner.py   # DuckDB queries
```

## Support

If you encounter issues:
1. Check the terminal for error messages
2. Verify `.env` file has correct credentials
3. Check Supabase dashboard for data
4. Review logs in terminal where server is running
