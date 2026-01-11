from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from ai_service import ai_service as ai_tutor_service
import uuid
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router without prefix since main.py handles the /api prefix
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = "financial_learning"

@router.post("/chat/tutor")
async def chat(request: Request):
    try:
        # Get the request data
        data = await request.json()
        chat_request = ChatRequest(**data)
        
        # Generate a unique user ID for the session
        user_id = "session_" + str(uuid.uuid4())
        
        # Log incoming request
        logger.info(f"Received chat request - User ID: {user_id}, Context: {chat_request.context}")
        
        try:
            # Generate response using AI service
            response = ai_tutor_service.generate_response(
                user_id=user_id,
                module_content=chat_request.context,
                question=chat_request.message
            )
            
            if not response or not isinstance(response, dict):
                logger.error(f"Invalid response format from AI service: {response}")
                raise HTTPException(
                    status_code=500,
                    detail="Invalid response from AI service"
                )
            
            if response.get('status') == 'error':
                logger.error(f"AI service error: {response.get('message')}")
                raise HTTPException(
                    status_code=500,
                    detail=response.get('message', 'An unexpected error occurred')
                )
            
            # Log successful response
            logger.info(f"Successfully generated response for user {user_id}")
            
            return {
                "response": response.get("message", ""),
                "timestamp": response.get("timestamp", datetime.now().isoformat())
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error generating AI response"
            )
            
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )
