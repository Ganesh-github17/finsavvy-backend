import os
import logging
from typing import Dict, Any
import requests
from datetime import datetime
import json
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from websocket_manager import websocket_manager

# Load environment variables
load_dotenv()

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Google Gemini API configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY environment variable is required")
logger.info("API Key loaded successfully")

class AIService:
    def __init__(self):
        try:
            self.api_key = GEMINI_API_KEY
            if not self.api_key:
                logger.error("No valid API key found in environment")
                raise ValueError("Missing API key. Please check your environment configuration.")

            # Add more detailed logging for API key validation
            logger.info("Attempting to configure Gemini API...")
            try:
                genai.configure(api_key=self.api_key, transport="rest")
                # Initialize with a more stable API version
                generation_config = {
                    "temperature": 0.7,
                    "top_p": 1,
                    "top_k": 1,
                    "max_output_tokens": 2048,
                }
                safety_settings = [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
                
                # List available models first
                available_models = genai.list_models()
                model_found = False
                for model in available_models:
                    logger.info(f"Available model: {model.name}")
                    if "gemini-pro" in model.name:
                        model_found = True
                        break
                
                if not model_found:
                    logger.warning("Gemini Pro model not found in available models")
                    raise ValueError("Gemini Pro model not available")
                
                # Initialize and test with the main model instead of a separate test model
                self.model = genai.GenerativeModel(
                    model_name="models/gemini-1.5-flash",
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                
                # Test with a simple prompt
                test_response = self.model.generate_content('Test')
                if not test_response:
                    raise ValueError("Failed to get response from Gemini API")
                logger.info("Gemini API configured and tested successfully")
            except Exception as api_error:
                logger.error(f"Failed to configure Gemini API: {str(api_error)}")
                raise

            # Initialize the model with the correct API version
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                top_p=1,
                top_k=1,
                max_output_tokens=2048,
                candidate_count=1
            )
            
            # Initialize HuggingFace models
            try:
                logger.info("Initializing HuggingFace fallback model...")
                model_name = "gpt2"  # Using a more reliable and lightweight model
                self.fallback_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.fallback_model = AutoModelForCausalLM.from_pretrained(model_name)
                logger.info("HuggingFace fallback model initialized successfully")
            except Exception as hf_error:
                logger.warning(f"Failed to initialize HuggingFace model: {str(hf_error)}")
                self.fallback_model = None
                self.fallback_tokenizer = None
                # Log detailed error for debugging
                logger.error(f"Detailed HuggingFace error: {str(hf_error)}", exc_info=True)
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
            ]
            self.model = genai.GenerativeModel(
                model_name="models/gemini-1.5-flash",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            self.conversation_history = {}
            logger.info("AITutorService initialized successfully with API key")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {str(e)}")
            raise

    def generate_response(self, user_id: str, module_content: str, question: str) -> Dict[str, Any]:
        """Generate AI response using primary (Gemini) or fallback model"""
        try:
            logger.info(f"Generating response for user {user_id}")
            
            # Get conversation history for this user
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
                logger.debug(f"Created new conversation history for user {user_id}")

            try:
                # Try Gemini first
                if self.api_key and self.api_key != 'your-default-api-key-here':
                    # Prepare the context and prompt
                    context = f"You are a helpful financial tutor. Use the following context to help answer the user's questions: {module_content}"
                    
                    # Create chat history format
                    chat = self.model.start_chat(history=[
                        {"role": "user", "parts": [msg["content"]]}
                        if msg["type"] == "user" else
                        {"role": "model", "parts": [msg["content"]]}
                        for msg in self.conversation_history[user_id][-5:]
                    ])
                    
                    # Generate response
                    response = chat.send_message(f"{context}\n\nUser: {question}")
                    
                    if response and hasattr(response, 'text'):
                        content = response.text
                        model_used = "Gemini"
                    else:
                        raise Exception("Invalid response from Gemini")
                else:
                    raise Exception("Gemini API key not configured")
                    
            except Exception as gemini_error:
                logger.warning(f"Gemini API error, falling back to HuggingFace: {str(gemini_error)}")
                try:
                    # Check if HuggingFace model is available
                    if self.fallback_model and self.fallback_tokenizer:
                        # Prepare input for the model
                        context_prompt = f"Context: {module_content}\nQuestion: {question}\nAnswer:"
                        inputs = self.fallback_tokenizer(context_prompt, return_tensors="pt", truncation=True, max_length=512)
                        
                        # Generate response
                        outputs = self.fallback_model.generate(
                            inputs["input_ids"],
                            max_length=200,
                            num_return_sequences=1,
                            no_repeat_ngram_size=2,
                            temperature=0.7,
                            top_p=0.9,
                            pad_token_id=self.fallback_tokenizer.eos_token_id
                        )
                        
                        # Decode the response
                        content = self.fallback_tokenizer.decode(outputs[0], skip_special_tokens=True)
                        model_used = "HuggingFace"
                    else:
                        raise Exception("HuggingFace model not initialized")
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback model error: {str(fallback_error)}")
                    return self._generate_simulated_response(question, module_content)

            # Create message and update history
            message = {
                'type': 'assistant',
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'model': model_used
            }

            # Update conversation history
            self.conversation_history[user_id].append({
                'type': 'user',
                'content': question,
                'timestamp': datetime.now().isoformat()
            })
            self.conversation_history[user_id].append(message)
            
            # Broadcast the message through WebSocket
            asyncio.create_task(websocket_manager.broadcast_to_user(user_id, {
                'type': 'chat_response',
                'content': content,
                'model': model_used,
                'timestamp': message['timestamp']
            }))
            
            return {
                'status': 'success',
                'message': content,
                'model': model_used,
                'timestamp': message['timestamp']
            }
                
        except Exception as e:
            logger.error(f"Unexpected error in generate_response: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': f'An error occurred while processing your request: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

    def _generate_simulated_response(self, question: str, module_content: str) -> Dict[str, Any]:
        """Generate a simulated response for testing/development"""
        return {
            'status': 'success',
            'message': 'This is a simulated response for testing. Please configure a valid API key for production use.',
            'timestamp': datetime.now().isoformat()
        }

    def get_personalized_recommendations(self, user_id: str, user_progress: Dict[str, Any]) -> Dict[str, Any]:
        """Get personalized learning recommendations based on user progress"""
        try:
            logger.info(f"Generating personalized recommendations for user {user_id}")
            
            # Use Gemini to analyze user progress and generate recommendations
            prompt = f"Based on the user's progress: {json.dumps(user_progress)}, suggest personalized learning recommendations for financial education."
            response = self.model.generate_content(prompt)
            
            # Parse the response and format recommendations
            try:
                suggestions = response.text.split('\n')
                return {
                    'recommendations': [
                        {
                            'module_id': f'mod{i+1}',
                            'title': suggestion.strip(),
                            'reason': 'Based on your learning progress and interests'
                        } for i, suggestion in enumerate(suggestions[:3])
                    ],
                    'learning_path': {
                        'current_focus': 'Personalized Learning Track',
                        'next_steps': suggestions[:3],
                        'estimated_completion': '2 weeks'
                    }
                }
            except Exception as e:
                logger.error(f"Error parsing recommendations: {str(e)}")
                return self._get_default_recommendations()

        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {str(e)}")
            return self._get_default_recommendations()

    def _get_default_recommendations(self) -> Dict[str, Any]:
        return {
            'recommendations': [],
            'learning_path': {
                'current_focus': 'Basic Concepts',
                'next_steps': [],
                'estimated_completion': 'Unknown'
            }
        }

# Create a singleton instance
ai_service = AIService()
