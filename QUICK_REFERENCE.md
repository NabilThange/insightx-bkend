# InsightX Backend - Quick Reference

## Start Server

```bash
# Windows
run.bat

# Mac/Linux
./run.sh

# Manual
uvicorn main:app --reload
```

Server: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health |
| POST | `/api/upload` | Upload CSV file |
| POST | `/api/explore/{session_id}` | Generate Data DNA |
| GET | `/api/session/{session_id}` | Get session details |
| POST | `/api/chats` | Create new chat |
| GET | `/api/chats/{session_id}` | List all chats |
| POST | `/api/messages` | Create message |
| GET | `/api/messages/{chat_id}` | List messages |
| POST | `/api/chat/stream` | Chat (stubbed) |

## Quick Test Flow

```bash
# 1. Upload
curl -X POST http://localhost:8000/api/upload \
  -F "file=@sample_data.csv"
# Returns: session_id

# 2. Explore
curl -X POST http://localhost:8000/api/explore/{session_id}
# Returns: data_dna

# 3. Get Session
curl http://localhost:8000/api/session/{session_id}
# Returns: full session with data_dna

# 4. Create Chat
curl -X POST http://localhost:8000/api/chats \
  -H "Content-Type: application/json" \
  -d '{"session_id":"xxx","title":"Test"}'
# Returns: chat_id

# 5. Send Message
curl -X POST http://localhost:8000/api/messages \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"xxx","role":"user","content":"Hello"}'
```

## File Locations

### Supabase Storage
```
datasets/
  {session_id}/
    raw.csv        ← Original upload
    raw.parquet    ← Converted for queries
```

### Railway Disk (Local Cache)
```
/data/
  {session_id}/
    raw.parquet    ← DuckDB reads from here
```

## Data Flow

```
1. Upload CSV
   ↓
2. Convert to Parquet
   ↓
3. Upload both to Supabase Storage
   ↓
4. Save Parquet to local disk
   ↓
5. Create session in DB (status: exploring)
   ↓
6. Run exploration
   ↓
7. Generate Data DNA
   ↓
8. Update session (status: ready)
   ↓
9. Frontend polls session
   ↓
10. User chats
    ↓
11. DuckDB queries local Parquet
    ↓
12. Results streamed back
```

## Environment Variables

```bash
SUPABASE_URL=https://xvtqbvavwbowyyoevolo.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload

# Run on different port
uvicorn main:app --reload --port 8001

# Run in production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Debugging

```bash
# Check if server is running
curl http://localhost:8000/health

# View logs
# Check terminal where uvicorn is running

# Test Supabase connection
python -c "from db.client import supabase; print(supabase)"

# Check local Parquet files
ls /data/  # Mac/Linux
dir C:\data\  # Windows
```

## Status Codes

- `200` - Success
- `404` - Not found (session/chat/message)
- `500` - Server error (check logs)

## Next Steps After Setup

1. ✅ Test all endpoints in `/docs`
2. ✅ Verify files in Supabase Storage
3. ✅ Check data in Supabase tables
4. 🔄 Connect frontend
5. 🔄 Deploy to Railway
6. 🔄 Add AI integration
