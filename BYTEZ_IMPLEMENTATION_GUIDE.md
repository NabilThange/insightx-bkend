# Bytez AI Agent Implementation Guide

## Overview

This document describes the complete Bytez-powered multi-agent orchestration system for InsightX. The system implements:

1. **Key Manager** — Automatic API key rotation with health tracking
2. **Bytez Client** — OpenAI-compatible wrapper with retry logic
3. **Agent Config** — Centralized system prompts and agent registry
4. **SQL Executor** — Safe DuckDB query execution with validation
5. **Python Executor** — Safe Python analytics with AST validation
6. **Orchestrator** — Multi-agent workflow with streaming

## Architecture

```
User Message
    ↓
Chat Route (/api/chat/stream)
    ↓
Orchestrator (async generator)
    ├─ Load Data DNA from Supabase
    ├─ Run Orchestrator Agent (classify query)
    ├─ Run SQL Agent (if needed)
    │   └─ Execute SQL via DuckDB
    ├─ Run Python Agent (if needed)
    │   └─ Execute Python safely
    ├─ Run Composer Agent (synthesize response)
    └─ Save to Supabase + Update accumulated_insights
    ↓
SSE Stream to Frontend
    ├─ status events (routing, execution stages)
    ├─ orchestrator_result (classification)
    ├─ sql_result (query + data)
    ├─ python_result (analysis + code)
    ├─ final_response (composed answer)
    └─ error events (if any)
```

## Components

### 1. Key Manager (`backend/services/key_manager.py`)

Manages multiple Bytez API keys with automatic rotation.

**Features:**
- Loads keys from environment: `BYTEZ_API_KEY_1`, `BYTEZ_API_KEY_2`, ...
- Tracks key health (failed, usage count, error count)
- Rotates on 401/403/429/5xx errors
- Emits rotation events for UI notifications

**Usage:**
```python
from services.key_manager import get_key_manager

km = get_key_manager()
key = km.get_current_key()  # Get active key
km.record_success()  # Record successful call
km.mark_current_key_failed("401 Unauthorized")  # Mark failed
km.rotate_key()  # Rotate to next key
event = km.get_and_clear_last_event()  # Get rotation event
```

### 2. Bytez Client (`backend/services/bytez_client.py`)

OpenAI-compatible HTTP client for Bytez API.

**Features:**
- Base URL: `https://api.bytez.com/models/v2/openai/v1`
- Automatic key rotation on auth/rate-limit errors
- Streaming and non-streaming support
- Tool calling support (OpenAI function schemas)

**Usage:**
```python
from services.bytez_client import get_bytez_client

client = await get_bytez_client()
response = await client.chat_completions(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": "Hello"}],
    temperature=0.7,
    max_tokens=1000,
    stream=False
)
```

### 3. Agent Config (`backend/services/agent_config.py`)

Centralized registry of all agents with system prompts.

**Agents:**
- **Orchestrator** — Classifies query type (SQL_ONLY, PY_ONLY, SQL_THEN_PY, EXPLAIN_ONLY)
- **SQL Agent** — Generates and executes DuckDB queries
- **Python Agent** — Performs statistical analysis
- **Composer** — Synthesizes final response
- **Validator** — Checks consistency (optional)

**Usage:**
```python
from services.agent_config import get_agent_config, get_tools_for_agent

config = get_agent_config("sql_agent")
print(config.system_prompt)
print(config.model)  # "gpt-4-turbo"
print(config.temperature)  # 0.2

tools = get_tools_for_agent("sql_agent")  # ["get_data_dna", "run_sql"]
```

### 4. SQL Executor (`backend/services/sql_executor.py`)

Safe SQL execution with validation and DuckDB.

**Features:**
- Validates SQL (blocks dangerous keywords)
- Only allows SELECT statements
- Replaces `transactions` placeholder with actual parquet path
- Applies row limits for UI previews
- Downloads parquet from Supabase Storage if needed

**Usage:**
```python
from services.sql_executor import run_sql, validate_sql

# Validate first
is_valid, error = validate_sql("SELECT * FROM transactions")

# Execute
result_df, summary = run_sql(
    session_id="abc123",
    sql="SELECT age_group, COUNT(*) FROM transactions GROUP BY age_group",
    limit_rows=500
)
```

### 5. Python Executor (`backend/services/python_executor.py`)

Safe Python execution with AST validation.

**Features:**
- Validates code AST (blocks dangerous imports/calls)
- Allows: pandas, numpy, scipy, math, statistics, json
- Blocks: open, exec, eval, __import__, file operations
- Runs in subprocess with timeout
- Provides safe locals: df, result_df, pd, np, stats

**Usage:**
```python
from services.python_executor import run_python, validate_python_code

# Validate first
is_valid, error = validate_python_code("import pandas as pd")

# Execute
code = """
results = {
    'mean': df['amount'].mean(),
    'std': df['amount'].std()
}
"""
results, summary = run_python(code, df=my_dataframe, timeout_s=10)
```

### 6. Orchestrator (`backend/services/orchestrator.py`)

Multi-agent workflow orchestration with streaming.

**Features:**
- Loads Data DNA from Supabase
- Routes queries through agent chain
- Streams events via async generator
- Saves messages and updates accumulated_insights
- Handles SQL and Python execution

**Usage:**
```python
from services.orchestrator import get_orchestrator

orchestrator = await get_orchestrator()

async for event in orchestrator.stream_chat(
    chat_id="chat_xyz",
    session_id="session_abc",
    message="Which age group has highest failure rate?",
    history=[]
):
    print(event)  # {"type": "status", "message": "...", ...}
```

