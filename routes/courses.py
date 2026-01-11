from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel

from course_data import course_library

router = APIRouter()

class QuizSubmission(BaseModel):
    answers: Dict[str, int]

@router.get("/courses")
async def get_courses(level: Optional[str] = None) -> List[Dict]:
    """Get all courses or filter by level"""
    return course_library.get_courses(level)

@router.get("/courses/{course_id}")
async def get_course(course_id: str) -> Dict:
    """Get a specific course by ID"""
    return course_library.get_course(course_id)

@router.get("/courses/{course_id}/modules/{module_id}")
async def get_module(course_id: str, module_id: str) -> Dict:
    """Get a specific module from a course"""
    return course_library.get_module(course_id, module_id)

@router.post("/courses/{course_id}/modules/{module_id}/quiz")
async def submit_quiz(
    course_id: str, 
    module_id: str, 
    user_id: str,
    submission: QuizSubmission
) -> Dict:
    """Submit quiz answers and get results"""
    return course_library.submit_quiz(course_id, module_id, user_id, submission.answers)

@router.get("/users/{user_id}/progress")
async def get_user_progress(user_id: str) -> Dict:
    """Get user's course progress"""
    return course_library.get_user_progress(user_id)
