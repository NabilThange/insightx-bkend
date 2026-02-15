# Bytez Implementation Quick Start

## 1. Setup Environment

Add to `backend/.env`:

```bash
# Bytez API Keys (get from https://bytez.com)
BYTEZ_API_KEY_1=your_first_key_here
BYTEZ_API_KEY_2=your_second_key_here

# Keep existing Supabase config
SUPABASE_URL=https://xvtqbvavwbowyyoevolo.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 2. Verify Installation

All required packages are already in `requirements.txt`:
- `httpx` — for Bytez API calls
- `pandas`, `numpy`, `scipy` — for analysis
- `duckdb` — for SQL execution
- `fastapi`, `uvicorn` — for server

## 3. Test Components

### Test Key Manager
```bash
cd backend
python -c "
from services.key_manager import get_key_manager
km = get_key_manager()
print(f'✓ Keys loaded: {len(km.keys)}')
print(f'✓ Current index: {km.current_key_index}')
"
```

### Test Bytez Client
```bash
python -c "
import asyncio
from services.bytez_client import get_bytez_client

async def test():
    client = await get_bytez_client()
    response = await client.chat_completions(
        model='gpt-4-turbo',
        messages=[{'role': 'user', 'content': 'Say hello'}],
        temperature=0.7,
        max_tokens=100
    )
    print('✓ Bytez API working')
    print(f'Response: {response[\"choices\"][0][\"message\"][\"content\"]}')

asyncio.run(test())
"
```

### Test SQL Executor
```bash
python -c "
from services.sql_executor import validate_sql

# Test validation
is_valid, error = validate_sql('SELECT * FROM transactions')
print(f'✓ SQL validation: {is_valid}')

# Test dangerous keyword blocking
is_valid, error = validate_sql('DROP TABLE transactions')
print(f'✓ Dangerous SQL blocked: {not is_valid}')
"
```

### Test Python Executor
```bash
python -c "
from services.python_executor import validate_python_code

# Test safe code
is_valid, error = validate_python_code('import pandas as pd')
print(f'✓ Safe code allowed: {is_valid}')

# Test dangerous code
is_valid, error = validate_python_code('import os; os.system(\"rm -rf /\")')
print(f'✓ Dangerous code blocked: {not is_valid}')
"
```

## 4. Start Server

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 5. Test Chat Endpoint

### Using curl (streaming):
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "test-chat-123",
    "session_id": "test-session-123",
    "message": "What is the average transaction amount?",
    "history": []
  }'
```

### Using Python:
```python
import asyncio
import json
from services.orchestrator import get_orchestrator

async def test_chat():
    orchestrator = await get_orchestrator()
    
    async for event in orchestrator.stream_chat(
        chat_id="test-chat",
        session_id="test-session",
        message="Analyze the data",
        history=[]
    ):
        print(f"Event: {event['type']}")
        if event['type'] == 'error':
            print(f"Error: {event['message']}")
        elif event['type'] == 'final_response':
            print(f"Response: {event['data']}")

asyncio.run(test_chat())
```

## 6. Monitor Key Rotation

The KeyManager automatically rotates keys on:
- **401/403** — Unauthorized (key invalid)
- **429** — Rate limited
- **5xx** — Server errors

Check rotation events:
```python
from services.key_manager import get_key_manager

km = get_key_manager()
event = km.get_and_clear_last_event()
if event:
    print(f"Rotation event: {event}")
```

## 7. Frontend Integration

Update `insightx-app/lib/api/backend.ts`:

```typescript
export async function* chatStream(
  chatId: string,
  sessionId: string,
  message: string,
  history: any[] = []
): AsyncGenerator<any> {
  const response = await fetch(`${API_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      session_id: sessionId,
      message,
      history,
    }),
  });

  if (!response.ok) throw new Error(`API error: ${response.status}`);

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const event = JSON.parse(line.slice(6));
          yield event;
        } catch (e) {
          console.error("Parse error:", e);
        }
      }
    }
  }
}
```

Update `insightx-app/components/workspace/ChatPanel.tsx`:

```typescript
async function handleSendMessage(text: string) {
  // Add user message
  const userMsg = { role: "user", content: text };
  setMessages((prev) => [...prev, userMsg]);

  // Stream assistant response
  let assistantContent = "";

  try {
    for await (const event of chatStream(chatId, sessionId, text, messages)) {
      if (event.type === "status") {
        setThinkingSteps((prev) => [...prev, event.message]);
      } else if (event.type === "orchestrator_result") {
        console.log("Classification:", event.data.classification);
      } else if (event.type === "sql_result") {
        console.log("SQL executed:", event.data.query);
      } else if (event.type === "python_result") {
        console.log("Python analysis:", event.data.results);
      } else if (event.type === "final_response") {
        assistantContent = event.data.text;
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: assistantContent },
        ]);
      } else if (event.type === "error") {
        console.error("Stream error:", event.message);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `Error: ${event.message}` },
        ]);
      }
    }
  } catch (error) {
    console.error("Chat failed:", error);
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: `Failed: ${error}` },
    ]);
  }
}
```

## 8. Deployment to Railway

1. Push code to GitHub
2. Connect Railway to repo
3. Add environment variables in Railway dashboard:
   - `BYTEZ_API_KEY_1`
   - `BYTEZ_API_KEY_2`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
4. Deploy

## 9. Troubleshooting

### "No Bytez API keys found"
```bash
# Check .env file
cat backend/.env | grep BYTEZ

# Verify keys are set
echo $BYTEZ_API_KEY_1
```

### "Connection refused"
```bash
# Make sure server is running
curl http://localhost:8000/health

# Check port 8000 is available
lsof -i :8000
```

### "SQL execution failed"
- Verify session_id exists in Supabase
- Check parquet file was uploaded
- Test with simple query: `SELECT COUNT(*) FROM transactions`

### "Python execution timed out"
- Reduce timeout_s parameter
- Simplify Python code
- Check for infinite loops

## 10. Next Steps

1. ✅ Setup environment variables
2. ✅ Test each component
3. ✅ Start server and test chat endpoint
4. ✅ Update frontend to consume SSE
5. ✅ Deploy to Railway
6. 📋 Monitor logs for errors
7. 📋 Add caching for performance
8. 📋 Implement validator agent

## Files Created

- `backend/services/key_manager.py` — API key rotation
- `backend/services/bytez_client.py` — Bytez API wrapper
- `backend/services/agent_config.py` — Agent registry
- `backend/services/sql_executor.py` — Safe SQL execution
- `backend/services/python_executor.py` — Safe Python execution
- `backend/services/orchestrator.py` — Multi-agent orchestration
- `backend/routes/chat.py` — Updated chat endpoint (SSE streaming)
- `backend/BYTEZ_IMPLEMENTATION_GUIDE.md` — Full documentation
- `backend/BYTEZ_QUICK_START.md` — This file

## Support

For issues:
1. Check logs: `docker logs <container_id>`
2. Test components individually
3. Verify Bytez API keys are valid
4. Check Supabase connection
5. Review error messages in SSE stream