## Event Stream Format

The `/api/chat/stream` endpoint returns Server-Sent Events (SSE) with the following event types:

### Status Events
```json
{
  "type": "status",
  "message": "Loading dataset profile...",
  "data": {"stage": "loading"}
}
```

### Orchestrator Result
```json
{
  "type": "orchestrator_result",
  "data": {
    "classification": "SQL_THEN_PY",
    "reasoning": "Need to query data then analyze",
    "columns_needed": ["age_group", "transaction_status"],
    "next_agent": "sql_agent"
  }
}
```

### SQL Result
```json
{
  "type": "sql_result",
  "data": {
    "query": "SELECT age_group, COUNT(*) FROM transactions GROUP BY age_group",
    "rows": 5,
    "columns": ["age_group", "count"],
    "summary": "Query returned 5 rows, 2 columns",
    "data": [{"age_group": "18-25", "count": 1000}, ...]
  }
}
```

### Python Result
```json
{
  "type": "python_result",
  "data": {
    "code": "results = {'mean': df['amount'].mean()}",
    "results": {"mean": 1840.5},
    "summary": "Python execution completed successfully"
  }
}
```

### Final Response
```json
{
  "type": "final_response",
  "data": {
    "text": "The 18-25 age group has the highest failure rate at 7.8%...",
    "metrics": {"failure_rate": 0.078, "confidence": 95},
    "chart_spec": {"type": "bar", "data": [...]},
    "follow_ups": ["Why is this age group affected?", "..."]
  }
}
```

### Error Events
```json
{
  "type": "error",
  "message": "SQL execution failed: Invalid column name"
}
```

## Environment Setup

Add to `backend/.env`:

```bash
# Bytez API Keys (required)
BYTEZ_API_KEY_1=your_key_1
BYTEZ_API_KEY_2=your_key_2
# or legacy format:
# BYTEZ_API_KEYS=key1,key2,key3
# or single key:
# BYTEZ_API_KEY=your_key

# Existing Supabase config
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...
```

## Frontend Integration

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
    body: JSON.stringify({ chat_id: chatId, session_id: sessionId, message, history }),
  });

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
          console.error("Failed to parse event:", e);
        }
      }
    }
  }
}
```

Update `insightx-app/components/workspace/ChatPanel.tsx`:

```typescript
async function handleSendMessage(text: string) {
  // Save user message
  const userMsg = { role: "user", content: text };
  setMessages([...messages, userMsg]);

  // Stream response
  const assistantMsg = { role: "assistant", content: "" };
  setMessages([...messages, userMsg, assistantMsg]);

  try {
    for await (const event of chatStream(chatId, sessionId, text, messages)) {
      if (event.type === "status") {
        setThinkingSteps([...thinkingSteps, event.message]);
      } else if (event.type === "final_response") {
        assistantMsg.content = event.data.text;
        setMessages([...messages, userMsg, assistantMsg]);
      } else if (event.type === "error") {
        console.error("Stream error:", event.message);
      }
    }
  } catch (error) {
    console.error("Chat failed:", error);
  }
}
```

## Testing

### Test Key Manager
```bash
cd backend
python -c "
from services.key_manager import get_key_manager
km = get_key_manager()
print(f'Keys loaded: {len(km.keys)}')
print(f'Current key index: {km.current_key_index}')
print(f'Stats: {km.get_stats()}')
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
        messages=[{'role': 'user', 'content': 'Hello'}],
        temperature=0.7
    )
    print(response)

asyncio.run(test())
"
```

### Test SQL Executor
```bash
python -c "
from services.sql_executor import run_sql, validate_sql

# Validate
is_valid, error = validate_sql('SELECT * FROM transactions')
print(f'Valid: {is_valid}')

# Run (requires valid session_id)
# result_df, summary = run_sql('session_id', 'SELECT COUNT(*) FROM transactions')
# print(result_df)
"
```

### Test Python Executor
```bash
python -c "
from services.python_executor import run_python, validate_python_code
import pandas as pd

# Validate
is_valid, error = validate_python_code('import pandas as pd')
print(f'Valid: {is_valid}')

# Run
code = 'results = {\"mean\": 42}'
results, summary = run_python(code, df=pd.DataFrame())
print(results)
"
```

## Troubleshooting

### "No Bytez API keys found"
- Check `.env` file has `BYTEZ_API_KEY_1` or `BYTEZ_API_KEYS` set
- Restart the server after updating `.env`

### "All API keys exhausted"
- Check Bytez account for quota/billing issues
- Verify keys are valid and not rate-limited
- Check `KeyManager.get_stats()` for error details

### "SQL execution failed"
- Check SQL syntax (only SELECT allowed)
- Verify column names exist in dataset
- Check row limits aren't too restrictive

### "Python execution timed out"
- Reduce timeout_s parameter
- Simplify Python code
- Check for infinite loops

## Next Steps

1. Add Bytez API keys to `.env`
2. Test each component individually
3. Deploy to Railway
4. Update frontend to consume SSE stream
5. Monitor key rotation events in production
6. Add caching for frequently-run queries
7. Implement validator agent for consistency checks

## References

- [flow_of_work.md](../flow_of_work.md) — System architecture
- [PLAN_FOR_BYTEZ_DUCKDB_PY_AGENTS.md](../PLAN_FOR_BYTEZ_DUCKDB_PY_AGENTS.md) — Implementation plan
- [HOW_OTHERS_DO_IT](../HOW_OTHERS_DO_IT) — Reference patterns
