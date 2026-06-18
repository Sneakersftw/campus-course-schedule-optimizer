from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import schedules

app = FastAPI(
    title="Campus Course Schedule Optimizer API",
    description="Backend API for generating valid student course schedules.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(schedules.router)


@app.get("/")
def root():
    return {
        "message": "Campus Course Schedule Optimizer API is running."
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "course-schedule-optimizer-backend"
    }