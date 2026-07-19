from fastapi import FastAPI, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional

app = FastAPI(title="Task API", version="1.0")

# Global in-memory storage (Hash Map) and atomic counter
tasks_db = {
    1: {"id": 1, "title": "Setup quarantined environment", "done": True},
    2: {"id": 2, "title": "Analyze AI code choices", "done": False}
}
task_id_counter = 2

# Input Validation Schemas
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Title cannot be empty or whitespace only")
        return stripped

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            stripped = value.strip()
            if not stripped:
                raise ValueError("Title cannot be empty or whitespace only")
            return stripped
        return value

# Override default 422 Unprocessable Entity with a clean 400 Bad Request
@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad Request", "details": exc.errors()}
    )

@app.get("/")
async def get_meta():
    """
    Retrieve system metadata, API naming conventions, and structural endpoints.
    """
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
async def health_check():
    """
    Execute an automated uptime check to confirm backend service status.
    """
    return {"status": "ok"}

@app.get("/tasks")
async def list_tasks(limit: int = 10, offset: int = 0):
    """
    Fetch a targeted paginated slice of all current todo list entries.
    """
    all_tasks = list(tasks_db.values())
    return all_tasks[offset : offset + limit]

@app.get("/tasks/{id}")
async def get_task(id: int):
    """
    Look up details for a specific task using an optimized O(1) key identification.
    """
    if id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    return tasks_db[id]

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """
    Register a new task entry, generate a dynamic ID counter, and default state to incomplete.
    """
    global task_id_counter
    task_id_counter += 1
    new_task = {"id": task_id_counter, "title": task.title, "done": False}
    tasks_db[task_id_counter] = new_task
    return new_task

@app.put("/tasks/{id}")
async def update_task(id: int, task_data: TaskUpdate):
    """
    Evaluate structural changes and apply title edits or state updates to a matching task.
    """
    if id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    
    current_task = tasks_db[id]
    if task_data.title is not None:
        current_task["title"] = task_data.title
    if task_data.done is not None:
        current_task["done"] = task_data.done
        
    return current_task

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int):
    """
    Purge a targeted entry from the primary dict instantly using key matching rules.
    """
    if id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    del tasks_db[id]
    return