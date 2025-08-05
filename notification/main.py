from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.database import (
    connect_to_mongo, 
    close_mongo_connection, 
    connect_to_redis, 
    close_redis_connection
)
from config.settings import settings
from models import register_all_models

# Import API routers
from api.auth import router as auth_router
from api.customer import router as customer_router
from api.message import router as message_router
from api.tasks import router as tasks_router
from api.notification import router as notification_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    await connect_to_mongo()
    await connect_to_redis()
    
    # Register all models after database connection
    register_all_models()
    
    print("Application started successfully!")
    
    yield
    
    await close_mongo_connection()
    await close_redis_connection()
    print("Application shutdown complete!")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Chatbot API Backend with TaskIQ, MongoDB, and AI",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(customer_router)
app.include_router(message_router)
app.include_router(tasks_router)
app.include_router(notification_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Chatbot API Backend",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 