from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import logging
from datetime import datetime
from .course_data import course_library

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FinLearn Pro API")

# Configure CORS to allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request path: {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

@app.get("/api/courses")
async def get_courses(level: str = None):
    """Get all courses or filter by level"""
    return course_library.get_courses(level)

@app.get("/api/courses/{course_id}")
async def get_course(course_id: str):
    """Get a specific course by ID"""
    return course_library.get_course(course_id)

@app.get("/api/courses/{course_id}/modules/{module_id}")
async def get_module(course_id: str, module_id: str):
    """Get a specific module from a course"""
    return course_library.get_module(course_id, module_id)

@app.post("/api/courses/{course_id}/modules/{module_id}/quiz")
async def submit_quiz(course_id: str, module_id: str, user_id: str, answers: Dict[str, int]):
    """Submit quiz answers and get results"""
    return course_library.submit_quiz(course_id, module_id, user_id, answers)

@app.get("/api/users/{user_id}/progress")
async def get_user_progress(user_id: str):
    """Get user's course progress"""
    return course_library.get_user_progress(user_id)

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
