from fastapi import FastAPI, HTTPException, status, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Schema for incoming task creations
class TaskCreate(BaseModel):
    title: str

# Schema for task updates (both fields are optional per request)
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# Override FastAPI's default 422 handler to return a strict 400 Bad Request
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad Request: Invalid or missing data fields"}
    )

# In-memory store
tasks = [
    {"id": 1, "title": "Complete Stage 1 of FlyRank assignment", "done": True},
    {"id": 2, "title": "Build the Read endpoints for Stage 2", "done": False},
    {"id": 3, "title": "Crush the technical interview later", "done": False}
]

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_all_tasks():
    return tasks

@app.get("/tasks/{id}")
def get_task_by_id(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {id} not found")

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="Bad Request: Title cannot be empty")
    
    next_id = max([t["id"] for t in tasks]) + 1 if tasks else 1
    new_task = {"id": next_id, "title": payload.title, "done": False}
    tasks.append(new_task)
    return new_task

# D. PUT /tasks/{id} -> Updates a task's title and/or done status
@app.put("/tasks/{id}")
def update_task(id: int, payload: TaskUpdate):
    # Search for target task
    task_to_update = None
    for task in tasks:
        if task["id"] == id:
            task_to_update = task
            break
            
    if not task_to_update:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    
    # Validation: Ensure client sent at least one field to change
    if payload.title is None and payload.done is None:
        raise HTTPException(status_code=400, detail="Bad Request: Body cannot be completely empty")
        
    # Validation: If title is provided, verify it isn't an empty string
    if payload.title is not None and not payload.title.strip():
        raise HTTPException(status_code=400, detail="Bad Request: Title cannot be blank")

    # Safely apply individual updates
    if payload.title is not None:
        task_to_update["title"] = payload.title
    if payload.done is not None:
        task_to_update["done"] = payload.done

    return task_to_update

# E. DELETE /tasks/{id} -> Removes a task, returns 204 No Content
@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):
    global tasks
    for index, task in enumerate(tasks):
        if task["id"] == id:
            tasks.pop(index)
            # 204 No Content requires returning an empty Response object
            return Response(status_code=status.HTTP_204_NO_CONTENT)
            
    raise HTTPException(status_code=404, detail=f"Task {id} not found")