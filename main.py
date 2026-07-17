from fastapi import FastAPI

app = FastAPI()

# 1. Root endpoint describing the API
@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

# 2. Professional health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}