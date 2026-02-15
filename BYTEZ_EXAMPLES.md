# Bytez Implementation — Usage Examples

## Example 1: Basic Chat Flow

### User Query
```
"Which age group has the highest failure rate during peak hours?"
```

### Backend Processing

1. **Orchestrator classifies:**
```json
{
  "classification": "SQL_THEN_PY",
  "reasoning": "Need to extract failure rates by age group and hour, then analyze",
  "columns_needed": ["age_group", "transaction_status", "created_at"],
  "next_agent": "sql_agent"
}
```

2. **SQL Agent generates query:**
```sql
SELECT 
  age_group,
  EXTRACT(HOUR FROM created_at) AS hour,
  COUNT(*) AS total,
  ROUND(100.0 * SUM(CASE WHEN transaction_status='FAILED' THEN 1 ELSE 0 END) / COUNT(*), 2) AS failure_rate
FROM transactions
WHERE EXTRACT(HOUR FROM created_at) BETWEEN 18 AND 22
GROUP BY age_group, hour
ORDER BY failure_rate DESC
```

3. **SQL executes and returns:**
```
age_group | hour | total | failure_rate
----------|------|-------|-------------
18-25     | 20   | 1200  | 7.8
26-35     | 20   | 1500  | 5.2
36-45     | 20   | 1100  | 4.1
...
```

4. **Python Agent analyzes:**
```python
import pandas as pd
from scipy import stats

# Calculate z-scores
result_df['z_score'] = stats.zscore(result_df['failure_rate'])
result_df['is_outlier'] = result_df['z_score'].abs() > 2

# Compare to baseline
baseline = 4.2  # From Data DNA
result_df['vs_baseline'] = result_df['failure_rate'] - baseline

# Find significant findings
findings = result_df[result_df['is_outlier']]
```

5. **Composer synthesizes:**
```json
{
  "text": "The 18-25 age group shows a significantly higher failure rate of 7.8% during peak hours (8PM), which is 3.6% above the baseline of 4.2%. This is statistically significant (z-score: 2.4, p < 0.05). The 26-35 age group also shows elevated failure at 5.2%, but within normal variation.",
  "metrics": {
    "peak_failure_rate": 0.078,
    "baseline": 0.042,
    "difference": 0.036,
    "z_score": 2.4,
    "confidence": 95
  },
  "chart_spec": {
    "type": "bar",
    "title": "Failure Rate by Age Group (Peak Hours)",
    "data": [
      {"age_group": "18-25", "failure_rate": 7.8},
      {"age_group": "26-35", "failure_rate": 5.2},
      {"age_group": "36-45", "failure_rate": 4.1}
    ]
  },
  "follow_ups": [
    "Why is the 18-25 age group more affected?",
    "Is this consistent across all days of the week?",
    "What device types are used by this age group?"
  ]
}
```

### Frontend Receives SSE Stream

```
data: {"type": "status", "message": "Loading dataset profile...", "data": {"stage": "loading"}}

data: {"type": "status", "message": "Analyzing query...", "data": {"stage": "orchestrating"}}

data: {"type": "orchestrator_result", "data": {"classification": "SQL_THEN_PY", ...}}

data: {"type": "status", "message": "Generating SQL query...", "data": {"stage": "sql_generation"}}

data: {"type": "status", "message": "Executing SQL query...", "data": {"stage": "sql_execution"}}

data: {"type": "sql_result", "data": {"query": "SELECT ...", "rows": 12, "columns": ["age_group", "hour", "total", "failure_rate"], ...}}

data: {"type": "status", "message": "Running Python analysis...", "data": {"stage": "python_execution"}}

data: {"type": "python_result", "data": {"code": "import pandas as pd...", "results": {...}, "summary": "Python execution completed successfully"}}

data: {"type": "status", "message": "Composing response...", "data": {"stage": "composition"}}

data: {"type": "final_response", "data": {"text": "The 18-25 age group shows...", "metrics": {...}, "chart_spec": {...}, "follow_ups": [...]}}
```

## Example 2: SQL-Only Query

### User Query
```
"Show me the top 5 merchants by transaction volume"
```

