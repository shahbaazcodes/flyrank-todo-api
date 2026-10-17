from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.auth.router import router as auth_router

app = FastAPI(
    title="Supabase Auth & Security Microservice",
    description="Enterprise-grade authentication and token-guard service built with FastAPI, Pydantic v2, and Supabase Auth.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Standardize exception payloads to strictly match {"error": "..."}
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid or missing data fields"}
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


app.include_router(auth_router)


@app.get("/")
def read_root():
    return {
        "service": "Supabase Auth Guard API",
        "status": "online",
        "documentation": "/docs"
    }