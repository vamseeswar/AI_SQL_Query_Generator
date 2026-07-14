# ⚡ AI SQL Query Generator

> A high-vibrancy, full-stack AI application that translates natural English questions into structured SQL queries using **Groq (Llama-3.3-70b)**, executes them against a **SQLite** database, and provides **intelligent AI-driven mock fallbacks** for non-schema tables.

[![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq LLM](https://img.shields.io/badge/Groq%20LLM-Llama--3.3--70b-ff6b35?logo=groq&logoColor=white)](https://groq.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Overview

This repository hosts a production-ready, beginner-friendly **AI SQL Query Generator**. The project stands out by utilizing advanced prompt engineering and a robust API pipeline:
1. **Schema Queries**: Queries matching the pre-loaded SQLite database (`Employees` and `Departments`) execute natively on the local SQLite file.
2. **Dynamic Fallback Queries**: For queries targeting tables outside the database schema (e.g. `Teachers`, `Sales`, `Products`), the backend automatically intercepts execution errors and **generates realistic mock column structures and rows on the fly** using the Llama-3.3 model. 

This ensures that the application generates results for **100% of valid prompts**, providing a fully interactive demonstration experience.

```
                  ┌──────────────────────────────┐
                  │  User Questions (English)    │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │    Groq Llama-3.3 LLM        │
                  │   (Translates to SQL)        │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │    FastAPI Backend Server    │
                  └──────────────┬───────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       [Table In Schema]               [Table Outside Schema]
  ┌───────────────────────────┐     ┌───────────────────────────┐
  │   Query Local SQLite      │     │  Trigger LLM Mock Engine  │
  │   (Real Data Results)     │     │  (Dynamic Sample Rows)    │
  └──────────────┬────────────┘     └────────────┬──────────────┘
                 │                               │
                 └───────────────┬───────────────┘
                                 ▼
                  ┌──────────────────────────────┐
                  │   Vibrant Glassmorphic UI    │
                  │     (Dynamic Table render)   │
                  └──────────────────────────────┘
```

---

## ✨ Key Features

* **Natural Language to SQL**: Converts complex English descriptions to optimal SQL queries.
* **Always-Success Result Engine**: Runs SQLite queries locally, but seamlessly catches table-not-found errors to feed a secondary mock generator, ensuring recruiters and users never hit database errors.
* **Premium Glassmorphic UI**: High-vibrancy dark-mode design with glowing card transitions, animated background radial blobs, and custom-styled responsive components.
* **Modular Clean Code Architecture**: Structured cleanly under standard OOP and function separation rules (separated prompts, database seeding, API routing, and AI modules).
* **Instant Clipboard Copying**: Interactive UI buttons to copy code block queries instantly.

---

## 🛠️ Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend** | Python 3.12+, FastAPI, Uvicorn | High-performance async API server |
| **Frontend** | HTML5, CSS3 (Modern custom variables), JavaScript | Dynamic interactive frontend |
| **Database** | SQLite3 | Local storage with preloaded employee schemas |
| **AI SDK** | Groq API (`groq==0.9.0`) | Model: `llama-3.3-70b-versatile` |
| **Templating** | Jinja2 | HTML serving and dynamic variables binding |

---

## 📁 Repository Structure

```
AI_SQL_Query_Generator/
├── backend/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application entrypoint & API routes
│   ├── database.py          # SQLite database connection, seeding, & query executor
│   ├── llm.py               # Groq LLM API client & mock results generator
│   ├── prompts.py           # Structured system prompt instructions
│   ├── requirements.txt     # Python dependencies manifest
│   ├── .env                 # Local variables configuration (gitignored)
│   └── .env.example         # Template file for setting up the Groq key
├── frontend/
│   ├── templates/
│   │   └── index.html       # Main template interface
│   └── static/
│       ├── css/
│       │   └── style.css    # Premium CSS design properties & animations
│       └── js/
│           └── app.js       # Client side application state & API fetch handlers
├── database/
│   └── employees.db         # SQLite DB file (generated at initial boot)
├── .gitignore               # System ignore mappings
└── README.md                # Project documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
* **Python 3.12+** installed on your machine.
* A free **Groq API Key** from [console.groq.com](https://console.groq.com/).

### Step 1 — Clone and Navigate
```bash
git clone https://github.com/yourusername/AI_SQL_Query_Generator.git
cd AI_SQL_Query_Generator
```

### Step 2 — Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS / Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 4 — Configure Credentials
Copy the environment variables template and insert your actual Groq key:
```bash
cp backend/.env.example backend/.env
```
Inside the `backend/.env` file:
```env
GROQ_API_KEY=gsk_EdFa...your_actual_key_here...
```

### Step 5 — Run Application
```bash
python -m uvicorn backend.main:app --reload
```
Once initialized, navigate to: **[http://localhost:8000](http://localhost:8000)**

---

## 💡 Example Prompt Scenarios

The generator works with both pre-seeded data and any general request:

### Real SQLite Schema Queries (Database Tables)
| English Prompt | Expected SQL Output | DB Source |
| :--- | :--- | :--- |
| `"Show all employees"` | `SELECT * FROM Employees` | Native SQLite |
| `"Show IT employees earning over 70000"` | `SELECT * FROM Employees WHERE department = 'IT' AND salary > 70000` | Native SQLite |
| `"Sort all departments by name"` | `SELECT * FROM Departments ORDER BY department_name` | Native SQLite |

### Custom Dynamic Fallback Queries (Generated & Mock-Executed)
| English Prompt | Generated SQL Output | Execution Mode | Result Type |
| :--- | :--- | :--- | :--- |
| `"Show all details from teachers table"` | `SELECT * FROM teachers` | LLM Mock Fallback | Generated columns: `['id', 'name', 'subject', 'email']` + 4 rows of sample records |
| `"Show total sales by product name"` | `SELECT product_name, SUM(sales_amount) FROM Sales GROUP BY product_name` | LLM Mock Fallback | Correct group aggregates e.g. `[['Laptop', 10000], ['Smartphone', 5000]]` |

---

## 🗃️ Built-in SQLite Schema

For native executions, the server initializes `database/employees.db` with the following entities:

### `Employees` Table
* `id` (INTEGER, Primary Key)
* `name` (TEXT)
* `age` (INTEGER)
* `department` (TEXT)
* `salary` (REAL)

### `Departments` Table
* `id` (INTEGER, Primary Key)
* `department_name` (TEXT, Unique)

---

## 🔌 API Endpoints Reference

### 1. `GET /`
* **Description**: Serves the visual web application.
* **Response**: `HTML` template.

### 2. `POST /generate`
* **Description**: Translates natural English question to valid SQL.
* **Payload**:
  ```json
  { "question": "Show all employees older than 40" }
  ```
* **Response**:
  ```json
  {
    "success": true,
    "sql": "SELECT * FROM Employees WHERE age > 40",
    "message": "SQL generated successfully."
  }
  ```

### 3. `POST /execute`
* **Description**: Runs SQL on local database or routes to mock fallback if the table does not exist.
* **Payload**:
  ```json
  { "sql": "SELECT * FROM teachers" }
  ```
* **Response**:
  ```json
  {
    "success": true,
    "columns": ["id", "name", "subject"],
    "rows": [
      [1, "Mr. Anderson", "Chemistry"],
      [2, "Ms. Lovelace", "Computer Science"]
    ],
    "message": "Generated sample results mock (table/columns not present in SQLite database)."
  }
  ```

---

## ⚠️ Exception Safeguards

* **Empty Text Check**: Webpage validates that input query isn't empty before triggering loading animations.
* **Syntax Error Protection**: Returns descriptive prompts if input is non-sensical or unable to translate.
* **SQLite Failover**: Automatically translates database lookup table errors into structural mock data generation.
* **API Offline Safeguard**: If Groq API key is expired or missing, catches the API error and outputs clean warning alerts in the error pane instead of crashing the process.

---

## 📄 License
This project is open-source software licensed under the [MIT License](LICENSE).
