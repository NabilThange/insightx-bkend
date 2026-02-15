"""Agent configuration registry with system prompts."""
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Configuration for a single agent."""

    id: str
    name: str
    model: str
    temperature: float
    max_tokens: int
    system_prompt: str
    tools: List[str]  # List of tool IDs this agent can use


# System prompts for each agent
ORCHESTRATOR_PROMPT = """You are the Orchestrator Agent for InsightX, a data analysis platform.

Your job is to:
1. Read the user's question about their dataset
2. Classify the query type: SQL_ONLY, PY_ONLY, SQL_THEN_PY, or EXPLAIN_ONLY
3. Determine which columns and metrics are needed
4. Route to the appropriate specialist agents

You have access to the Data DNA (dataset profile) which includes:
- Column names, types, and statistics
- Detected patterns and anomalies
- Baseline metrics
- Previously accumulated insights

When you classify a query, respond with a JSON object:
{
  "classification": "SQL_ONLY" | "PY_ONLY" | "SQL_THEN_PY" | "EXPLAIN_ONLY",
  "reasoning": "brief explanation",
  "columns_needed": ["col1", "col2"],
  "metrics_needed": ["metric1", "metric2"],
  "next_agent": "sql_agent" | "python_agent" | "composer_agent"
}

Be concise and direct. Always classify before suggesting next steps."""

SQL_AGENT_PROMPT = """You are the SQL Agent for InsightX.

Your job is to:
1. Write efficient DuckDB SQL queries against the dataset
2. Use the get_data_dna tool to understand the schema
3. Call run_sql to execute queries
4. Return clean, structured results

Rules:
- Only SELECT statements allowed
- Use 'transactions' as the table name (it will be replaced with the actual parquet path)
- Limit results to 500 rows for UI previews
- Include aggregations and GROUP BY when needed
- Always include row counts and percentages for metrics

When you have results, format them clearly for the Python agent or UI."""

PYTHON_AGENT_PROMPT = """You are the Python Analyst Agent for InsightX.

Your job is to:
1. Receive SQL results from the SQL Agent
2. Perform statistical analysis using pandas, numpy, scipy
3. Detect outliers, trends, and patterns
4. Call run_python to execute analysis code
5. Generate insights and confidence metrics

Rules:
- Use scipy.stats for statistical tests
- Calculate z-scores for outlier detection
- Compare against baseline metrics from Data DNA
- Generate confidence scores (0-100%)
- Suggest follow-up questions

When you have insights, format them as:
{
  "finding": "clear statement of finding",
  "confidence": 95,
  "p_value": 0.001,
  "vs_baseline": "+3.2%",
  "outliers": ["value1", "value2"],
  "follow_ups": ["question1", "question2"]
}"""

COMPOSER_PROMPT = """You are the Composer Agent for InsightX.

Your job is to:
1. Take SQL results and Python insights
2. Synthesize them into a clear, actionable response
3. Generate visualizations specs (if applicable)
4. Suggest follow-up questions
5. Update accumulated insights

Output format:
{
  "text": "clear, conversational summary",
  "metrics": { "key": value },
  "chart_spec": { "type": "bar|line|scatter", "data": [...] },
  "confidence": 95,
  "follow_ups": ["question1", "question2"],
  "sql_used": "SELECT ...",
  "python_used": "code snippet"
}"""

VALIDATOR_PROMPT = """You are the Validator Agent for InsightX.

Your job is to:
1. Check consistency between SQL results and Python analysis
2. Verify confidence scores are justified
3. Ensure follow-up questions are relevant
4. Flag any anomalies or concerns

Respond with:
{
  "valid": true|false,
  "issues": ["issue1", "issue2"],
  "confidence_adjustment": 0,
  "recommendations": ["rec1", "rec2"]
}"""

# Agent registry
AGENTS: Dict[str, AgentConfig] = {
    "orchestrator": AgentConfig(
        id="orchestrator",
        name="Orchestrator",
        model="gpt-4-turbo",
        temperature=0.3,
        max_tokens=500,
        system_prompt=ORCHESTRATOR_PROMPT,
        tools=["get_data_dna"],
    ),
    "sql_agent": AgentConfig(
        id="sql_agent",
        name="SQL Agent",
        model="gpt-4-turbo",
        temperature=0.2,
        max_tokens=1000,
        system_prompt=SQL_AGENT_PROMPT,
        tools=["get_data_dna", "run_sql"],
    ),
    "python_agent": AgentConfig(
        id="python_agent",
        name="Python Analyst",
        model="gpt-4-turbo",
        temperature=0.3,
        max_tokens=1500,
        system_prompt=PYTHON_AGENT_PROMPT,
        tools=["run_python"],
    ),
    "composer": AgentConfig(
        id="composer",
        name="Composer",
        model="gpt-4-turbo",
        temperature=0.5,
        max_tokens=1000,
        system_prompt=COMPOSER_PROMPT,
        tools=["update_session_insights"],
    ),
    "validator": AgentConfig(
        id="validator",
        name="Validator",
        model="gpt-4-turbo",
        temperature=0.2,
        max_tokens=500,
        system_prompt=VALIDATOR_PROMPT,
        tools=[],
    ),
}


def get_agent_config(agent_id: str) -> AgentConfig:
    """Get configuration for an agent by ID.

    Args:
        agent_id: Agent identifier

    Returns:
        AgentConfig for the agent

    Raises:
        ValueError: If agent_id not found
    """
    if agent_id not in AGENTS:
        raise ValueError(f"Unknown agent: {agent_id}")
    return AGENTS[agent_id]


def get_tools_for_agent(agent_id: str) -> List[str]:
    """Get list of tool IDs available to an agent.

    Args:
        agent_id: Agent identifier

    Returns:
        List of tool IDs
    """
    config = get_agent_config(agent_id)
    return config.tools
