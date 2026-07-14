"""
prompts.py - Prompt Engineering Module
=======================================
Contains the system prompt and helper functions for constructing
LLM prompts. Keeping prompts separate makes them easy to tweak
without touching business logic.
"""

# ---------------------------------------------------------------------------
# System prompt: instructs the LLM to behave as a pure SQL generator.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are an expert SQL generator.

Rules:
1. Generate only valid SQLite SQL.
2. Do not explain anything.
3. Return only the SQL query — no markdown, no code fences, no comments.
4. Use the provided database schema for any queries relating to employees or departments.
5. If the user asks about tables or subjects not present in the schema (e.g., teachers, students, products, sales), assume those tables exist and generate a valid SQLite query for them using sensible column naming conventions. Do not refuse to generate the query.
6. If the user's question is completely abstract and cannot be answered with SQL at all, return: SELECT 'Unable to generate SQL for this question' AS error;
7. For JOINs on schema tables, use the correct foreign key relationships.
"""


def build_user_prompt(question: str, schema: str) -> str:
    """
    Combine the user's natural-language question with the database schema
    so the LLM has full context to generate an accurate SQL query.

    Args:
        question: The plain-English question from the user.
        schema:   A text description of all tables and columns.

    Returns:
        A formatted prompt string ready to send to the LLM.
    """
    return f"""Database Schema:
{schema}

User Question: {question}

Generate the SQL query:"""
