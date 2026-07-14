"""
llm.py - LLM Integration Module
=================================
Handles communication with the Groq API to convert
natural-language questions into SQL queries.
"""

import os
import re
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPT, build_user_prompt

# Load environment variables from backend/.env
# Using __file__ so it works regardless of the working directory
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

# ---------------------------------------------------------------------------
# Groq client (initialised once at module level)
# ---------------------------------------------------------------------------
_client: Groq | None = None


def _get_client() -> Groq:
    """Lazy-initialise and return the Groq client."""
    global _client
    if _client is None:
        # Clear proxy environment variables to prevent httpx constructor bugs on Render
        for proxy_key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
            os.environ.pop(proxy_key, None)

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Add it to your .env file or export it as an environment variable."
            )
        _client = Groq(api_key=api_key)
    return _client


# ---------------------------------------------------------------------------
# Clean up the raw LLM response
# ---------------------------------------------------------------------------
def _clean_sql(raw: str) -> str:
    """
    Strip markdown code fences and extraneous whitespace that the LLM
    may return despite being told not to.
    """
    # Remove ```sql ... ``` wrappers
    cleaned = re.sub(r"```(?:sql)?\s*", "", raw)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()


# ---------------------------------------------------------------------------
# Public function: generate SQL from a question
# ---------------------------------------------------------------------------
def generate_sql(question: str, schema: str) -> dict:
    """
    Send the user's question (plus the DB schema) to Groq and return
    the generated SQL query.

    Args:
        question: Plain-English question from the user.
        schema:   Database schema text.

    Returns:
        dict with keys:
          - success (bool)
          - sql     (str)   — the generated SQL query
          - message (str)   — error description on failure
    """
    try:
        client = _get_client()

        # Build the chat messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": build_user_prompt(question, schema)},
        ]

        # Call the Groq API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0,      # deterministic output
            max_tokens=1024,
        )

        # Extract and clean the SQL
        raw_sql = response.choices[0].message.content
        sql = _clean_sql(raw_sql)

        return {"success": True, "sql": sql, "message": "SQL generated successfully."}

    except ValueError as ve:
        # Missing API key
        return {"success": False, "sql": "", "message": str(ve)}

    except Exception as e:
        # Network / API errors
        return {
            "success": False,
            "sql": "",
            "message": f"Groq API Error: {str(e)}",
        }


# ---------------------------------------------------------------------------
# Public function: generate mock results from a query
# ---------------------------------------------------------------------------
def generate_mock_results(sql: str) -> dict:
    """
    Send the SQL query to Groq to generate matching columns and 3-5 rows
    of mock sample data. Used when the database doesn't have the table.

    Args:
        sql: The generated SQL query.

    Returns:
        dict with keys:
          - success (bool)
          - columns (list[str])
          - rows    (list[list])
          - message (str)
    """
    import json
    try:
        client = _get_client()
        prompt = f"""You are a database mocker. Given the SQL query:
{sql}

Generate a realistic mock result set as a JSON object with exactly two keys:
1. "columns": a list of string column names that would be returned by this query.
2. "rows": a list of lists representing 3 to 5 realistic mock data rows matching the column structure and conditions of the query.

Return ONLY a valid raw JSON block. Do not explain anything, do not include markdown wrappers or code fences.
Example format:
{{"columns": ["id", "name"], "rows": [[1, "John Doe"], [2, "Jane Smith"]]}}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1024,
        )

        raw_content = response.choices[0].message.content.strip()
        
        # Clean any markdown code fences if returned
        cleaned = re.sub(r"```(?:json)?\s*", "", raw_content)
        cleaned = re.sub(r"```", "", cleaned).strip()

        data = json.loads(cleaned)
        if "columns" in data and "rows" in data:
            return {
                "success": True,
                "columns": data["columns"],
                "rows": data["rows"],
                "message": "Generated sample results mock (table/columns not present in SQLite database)."
            }
        
        raise ValueError("Invalid JSON format from mock generator.")

    except Exception as e:
        return {
            "success": False,
            "columns": ["error_details"],
            "rows": [[f"SQL Error: could not execute or generate mock results. Detail: {str(e)}"]],
            "message": f"Failed to generate mock data: {str(e)}"
        }

