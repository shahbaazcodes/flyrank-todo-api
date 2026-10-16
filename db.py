import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Load local .env if available
load_dotenv()

# Fallback default for local execution vs. Docker container
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dev@localhost:5432/tasks")


def get_connection():
    """Establishes a connection to PostgreSQL with dictionary row formatting."""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    """Creates the 'tasks' table if missing and seeds 3 initial tasks if empty."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
            """)
            conn.commit()

            cursor.execute("SELECT COUNT(*) FROM tasks")
            row = cursor.fetchone()
            row_count = row["count"] if isinstance(row, dict) else row[0]

            if row_count == 0:
                initial_tasks = [
                    ("Complete Stage 1 of FlyRank assignment", True),
                    ("Build the Read endpoints for Stage 2", False),
                    ("Crush the technical interview later", False)
                ]
                cursor.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)", 
                    initial_tasks
                )
                conn.commit()


def ping():
    """Verifies database availability for health checks."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")


def list_tasks(limit: int, offset: int):
    """Retrieves a paginated list of tasks."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done FROM tasks ORDER BY id ASC LIMIT %s OFFSET %s",
                (limit, offset)
            )
            return cursor.fetchall()


def get_task(task_id: int):
    """Retrieves a single task by ID."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
            return cursor.fetchone()


def create_task(title: str):
    """Inserts a new task and returns the inserted row."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
                (title, False)
            )
            new_task = cursor.fetchone()
            conn.commit()
            return new_task


def update_task(task_id: int, title: str | None, done: bool | None):
    """Updates an existing task safely."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
            existing = cursor.fetchone()
            if not existing:
                return None

            updated_title = existing["title"] if title is None else title
            updated_done = existing["done"] if done is None else done

            cursor.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
                (updated_title, updated_done, task_id)
            )
            updated_task = cursor.fetchone()
            conn.commit()
            return updated_task


def delete_task(task_id: int) -> bool:
    """Deletes a task by ID. Returns True if deleted, False if not found."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            conn.commit()
            return cursor.rowcount > 0