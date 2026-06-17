from fastapi import FastAPI

app = FastAPI(
    title = "Campus Course Schedule Optimizer API",
    description = "Backend API for generating valid student course schedules",
    version = "0.1.0",
)

@app.get("/")
def root():
    return{
        "message": "Campus Course Schedule Optimizer API is running"
    }

@app.get("/health")
def root():
    return{
        "status": "healthy",
        "service": "course-schedule-optimizer-backend"
    }