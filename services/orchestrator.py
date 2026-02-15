"""Multi-agent orchestration for InsightX."""
import json
from typing import Dict, Any, AsyncGenerator, Optional, List
from datetime import datetime
from db.client import supabase
from services.bytez_client import get_bytez_client
from services.agent_config import get_agent_config, AGENTS
from services.sql_executor import run_sql
from services.python_executor import run_python
import pandas as pd


class Orchestrator:
    """Orchestrates multi-agent workflow for data analysis."""

    def __init__(self):
        self.bytez_client = None

    async def initialize(self):
        """Initialize the orchestrator with Bytez client."""
        self.bytez_client = await get_bytez_client()

    async def stream_chat(
        self,
        chat_id: str,
        session_id: str,
        message: str,
        history: List[Dict[str, Any]],
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream a chat response with multi-agent orchestration.

        Args:
            chat_id: Chat ID
            session_id: Session ID
            message: User message
            history: Chat history

        Yields:
            Event dicts with type and data
        """
        try:
            # 1. Load session and Data DNA
            yield {
                "type": "status",
                "message": "Loading dataset profile...",
                "data": {"stage": "loading"},
            }

            session_result = supabase.table("sessions").select("*").eq("id", session_id).execute()
            if not session_result.data:
                raise ValueError(f"Session {session_id} not found")

            session = session_result.data[0]
            data_dna = session.get("data_dna", {})

            # 2. Run Orchestrator agent to classify query
            yield {
                "type": "status",
                "message": "Analyzing query...",
                "data": {"stage": "orchestrating"},
            }

            orchestrator_config = get_agent_config("orchestrator")
            classification = await self._run_agent(
                agent_id="orchestrator",
                messages=[
                    {
                        "role": "system",
                        "content": orchestrator_config.system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"Dataset: {json.dumps(data_dna.get('columns', [])[:5])}\n\nUser query: {message}",
                    },
                ],
            )

            yield {
                "type": "orchestrator_result",
                "data": classification,
            }

            # Parse classification
            try:
                classification_obj = json.loads(classification)
            except json.JSONDecodeError:
                classification_obj = {"classification": "EXPLAIN_ONLY"}

            query_type = classification_obj.get("classification", "EXPLAIN_ONLY")

            # 3. Execute based on classification
            sql_result = None
            python_result = None

            if query_type in ("SQL_ONLY", "SQL_THEN_PY"):
                yield {
                    "type": "status",
                    "message": "Generating SQL query...",
                    "data": {"stage": "sql_generation"},
                }

                sql_agent_config = get_agent_config("sql_agent")
                sql_query = await self._run_agent(
                    agent_id="sql_agent",
                    messages=[
                        {
                            "role": "system",
                            "content": sql_agent_config.system_prompt,
                        },
                        {
                            "role": "user",
                            "content": f"Dataset columns: {json.dumps(data_dna.get('columns', []))}\n\nGenerate SQL for: {message}",
                        },
                    ],
                )

                yield {
                    "type": "status",
                    "message": "Executing SQL query...",
                    "data": {"stage": "sql_execution"},
                }

                # Extract SQL from response
                sql_to_run = self._extract_sql(sql_query)
                if sql_to_run:
                    try:
                        result_df, sql_summary = run_sql(session_id, sql_to_run)
                        sql_result = {
                            "query": sql_to_run,
                            "rows": len(result_df),
                            "columns": list(result_df.columns),
                            "summary": sql_summary,
                            "data": result_df.head(10).to_dict("records"),
                        }

                        yield {
                            "type": "sql_result",
                            "data": sql_result,
                        }
                    except Exception as e:
                        yield {
                            "type": "error",
                            "message": f"SQL execution failed: {str(e)}",
                        }

            if query_type in ("PY_ONLY", "SQL_THEN_PY") and sql_result:
                yield {
                    "type": "status",
                    "message": "Running Python analysis...",
                    "data": {"stage": "python_execution"},
                }

                python_agent_config = get_agent_config("python_agent")
                python_code = await self._run_agent(
                    agent_id="python_agent",
                    messages=[
                        {
                            "role": "system",
                            "content": python_agent_config.system_prompt,
                        },
                        {
                            "role": "user",
                            "content": f"SQL results: {json.dumps(sql_result)}\n\nAnalyze for: {message}",
                        },
                    ],
                )

                # Extract Python code and run it
                python_to_run = self._extract_python(python_code)
                if python_to_run:
                    try:
                        # Load data for Python execution
                        result_df = pd.DataFrame(sql_result["data"])
                        python_result, py_summary = run_python(
                            python_to_run, result_df
                        )

                        yield {
                            "type": "python_result",
                            "data": {
                                "code": python_to_run,
                                "results": python_result,
                                "summary": py_summary,
                            },
                        }
                    except Exception as e:
                        yield {
                            "type": "error",
                            "message": f"Python execution failed: {str(e)}",
                        }

            # 4. Compose final response
            yield {
                "type": "status",
                "message": "Composing response...",
                "data": {"stage": "composition"},
            }

            composer_config = get_agent_config("composer")
            final_response = await self._run_agent(
                agent_id="composer",
                messages=[
                    {
                        "role": "system",
                        "content": composer_config.system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"SQL: {json.dumps(sql_result)}\nPython: {json.dumps(python_result)}\n\nCompose response for: {message}",
                    },
                ],
            )

            # Parse final response
            try:
                response_obj = json.loads(final_response)
            except json.JSONDecodeError:
                response_obj = {"text": final_response}

            # 5. Save to Supabase
            message_data = {
                "chat_id": chat_id,
                "role": "assistant",
                "content": json.dumps(response_obj),
            }

            supabase.table("messages").insert(message_data).execute()

            # 6. Update accumulated insights
            if "finding" in response_obj:
                insights = data_dna.get("accumulated_insights", [])
                insights.append(
                    {
                        "query": message,
                        "finding": response_obj.get("finding"),
                        "confidence": response_obj.get("confidence", 0),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

                supabase.table("sessions").update(
                    {"data_dna": {**data_dna, "accumulated_insights": insights}}
                ).eq("id", session_id).execute()

            yield {
                "type": "final_response",
                "data": response_obj,
            }

        except Exception as e:
            yield {
                "type": "error",
                "message": f"Orchestration failed: {str(e)}",
            }

    async def _run_agent(
        self, agent_id: str, messages: List[Dict[str, str]]
    ) -> str:
        """Run a single agent and return its response.

        Args:
            agent_id: Agent identifier
            messages: Message history

        Returns:
            Agent response text
        """
        config = get_agent_config(agent_id)

        response = await self.bytez_client.chat_completions(
            model=config.model,
            messages=messages,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

        # Extract text from response
        if "choices" in response and response["choices"]:
            return response["choices"][0]["message"]["content"]

        return ""

    def _extract_sql(self, response: str) -> Optional[str]:
        """Extract SQL query from agent response.

        Args:
            response: Agent response text

        Returns:
            SQL query or None
        """
        # Look for SQL in code blocks
        if "```sql" in response:
            start = response.find("```sql") + 6
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()

        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                sql = response[start:end].strip()
                if sql.upper().startswith("SELECT"):
                    return sql

        # Look for SELECT statement
        if "SELECT" in response.upper():
            start = response.upper().find("SELECT")
            # Find the end (next newline or end of string)
            end = response.find("\n", start)
            if end == -1:
                end = len(response)
            return response[start:end].strip()

        return None

    def _extract_python(self, response: str) -> Optional[str]:
        """Extract Python code from agent response.

        Args:
            response: Agent response text

        Returns:
            Python code or None
        """
        # Look for Python in code blocks
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()

        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()

        return None


# Global orchestrator instance
_orchestrator: Optional[Orchestrator] = None


async def get_orchestrator() -> Orchestrator:
    """Get or create the global Orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
        await _orchestrator.initialize()
    return _orchestrator
