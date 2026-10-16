from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from starlette.exceptions import HTTPException as StarletteHTTPException

import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the table and seed on startup (safe to run on every start)."""
    db.init_db()
    yield


app = FastAPI(title="Task API", version="3.0", lifespan=lifespan)


# --- Errors: one JSON shape, {"error": "..."}, everywhere ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad Request: Invalid or missing data fields"},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


# --- Models ---
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot consist solely of whitespace")
        return v.strip()


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be blank")
        return v.strip() if v is not None else None


# --- Routes (no SQL here: that all lives in db.py) ---
@app.get("/")
def read_root():
    return {"name": "Task API", "version": "3.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health_check():
    """Reports API status AND whether the database answers SELECT 1."""
    try:
        db.ping()
    except Exception:
        return JSONResponse(status_code=503, content={"status": "error", "db": "down"})
    return {"status": "ok", "db": "ok"}


@app.get("/tasks")
def get_all_tasks(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    return db.list_tasks(limit, offset)


@app.get("/tasks/{id}")
def get_task_by_id(id: int):
    task = db.get_task(id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    return db.create_task(payload.title)


@app.put("/tasks/{id}")
def update_task(id: int, payload: TaskUpdate):
    if payload.title is None and payload.done is None:
        raise HTTPException(status_code=400, detail="Bad Request: Body cannot be completely empty")
    task = db.update_task(id, payload.title, payload.done)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):
    if not db.delete_task(id):
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
