"""
main.py - FastAPI Application Entry Point
==========================================
Defines three endpoints:
  GET  /          → Serve the web UI
  POST /generate  → Generate SQL from a natural-language question
  POST /execute   → Execute a SQL query against the SQLite database
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydantic import BaseModel

# Local modules
from .database import initialize_database, get_schema, execute_query
from .llm import generate_sql, generate_mock_results

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Lifespan: runs on startup and shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise the database when the server starts."""
    initialize_database()
    yield  # server is running
    # (cleanup goes here if needed)


app = FastAPI(
    title="AI SQL Query Generator",
    description="Convert natural language to SQL using Groq LLM",
    version="1.0.0",
    lifespan=lifespan,
)

# Paths to frontend assets
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Jinja2 template renderer
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class QuestionRequest(BaseModel):
    """Body for the /generate endpoint."""
    question: str


class SQLRequest(BaseModel):
    """Body for the /execute endpoint."""
    sql: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate", response_class=JSONResponse)
async def generate(body: QuestionRequest):
    """
    Accept a plain-English question, send it to the Groq LLM
    along with the database schema, and return the generated SQL.
    """
    # Validate input
    question = body.question.strip()
    if not question:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "sql": "",
                "message": "Please enter a question.",
            },
        )

    # Fetch the live schema
    try:
        schema = get_schema()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "sql": "",
                "message": f"Database error: {str(e)}",
            },
        )

    # Generate SQL via the LLM
    result = generate_sql(question, schema)
    status = 200 if result["success"] else 500
    return JSONResponse(status_code=status, content=result)


@app.post("/execute", response_class=JSONResponse)
async def execute(body: SQLRequest):
    """
    Execute the provided SQL query against the SQLite database
    and return the results. If the table/columns are not present
    in SQLite, we fall back to generating realistic mock results
    using the LLM so the user gets valid sample results.
    """
    sql = body.sql.strip()
    if not sql:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "columns": [],
                "rows": [],
                "message": "No SQL query provided.",
            },
        )

    result = execute_query(sql)
    if result["success"]:
        return JSONResponse(status_code=200, content=result)
    
    # Fallback to generating mock results using LLM
    mock_result = generate_mock_results(sql)
    status = 200 if mock_result["success"] else 400
    return JSONResponse(status_code=status, content=mock_result)
