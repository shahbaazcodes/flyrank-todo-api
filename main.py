from fastapi import FastAPI, HTTPException

app = FastAPI()

# Your in-memory "database" pre-filled with 3 example tasks
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

# 1. GET /tasks -> Returns the whole list
@app.get("/tasks")
def get_all_tasks():
    return tasks

# 2. GET /tasks/{id} -> Returns a single task using a path parameter
@app.get("/tasks/{id}")
def get_task_by_id(id: int):
    # Search for the task matching the provided ID
    for task in tasks:
        if task["id"] == id:
            return task
            
    # If the loop finishes without finding the ID, throw a machine-readable 404
    raise HTTPException(status_code=404, detail=f"Task {id} not found")