### Backend Processing

1. **Orchestrator classifies:**
```json
{
  "classification": "SQL_ONLY",
  "reasoning": "Simple data extraction, no analysis needed"
}
```

2. **SQL Agent generates:**
```sql
SELECT 
  merchant_id,
  merchant_name,
  COUNT(*) AS transaction_count,
  SUM(amount) AS total_volume
FROM transactions
GROUP BY merchant_id, merchant_name
ORDER BY transaction_count DESC
LIMIT 5
```

3. **Composer formats response:**
```json
{
  "text": "Here are the top 5 merchants by transaction volume:\n\n1. Amazon - 45,230 transactions ($2.1M)\n2. Flipkart - 38,120 transactions ($1.8M)\n3. Paytm - 32,450 transactions ($1.5M)\n4. Google Play - 28,900 transactions ($1.2M)\n5. Netflix - 25,670 transactions ($890K)",
  "chart_spec": {
    "type": "bar",
    "title": "Top 5 Merchants by Volume",
    "data": [...]
  }
}
```

## Example 3: Python-Only Query

### User Query
```
"Calculate the correlation between transaction amount and failure rate"
```

### Backend Processing

1. **Orchestrator classifies:**
```json
{
  "classification": "PY_ONLY",
  "reasoning": "Statistical analysis, no SQL needed"
}
```

2. **Python Agent generates:**
```python
import pandas as pd
from scipy import stats

# Calculate correlation
correlation = df['amount'].corr(df['is_failed'].astype(int))

# Perform statistical test
pearson_r, p_value = stats.pearsonr(df['amount'], df['is_failed'].astype(int))

# Group by amount ranges
df['amount_range'] = pd.cut(df['amount'], bins=5)
failure_by_range = df.groupby('amount_range')['is_failed'].mean()

results = {
  "correlation": float(correlation),
  "pearson_r": float(pearson_r),
  "p_value": float(p_value),
  "significant": p_value < 0.05,
  "failure_by_amount_range": failure_by_range.to_dict()
}
```

3. **Composer synthesizes:**
```json
{
  "text": "There is a weak negative correlation (-0.12) between transaction amount and failure rate, which is statistically significant (p < 0.001). This suggests that higher-value transactions are slightly less likely to fail.",
  "metrics": {
    "correlation": -0.12,
    "p_value": 0.0001,
    "significant": true
  }
}
```

## Example 4: Key Rotation

### Scenario: First key hits rate limit

```python
from services.key_manager import get_key_manager
from services.bytez_client import get_bytez_client

km = get_key_manager()
client = await get_bytez_client()

# First call with key 1
try:
    response = await client.chat_completions(...)
except Exception as e:
    if "429" in str(e):  # Rate limited
        km.mark_current_key_failed("429 Rate Limited")
        km.rotate_key()  # Rotate to key 2
        await client._refresh_client()
        response = await client.chat_completions(...)  # Retry with key 2
```

### Event emitted:
```json
{
  "type": "key_rotation_event",
  "data": {
    "type": "key_rotated",
    "from_index": 0,
    "to_index": 1,
    "timestamp": "2026-02-15T20:00:00Z"
  }
}
```

## Example 5: Error Handling

### Scenario: Invalid SQL

```python
from services.sql_executor import run_sql, validate_sql

sql = "DROP TABLE transactions"
is_valid, error = validate_sql(sql)

if not is_valid:
    # Error: "Dangerous keyword 'DROP' not allowed"
    yield {
        "type": "error",
        "message": f"Invalid SQL: {error}"
    }
```

### Scenario: Python timeout

```python
from services.python_executor import run_python

code = """
while True:
    pass  # Infinite loop
"""

try:
    results, summary = run_python(code, df, timeout_s=5)
except RuntimeError as e:
    # Error: "Python execution timed out after 5s"
    yield {
        "type": "error",
        "message": f"Analysis failed: {str(e)}"
    }
```

## Example 6: Accumulated Insights

### First Query
```
User: "What's the average transaction amount?"
Response: "The average transaction amount is ₹1,840"
```

