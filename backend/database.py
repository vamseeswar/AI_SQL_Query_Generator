"""
database.py - Database Module
==============================
Handles all SQLite interactions:
  • Creating the sample 'employees.db' with seed data.
  • Retrieving the live schema for the LLM prompt.
  • Executing arbitrary SQL queries safely.
"""

import sqlite3
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# The database file lives in  <project_root>/database/employees.db
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "employees.db"


# ---------------------------------------------------------------------------
# Helper: get a connection (creates the directory if needed)
# ---------------------------------------------------------------------------
def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection to employees.db."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row          # rows behave like dicts
    conn.execute("PRAGMA foreign_keys = ON")  # enforce FK constraints
    return conn


# ---------------------------------------------------------------------------
# Create tables + seed data
# ---------------------------------------------------------------------------
def initialize_database() -> None:
    """
    Create the Departments and Employees tables (if they don't exist)
    and insert sample records.  Safe to call multiple times — uses
    INSERT OR IGNORE so duplicates are silently skipped.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ---- Departments table ------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Departments (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT    NOT NULL UNIQUE
        );
    """)

    # ---- Employees table --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Employees (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            age        INTEGER NOT NULL,
            department TEXT    NOT NULL,
            salary     REAL    NOT NULL
        );
    """)

    # ---- Seed departments -------------------------------------------------
    departments = [
        "HR", "IT", "Finance", "Marketing", "Sales",
        "Engineering", "Operations", "Legal"
    ]
    for dept in departments:
        cursor.execute(
            "INSERT OR IGNORE INTO Departments (department_name) VALUES (?)",
            (dept,),
        )

    # ---- Seed employees (20+ records) -------------------------------------
    employees = [
        ("Alice Johnson",   28, "IT",          72000),
        ("Bob Smith",       35, "HR",          55000),
        ("Charlie Brown",   42, "Finance",     68000),
        ("Diana Prince",    31, "Marketing",   61000),
        ("Edward Norton",   29, "IT",          78000),
        ("Fiona Apple",     38, "Sales",       52000),
        ("George Lucas",    45, "Engineering", 95000),
        ("Hannah Montana",  26, "HR",          48000),
        ("Isaac Newton",    55, "Engineering", 110000),
        ("Julia Roberts",   33, "Marketing",   59000),
        ("Kevin Hart",      40, "Sales",       63000),
        ("Laura Palmer",    27, "IT",          71000),
        ("Michael Scott",   44, "Operations",  67000),
        ("Nancy Drew",      30, "Legal",       74000),
        ("Oscar Wilde",     37, "Finance",     82000),
        ("Patricia Arquette", 34, "HR",        53000),
        ("Quentin Blake",   41, "Engineering", 89000),
        ("Rachel Green",    29, "Marketing",   57000),
        ("Steve Rogers",    36, "IT",          85000),
        ("Tina Turner",     48, "Operations",  70000),
        ("Uma Thurman",     32, "Sales",       60000),
        ("Victor Hugo",     50, "Legal",       92000),
    ]
    cursor.execute("SELECT COUNT(*) FROM Employees")
    if cursor.fetchone()[0] == 0:
        for name, age, dept, salary in employees:
            cursor.execute(
                """INSERT INTO Employees (name, age, department, salary)
                   VALUES (?, ?, ?, ?)""",
                (name, age, dept, salary),
            )

    conn.commit()
    conn.close()
    print(f"Database initialised at {DB_PATH}")


# ---------------------------------------------------------------------------
# Schema introspection (sent to the LLM with every request)
# ---------------------------------------------------------------------------
def get_schema() -> str:
    """
    Read the live schema from employees.db and return it as a
    human-readable string that the LLM can understand.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch all CREATE TABLE statements stored by SQLite
    cursor.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL"
    )
    tables = cursor.fetchall()
    conn.close()

    schema_parts: list[str] = []
    for table in tables:
        schema_parts.append(table["sql"])

    return "\n\n".join(schema_parts)


# ---------------------------------------------------------------------------
# Execute an arbitrary SQL query
# ---------------------------------------------------------------------------
def execute_query(sql: str) -> dict:
    """
    Execute a SQL query against employees.db and return the results.

    Args:
        sql: A valid SQLite SQL statement.

    Returns:
        A dict with keys:
          - success (bool)
          - columns (list[str])   — column names
          - rows    (list[list])  — row data
          - message (str)         — error message on failure
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)

        # SELECT queries return rows; others return row-count info.
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = [list(row) for row in cursor.fetchall()]
        else:
            conn.commit()
            columns = ["affected_rows"]
            rows = [[cursor.rowcount]]

        return {
            "success": True,
            "columns": columns,
            "rows": rows,
            "message": "Query executed successfully.",
        }

    except sqlite3.Error as e:
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "message": f"SQL Error: {str(e)}",
        }

    finally:
        conn.close()
