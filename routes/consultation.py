from fastapi import APIRouter, HTTPException, Request
from typing import Dict
from datetime import datetime
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for consultations (replace with database in production)
consultations = {}

@router.post("/consultation/schedule")
async def schedule_consultation(request: Request):
    """Schedule a consultation and get initial AI analysis"""
    try:
        data = await request.json()
        consultation_id = str(uuid.uuid4())
        
        # Store consultation details
        consultations[consultation_id] = {
            "id": consultation_id,
            "name": data.get("name"),
            "email": data.get("email"),
            "date": data.get("date"),
            "time": data.get("time"),
            "topic": data.get("topic"),
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        # Generate AI response based on consultation topic
        topic = data.get("topic", "").lower()
        
        # Prepare personalized response based on topic keywords
        if "investment" in topic or "portfolio" in topic:
            ai_response = {
                "type": "investment",
                "message": "Based on your interest in investments, I'll prepare a personalized portfolio analysis. We'll discuss investment strategies, risk assessment, and market opportunities during our consultation.",
                "preparation_tips": [
                    "Review your current investment portfolio",
                    "List your financial goals",
                    "Consider your risk tolerance level"
                ]
            }
        elif "budget" in topic or "saving" in topic:
            ai_response = {
                "type": "budget",
                "message": "I'll help you optimize your budget and develop effective saving strategies. We'll analyze your spending patterns and create a personalized savings plan.",
                "preparation_tips": [
                    "Gather your recent bank statements",
                    "List your monthly expenses",
                    "Identify your savings goals"
                ]
            }
        else:
            ai_response = {
                "type": "general",
                "message": "I look forward to our consultation. To make the most of our session, please prepare any specific questions or financial documents you'd like to discuss.",
                "preparation_tips": [
                    "Write down your financial questions",
                    "Gather relevant financial documents",
                    "Think about your short and long-term goals"
                ]
            }
        
        return {
            "consultation_id": consultation_id,
            "status": "scheduled",
            "ai_response": ai_response
        }
        
    except Exception as e:
        logger.error(f"Error scheduling consultation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to schedule consultation")

@router.get("/consultation/{consultation_id}")
async def get_consultation(consultation_id: str):
    """Get consultation details and AI analysis"""
    if consultation_id not in consultations:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return consultations[consultation_id]