from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from app.core.database import Base, engine
import app.models.user
import app.models.log
from app.api import auth, logs, users
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(logs.router, prefix=f"{settings.API_V1_STR}/logs", tags=["Logs"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Log API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": f"{settings.API_V1_STR}/auth",
            "users": f"{settings.API_V1_STR}/users",
            "logs": f"{settings.API_V1_STR}/logs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "log-api"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Fallback handler for uncaught exceptions with consistent response
    return JSONResponse(status_code=500, content={
        "success": False,
        "message": "Internal server error",
        "data": None,
    })

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Normalize HTTPException into unified APIResponse
    detail = exc.detail
    message = detail if isinstance(detail, str) else "Request failed"
    data = None
    if isinstance(detail, list):
        data = {"errors": detail}
    # Customize 404 message
    if exc.status_code == 404 and message == "Not Found":
        message = "Endpoint not found"
    return JSONResponse(status_code=exc.status_code, content={
        "success": False,
        "message": message,
        "data": data,
    })

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Pydantic/validation errors -> unified APIResponse with details
    return JSONResponse(status_code=422, content={
        "success": False,
        "message": "Validation error",
        "data": {"errors": exc.errors()},
    })

# For seeding, use: python -m app.seed