Saved to `sessions.data_dna.accumulated_insights`:
```json
{
  "query": "What's the average transaction amount?",
  "finding": "The average transaction amount is ₹1,840",
  "confidence": 100,
  "timestamp": "2026-02-15T20:00:00Z"
}
```

### Second Query
```
User: "How does this compare to last month?"
```

Orchestrator reads accumulated_insights and knows:
- Previous finding: average = ₹1,840
- Can now compare to historical data

Response: "This month's average of ₹1,840 is 5% higher than last month's ₹1,752"

## Example 7: Frontend Integration

### React Component

```typescript
import { useState } from "react";
import { chatStream } from "@/lib/api/backend";

export function ChatPanel() {
  const [messages, setMessages] = useState([]);
  const [thinking, setThinking] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleSendMessage(text: string) {
    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);
    setThinking([]);

    try {
      let assistantContent = "";

      for await (const event of chatStream(chatId, sessionId, text, messages)) {
        if (event.type === "status") {
          // Show thinking step
          setThinking((prev) => [...prev, event.message]);
        } else if (event.type === "orchestrator_result") {
          // Log classification
          console.log("Query type:", event.data.classification);
        } else if (event.type === "sql_result") {
          // Show SQL execution
          setThinking((prev) => [
            ...prev,
            `Executed SQL: ${event.data.rows} rows returned`,
          ]);
        } else if (event.type === "python_result") {
          // Show Python analysis
          setThinking((prev) => [
            ...prev,
            `Analysis complete: ${JSON.stringify(event.data.results)}`,
          ]);
        } else if (event.type === "final_response") {
          // Add assistant message
          assistantContent = event.data.text;
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: assistantContent,
              metrics: event.data.metrics,
              chart: event.data.chart_spec,
              followUps: event.data.follow_ups,
            },
          ]);
        } else if (event.type === "error") {
          // Show error
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
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      {/* Thinking process */}
      {thinking.length > 0 && (
        <div className="thinking-steps">
          {thinking.map((step, i) => (
            <div key={i} className="step">
              {step}
            </div>
          ))}
        </div>
      )}

      {/* Messages */}
      {messages.map((msg, i) => (
        <div key={i} className={`message ${msg.role}`}>
          {msg.content}
          {msg.chart && <Chart spec={msg.chart} />}
          {msg.followUps && (
            <div className="follow-ups">
              {msg.followUps.map((q, j) => (
                <button key={j} onClick={() => handleSendMessage(q)}>
                  {q}
                </button>
              ))}
            </div>
          )}
        </div>
      ))}

      {/* Input */}
      <input
        type="text"
        placeholder="Ask about your data..."
        onKeyPress={(e) => {
          if (e.key === "Enter") {
            handleSendMessage(e.currentTarget.value);
            e.currentTarget.value = "";
          }
        }}
        disabled={loading}
      />
    </div>
  );
}
```

## Example 8: Testing

### Test Key Manager
```bash
python -c "
from services.key_manager import get_key_manager

km = get_key_manager()
print(f'Keys loaded: {len(km.keys)}')
print(f'Current key index: {km.current_key_index}')

# Simulate failure
km.mark_current_key_failed('401 Unauthorized')
print(f'Failed keys: {len(km.failed_keys)}')

# Rotate
if km.rotate_key():
    print(f'Rotated to index: {km.current_key_index}')
    event = km.get_and_clear_last_event()
    print(f'Event: {event}')
"
```

### Test Orchestrator
```bash
python -c "
import asyncio
from services.orchestrator import get_orchestrator

async def test():
    orchestrator = await get_orchestrator()
    
    async for event in orchestrator.stream_chat(
        chat_id='test-chat',
        session_id='test-session',
        message='Analyze the data',
        history=[]
    ):
        print(f'{event[\"type\"]}: {event.get(\"message\", event.get(\"data\", \"\"))}')

asyncio.run(test())
"
```

## Summary

These examples show:
1. Complete query flow with multi-agent orchestration
2. Different query types (SQL, Python, combined)
3. Key rotation handling
4. Error handling
5. Accumulated insights usage
6. Frontend integration
7. Testing patterns

All components work together to provide a seamless, intelligent data analysis experience.
