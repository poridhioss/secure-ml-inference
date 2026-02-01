from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import logger
from app.middleware.cors import setup_cors
from app.db.session import init_db
from app.routers import auth, users, protected, health, sentiment
import socket
import pickle
import os

# Global variable to store loaded model
sentiment_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for the FastAPI application
    
    Startup:
    - Initialize database tables
    - Load sentiment model
    - Log application startup
    
    Shutdown:
    - Log application shutdown
    """
    global sentiment_model
    
    # Startup
    logger.info(f"Starting FastAPI application - Instance: {settings.INSTANCE_ID}")
    logger.info(f"Hostname: {socket.gethostname()}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
    
    # Load sentiment model
    try:
        model_path = settings.MODEL_PATH
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                sentiment_model = pickle.load(f)
            logger.info(f"Sentiment model loaded successfully from {model_path}")
            logger.info(f"Model type: {type(sentiment_model).__name__}")
        else:
            logger.warning(f"Model file not found at {model_path}")
            logger.warning("Sentiment predictions will not be available!")
    except Exception as e:
        logger.error(f"Failed to load sentiment model: {str(e)}")
        logger.warning("Sentiment predictions will not be available!")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down FastAPI application - Instance: {settings.INSTANCE_ID}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Authentication
    1. Register: POST /api/auth/register
    2. Login: POST /api/auth/login (get JWT token)
    3. Use token in Authorization header: Bearer <token>
    
    ## Prediction
    - Single: POST /api/predict
    - Batch: POST /api/predict/batch
    """,
    lifespan=lifespan
)

# Setup CORS middleware
setup_cors(app)


# Root endpoint
@app.get("/", tags=["Root"])
async def root(request: Request):
    """
    Root endpoint - shows instance information
    
    No authentication required
    """
    return {
        "message": f"Sentiment Analysis API - Instance: {settings.INSTANCE_ID}",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "instance_id": settings.INSTANCE_ID,
        "hostname": socket.gethostname(),
        "model_loaded": sentiment_model is not None,
        "client_ip": request.headers.get("X-Real-IP", request.client.host if request.client else "unknown"),
        "docs_url": "/docs",
        "health_check": "/health"
    }


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(protected.router, prefix="/api")
app.include_router(sentiment.router)  # Sentiment prediction endpoints
app.include_router(health.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "instance_id": settings.INSTANCE_ID,
            "path": str(request.url)
        }
    )


# Custom middleware to log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests
    """
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'} "
        f"[Instance: {settings.INSTANCE_ID}]"
    )
    
    response = await call_next(request)
    
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"[Instance: {settings.INSTANCE_ID}]"
    )
    
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )