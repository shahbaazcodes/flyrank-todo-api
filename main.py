from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# A. Define the structural schema for a incoming new task request
class TaskCreate(BaseModel):
    title: str

# B. Override FastAPI's default 422 handler to return a strict 400 Bad Request
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad Request: Missing required title field"}
    )

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

# C. POST /tasks -> Creates a new task and returns a 201 status code
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    # Business rule validation: Check if the string is empty or just blank spaces
    if not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Bad Request: Title cannot be empty"
        )
    
    # Calculate the next available ID dynamically
    next_id = max([t["id"] for t in tasks]) + 1 if tasks else 1
    
    new_task = {
        "id": next_id,
        "title": payload.title,
        "done": False # Default state per spec
    }
    
    tasks.append(new_task)
    return new_task