import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Response, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional

DB_FILE = "tasks.db"

# --- DATABASE SETUP & IDEMPOTENT SEEDING ---
def get_db():
    """Establishes an active connection to the SQLite database file."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enables dictionary-like row access by column name
    return conn

def init_db():
    """
    Creates the 'tasks.db' file and 'tasks' table automatically if missing.
    Seeds exactly 3 initial tasks ONLY if the database table is completely empty.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
        """)
        
        # Check row count to ensure seed tasks run only once
        cursor.execute("SELECT COUNT(*) FROM tasks")
        row_count = cursor.fetchone()[0]
        
        if row_count == 0:
            initial_tasks = [
                ("Complete Stage 1 of FlyRank assignment", 1),
                ("Build the Read endpoints for Stage 2", 0),
                ("Crush the technical interview later", 0)
            ]
            cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", initial_tasks)
            conn.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager that initializes the SQLite database on app startup."""
    init_db()
    yield

app = FastAPI(title="Task API", version="2.0", lifespan=lifespan)


# A. Override FastAPI's default 422 handler to return a strict 400 Bad Request
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad Request: Invalid or missing data fields"}
    )


# B. Pydantic Models with built-in string cleaning and constraints
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="The title cannot be empty")

    @field_validator('title')
    @classmethod
    def clean_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot consist solely of whitespace")
        return v.strip()

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator('title')
    @classmethod
    def clean_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be blank")
        return v.strip() if v is not None else None


# System Metadata & Health Check Endpoints
@app.get("/")
def read_root():
    """Retrieve basic API metadata and entry points."""
    return {
        "name": "Task API",
        "version": "2.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health_check():
    """Perform a system health check to verify the server is running."""
    return {"status": "ok"}


# D. GET /tasks -> Supports structural pagination using SQL LIMIT & OFFSET
@app.get("/tasks")
def get_all_tasks(limit: int = 10, offset: int = 0):
    """Fetch a paginated slice of tasks from the SQLite database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks LIMIT ? OFFSET ?", (limit, offset))
        rows = cursor.fetchall()
        return [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]

@app.get("/tasks/{id}")
def get_task_by_id(id: int):
    """Retrieve details of a single task using a parameterized SQL query."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Task {id} not found")
        return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    """Create a new task and persist it to SQLite with an auto-incremented ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, 0)", (payload.title,))
        conn.commit()
        new_id = cursor.lastrowid
        return {"id": new_id, "title": payload.title, "done": False}

@app.put("/tasks/{id}")
def update_task(id: int, payload: TaskUpdate):
    """Modify parameters of an existing task safely using parameterized SQL queries."""
    if payload.title is None and payload.done is None:
        raise HTTPException(status_code=400, detail="Bad Request: Body cannot be completely empty")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail=f"Task {id} not found")

        updated_title = existing["title"] if payload.title is None else payload.title
        updated_done = existing["done"] if payload.done is None else (1 if payload.done else 0)

        cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (updated_title, updated_done, id))
        conn.commit()

        return {"id": id, "title": updated_title, "done": bool(updated_done)}

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):
    """Permanently delete a task from SQLite using parameterized deletion."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Task {id} not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)