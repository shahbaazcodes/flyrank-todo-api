from fastapi import FastAPI, HTTPException, status, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional

app = FastAPI()

# A. Override FastAPI's default 422 handler to return a strict 400 Bad Request
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
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
        return v.strip()  # Automatically trims trailing spaces

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator('title')
    @classmethod
    def clean_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be blank")
        return v.strip() if v is not None else None


# C. Optimized O(1) In-Memory Data Store (Hash Map)
tasks_db = {
    1: {"id": 1, "title": "Complete Stage 1 of FlyRank assignment", "done": True},
    2: {"id": 2, "title": "Build the Read endpoints for Stage 2", "done": False},
    3: {"id": 3, "title": "Crush the technical interview later", "done": False}
}
current_id = 3  # Atomic tracking counter for O(1) ID creation


@app.get("/")
def read_root():
    """Retrieve basic API metadata and entry points."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health_check():
    """Perform a system health check to verify the server is running."""
    return {"status": "ok"}


# D. GET /tasks -> Supports structural pagination (Stretch Goal)
@app.get("/tasks")
def get_all_tasks(limit: int = 10, offset: int = 0):
    """Fetch a paginated slice of the stored tasks collection."""
    task_list = list(tasks_db.values())
    return task_list[offset : offset + limit]

@app.get("/tasks/{id}")
def get_task_by_id(id: int):
    """Retrieve details of a single task using O(1) direct lookup."""
    if id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    return tasks_db[id]

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    """Create a new task with a dynamic counter and append it to the database."""
    global current_id
    current_id += 1
    
    new_task = {"id": current_id, "title": payload.title, "done": False}
    tasks_db[current_id] = new_task
    return new_task

@app.put("/tasks/{id}")
def update_task(id: int, payload: TaskUpdate):
    """Modify parameters of an existing task safely using key matching."""
    if id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
        
    if payload.title is None and payload.done is None:
        raise HTTPException(status_code=400, detail="Bad Request: Body cannot be completely empty")

    if payload.title is not None:
        tasks_db[id]["title"] = payload.title
    if payload.done is not None:
        tasks_db[id]["done"] = payload.done

    return tasks_db[id]

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):
    """Permanently delete a task from the hash map in O(1) constant time."""
    if id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    
    tasks_db.pop(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)