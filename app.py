from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Optional, Dict, List
import json
from datetime import datetime, timedelta
import os
import uuid
from dotenv import load_dotenv
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from market_data import MarketDataService
from ai_service import ai_service as ai_tutor_service
from routes import chat, consultation
from course_data import course_library

market_service = MarketDataService()

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(chat.router, prefix="/api")
app.include_router(consultation.router, prefix="/api")
# AI routes only


# Sample course data
courses = {
    "1": {
        "id": "1",
        "title": "Financial Literacy Basics",
        "description": "Learn the fundamentals of financial literacy",
        "modules": [
            {
                "id": "1",
                "title": "Understanding Money",
                "content": "Introduction to money and its role in society",
                "quiz": {
                    "questions": [
                        {
                            "id": "1",
                            "text": "What is money?",
                            "options": ["A medium of exchange", "A store of value", "A unit of account", "All of the above"],
                            "correct": 3
                        }
                    ]
                }
            }
        ]
    }
}

# Certificate generation endpoint
@app.post("/api/courses/{course_id}/modules/{module_id}/certificate")
async def generate_certificate(course_id: str, module_id: str):
    course = course_library.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    module = course_library.get_module(course_id, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    certificate_id = str(uuid.uuid4())
    
    return JSONResponse(content={
        "certificate_id": certificate_id,
        "course": course["title"],
        "module": module["title"],
        "date": datetime.now().isoformat()
    })

# New Course Endpoints
@app.get("/courses")
async def get_courses():
    """Get all available courses"""
    try:
        courses = course_library.get_all_courses()
        return JSONResponse(content=courses)
    except Exception as e:
        logger.error(f"Error fetching courses: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch courses")

@app.get("/courses/{course_id}")
async def get_course_details(course_id: str):
    """Get detailed information about a specific course"""
    try:
        course = course_library.get_course_details(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return JSONResponse(content=course)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching course details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch course details")

@app.get("/courses/{course_id}/modules")
async def get_course_modules(course_id: str):
    """Get all modules for a specific course"""
    try:
        modules = course_library.get_course_modules(course_id)
        if not modules:
            raise HTTPException(status_code=404, detail="Course modules not found")
        return JSONResponse(content=modules)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching course modules: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch course modules")

@app.get("/courses/{course_id}/quizzes")
async def get_course_quizzes(course_id: str):
    """Get all quizzes for a specific course"""
    try:
        quizzes = course_library.get_course_quizzes(course_id)
        if not quizzes:
            raise HTTPException(status_code=404, detail="Course quizzes not found")
        return JSONResponse(content=quizzes)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching course quizzes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch course quizzes")

# Recommendation routes
@app.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    # Simulated personalized recommendations
    recommendations = [
        {
            "id": "1",
            "title": "Financial Literacy Basics",
            "description": "Learn the fundamentals of financial literacy",
            "level": "Beginner",
            "confidence": 0.9
        }
    ]
    return JSONResponse(content=recommendations)

# Market data routes
@app.get("/market/data")
async def get_market_data():
    try:
        market_data = await market_service.get_market_data()
        return JSONResponse(content=market_data)
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch market data")

# AI Tutor Chat routes
@app.post("/api/chat/tutor")
async def chat_with_tutor(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    context = data.get("context", "")
    user_id = str(uuid.uuid4())  # Generate a unique user ID for this session
    
    # Use the AI tutor service to generate response
    response = ai_tutor_service.generate_response(
        user_id=user_id,
        module_content=context,
        question=user_message
    )
    
    return {
        "response": response.get("message", ""),
        "context": context,
        "timestamp": datetime.now().isoformat()
    }

# Collaboration routes
@app.get("/api/study-groups")
async def get_study_groups():
    groups = [
        {
            "id": "1",
            "name": "Investment Basics",
            "description": "Learn fundamental investment concepts together",
            "members": 15,
            "topics": ["Stocks", "Bonds", "ETFs"],
            "next_session": (datetime.now() + timedelta(days=1)).isoformat()
        },
        {
            "id": "2",
            "name": "Trading Strategies",
            "description": "Discuss and practice trading strategies",
            "members": 12,
            "topics": ["Technical Analysis", "Risk Management"],
            "next_session": (datetime.now() + timedelta(days=2)).isoformat()
        }
    ]
    return groups

@app.post("/api/study-groups/{group_id}/join")
async def join_study_group(group_id: str, request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    return {
        "success": True,
        "message": f"Successfully joined group {group_id}",
        "group_id": group_id,
        "user_id": user_id
    }

@app.post("/api/study-groups/{group_id}/messages")
async def post_group_message(group_id: str, request: Request):
    data = await request.json()
    message = data.get("message")
    user_id = data.get("user_id")
    return {
        "id": str(uuid.uuid4()),
        "group_id": group_id,
        "user_id": user_id,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    import socket
    
    def find_available_port(start_port, max_attempts=10):
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('0.0.0.0', port))
                    return port
            except socket.error:
                continue
        raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")
    
    try:
        port = find_available_port(5000)
        logger.info(f"Starting server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise
