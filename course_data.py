from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class Question(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: int

class Quiz(BaseModel):
    id: str
    title: str
    questions: List[Question]
    time_limit: int  # in minutes

class Lesson(BaseModel):
    id: str
    title: str
    content: str
    duration: str
    video_url: Optional[str] = None

class Module(BaseModel):
    id: str
    title: str
    lessons: List[Lesson]
    quiz: Quiz

class Course(BaseModel):
    id: str
    title: str
    description: str
    level: str
    image: str
    modules: List[Module]
    duration: str

class CourseLibrary:
    def __init__(self):
        self.courses = {
            "fin101": {
                "id": "fin101",
                "title": "Introduction to Financial Markets",
                "description": "Learn the fundamentals of financial markets, including stocks, bonds, and market analysis",
                "level": "Beginner",
                "image": "https://example.com/fin101.jpg",
                "duration": "4 weeks",
                "modules": [
                    {
                        "id": "fin101-m1",
                        "title": "Understanding Stock Markets",
                        "lessons": [
                            {
                                "id": "fin101-l1",
                                "title": "What are Stocks?",
                                "content": """
                                In this lesson, you'll learn:
                                - Definition of stocks and shares
                                - How stock markets work
                                - Types of stock exchanges
                                - Reading stock quotes
                                - Understanding market indices
                                """,
                                "duration": "30 mins",
                                "video_url": "https://example.com/stocks-intro.mp4"
                            },
                            {
                                "id": "fin101-l2",
                                "title": "Stock Market Analysis",
                                "content": """
                                Learn about:
                                - Fundamental analysis
                                - Technical analysis
                                - Market indicators
                                - Trading volumes
                                - Price patterns
                                """,
                                "duration": "45 mins",
                                "video_url": "https://example.com/market-analysis.mp4"
                            }
                        ],
                        "quiz": {
                            "id": "fin101-q1",
                            "title": "Stock Market Basics Quiz",
                            "time_limit": 15,
                            "questions": [
                                {
                                    "id": "q1",
                                    "question": "What does a bull market indicate?",
                                    "options": [
                                        "Falling stock prices",
                                        "Rising stock prices",
                                        "Stable stock prices",
                                        "Market closure"
                                    ],
                                    "correct_answer": 1
                                },
                                {
                                    "id": "q2",
                                    "question": "Which of these is a major stock index?",
                                    "options": [
                                        "NASDAQ",
                                        "LIBOR",
                                        "SWIFT",
                                        "IBAN"
                                    ],
                                    "correct_answer": 0
                                }
                            ]
                        }
                    }
                ]
            },
            "fin201": {
                "id": "fin201",
                "title": "Investment Strategies",
                "description": "Master various investment strategies and portfolio management techniques",
                "level": "Intermediate",
                "image": "https://example.com/fin201.jpg",
                "duration": "6 weeks",
                "modules": [
                    {
                        "id": "fin201-m1",
                        "title": "Portfolio Management",
                        "lessons": [
                            {
                                "id": "fin201-l1",
                                "title": "Portfolio Diversification",
                                "content": """
                                Learn about:
                                - Risk management
                                - Asset allocation
                                - Diversification strategies
                                - Portfolio rebalancing
                                - Risk-return tradeoff
                                """,
                                "duration": "40 mins",
                                "video_url": "https://example.com/portfolio-div.mp4"
                            },
                            {
                                "id": "fin201-l2",
                                "title": "Investment Vehicles",
                                "content": """
                                Explore different investment options:
                                - Mutual funds
                                - ETFs
                                - Bonds
                                - Real estate
                                - Commodities
                                """,
                                "duration": "35 mins",
                                "video_url": "https://example.com/investment-vehicles.mp4"
                            }
                        ],
                        "quiz": {
                            "id": "fin201-q1",
                            "title": "Portfolio Management Quiz",
                            "time_limit": 15,
                            "questions": [
                                {
                                    "id": "q1",
                                    "question": "What is the main benefit of diversification?",
                                    "options": [
                                        "Guaranteed returns",
                                        "Risk reduction",
                                        "Tax benefits",
                                        "Higher returns"
                                    ],
                                    "correct_answer": 1
                                },
                                {
                                    "id": "q2",
                                    "question": "Which investment typically has the highest risk?",
                                    "options": [
                                        "Government bonds",
                                        "Blue-chip stocks",
                                        "Penny stocks",
                                        "Money market funds"
                                    ],
                                    "correct_answer": 2
                                }
                            ]
                        }
                    }
                ]
            },
            "python": {
                "id": "python-101",
                "title": "Python Programming Fundamentals",
                "description": "Learn Python programming from basics to advanced concepts",
                "level": "Beginner",
                "image": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg",
                "duration": "4 weeks",
                "modules": [
                    {
                        "id": "py-mod-1",
                        "title": "Introduction to Python",
                        "lessons": [
                            {
                                "id": "py-les-1",
                                "title": "Getting Started with Python",
                                "content": "Python is a high-level, interpreted programming language...",
                                "duration": "15 mins",
                                "video_url": None
                            },
                            {
                                "id": "py-les-2",
                                "title": "Variables and Data Types",
                                "content": "Learn about Python's basic data types: int, float, str, bool...",
                                "duration": "20 mins",
                                "video_url": None
                            }
                        ],
                        "quiz": {
                            "id": "py-quiz-1",
                            "title": "Python Basics Quiz",
                            "time_limit": 15,
                            "questions": [
                                {
                                    "id": "q1",
                                    "question": "What is the output of print(type(5.0))?",
                                    "options": [
                                        "<class 'int'>",
                                        "<class 'float'>",
                                        "<class 'str'>",
                                        "<class 'number'>"
                                    ],
                                    "correct_answer": 1
                                },
                                {
                                    "id": "q2",
                                    "question": "Which of these is a valid variable name in Python?",
                                    "options": [
                                        "2variable",
                                        "_variable",
                                        "variable-name",
                                        "variable name"
                                    ],
                                    "correct_answer": 1
                                }
                            ]
                        }
                    },
                    {
                        "id": "py-mod-2",
                        "title": "Control Flow",
                        "lessons": [
                            {
                                "id": "py-les-3",
                                "title": "Conditional Statements",
                                "content": "Learn about if, elif, and else statements in Python...",
                                "duration": "25 mins",
                                "video_url": None
                            },
                            {
                                "id": "py-les-4",
                                "title": "Loops in Python",
                                "content": "Understanding for and while loops...",
                                "duration": "30 mins",
                                "video_url": None
                            }
                        ],
                        "quiz": {
                            "id": "py-quiz-2",
                            "title": "Python Control Flow Quiz",
                            "time_limit": 15,
                            "questions": [
                                {
                                    "id": "q1",
                                    "question": "What is the purpose of the break statement in Python?",
                                    "options": [
                                        "To exit a loop",
                                        "To skip a loop iteration",
                                        "To continue a loop",
                                        "To start a loop"
                                    ],
                                    "correct_answer": 0
                                },
                                {
                                    "id": "q2",
                                    "question": "What is the difference between for and while loops?",
                                    "options": [
                                        "For loops are used for arrays, while loops are used for linked lists",
                                        "For loops are used for iteration, while loops are used for recursion",
                                        "For loops are used for iteration, while loops are used for conditional execution",
                                        "For loops are used for conditional execution, while loops are used for iteration"
                                    ],
                                    "correct_answer": 2
                                }
                            ]
                        }
                    }
                ]
            },
            "javascript": {
                "id": "js-101",
                "title": "JavaScript Essentials",
                "description": "Master modern JavaScript programming",
                "level": "Beginner",
                "image": "https://upload.wikimedia.org/wikipedia/commons/6/6a/JavaScript-logo.png",
                "duration": "4 weeks",
                "modules": [
                    {
                        "id": "js-mod-1",
                        "title": "JavaScript Basics",
                        "lessons": [
                            {
                                "id": "js-les-1",
                                "title": "Introduction to JavaScript",
                                "content": "JavaScript is a dynamic programming language...",
                                "duration": "20 mins",
                                "video_url": None
                            },
                            {
                                "id": "js-les-2",
                                "title": "Variables and Data Types",
                                "content": "Understanding var, let, const, and JavaScript data types...",
                                "duration": "25 mins",
                                "video_url": None
                            }
                        ],
                        "quiz": {
                            "id": "js-quiz-1",
                            "title": "JavaScript Basics Quiz",
                            "time_limit": 15,
                            "questions": [
                                {
                                    "id": "q1",
                                    "question": "Which keyword is used to declare a constant in JavaScript?",
                                    "options": [
                                        "var",
                                        "let",
                                        "const",
                                        "final"
                                    ],
                                    "correct_answer": 2
                                },
                                {
                                    "id": "q2",
                                    "question": "What is the output of typeof []?",
                                    "options": [
                                        "array",
                                        "object",
                                        "list",
                                        "undefined"
                                    ],
                                    "correct_answer": 1
                                }
                            ]
                        }
                    },
                    {
                        "id": "js-mod-2",
                        "title": "Functions and Objects",
                        "lessons": [
                            {
                                "id": "js-les-3",
                                "title": "JavaScript Functions",
                                "content": "Learn about function declarations, expressions, and arrow functions...",
                                "duration": "30 mins",
                                "video_url": None
                            },
                            {
                                "id": "js-les-4",
                                "title": "Working with Objects",
                                "content": "Understanding JavaScript objects and prototypes...",
                                "duration": "35 mins",
                                "video_url": None
                            }
                        ],
                        "quiz": {
                            "id": "js-quiz-2",
                            "title": "JavaScript Functions and Objects Quiz",
                            "time_limit": 15,
                            "questions": [
                                {
                                    "id": "q1",
                                    "question": "What is the purpose of the this keyword in JavaScript?",
                                    "options": [
                                        "To refer to the global object",
                                        "To refer to the current object",
                                        "To refer to the parent object",
                                        "To refer to the child object"
                                    ],
                                    "correct_answer": 1
                                },
                                {
                                    "id": "q2",
                                    "question": "What is the difference between null and undefined in JavaScript?",
                                    "options": [
                                        "Null is a primitive value, undefined is an object",
                                        "Null is an object, undefined is a primitive value",
                                        "Null is a primitive value, undefined is a type",
                                        "Null is a type, undefined is a primitive value"
                                    ],
                                    "correct_answer": 0
                                }
                            ]
                        }
                    }
                ]
            },
            "react": {
                "id": "react-101",
                "title": "React Development",
                "description": "Learn modern React development with hooks and best practices",
                "level": "Intermediate",
                "image": "https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg",
                "duration": "6 weeks",
                "modules": [
                    {
                        "id": "react-mod-1",
                        "title": "React Fundamentals",
                        "lessons": [
                            {
                                "id": "react-les-1",
                                "title": "Introduction to React",
                                "content": "Understanding React components and JSX...",
                                "duration": "25 mins",
                                "video_url": None
                            },
                            {
                                "id": "react-les-2",
                                "title": "State and Props",
                                "content": "Managing component state and props in React...",
                                "duration": "30 mins",
                                "video_url": None
                            }
                        ],
                        "quiz": {
                            "id": "react-quiz-1",
                            "title": "React Basics Quiz",
                            "time_limit": 15,
                            "questions": [
                                {
                                    "id": "q1",
                                    "question": "Which hook is used for side effects in React?",
                                    "options": [
                                        "useState",
                                        "useEffect",
                                        "useContext",
                                        "useReducer"
                                    ],
                                    "correct_answer": 1
                                },
                                {
                                    "id": "q2",
                                    "question": "What is the correct way to update state in React?",
                                    "options": [
                                        "this.state.count = 5",
                                        "setState(count = 5)",
                                        "setCount(5)",
                                        "state.count = 5"
                                    ],
                                    "correct_answer": 2
                                }
                            ]
                        }
                    },
                    {
                        "id": "react-mod-2",
                        "title": "React Hooks",
                        "lessons": [
                            {
                                "id": "react-les-3",
                                "title": "useState and useEffect",
                                "content": "Working with React's most common hooks...",
                                "duration": "35 mins",
                                "video_url": None
                            },
                            {
                                "id": "react-les-4",
                                "title": "Custom Hooks",
                                "content": "Creating and using custom React hooks...",
                                "duration": "40 mins",
                                "video_url": None
                            }
                        ],
                        "quiz": {
                            "id": "react-quiz-2",
                            "title": "React Hooks Quiz",
                            "time_limit": 15,
                            "questions": [
                                {
                                    "id": "q1",
                                    "question": "What is the purpose of the useState hook?",
                                    "options": [
                                        "To manage side effects",
                                        "To manage state",
                                        "To manage props",
                                        "To manage context"
                                    ],
                                    "correct_answer": 1
                                },
                                {
                                    "id": "q2",
                                    "question": "What is the difference between useState and useReducer?",
                                    "options": [
                                        "useState is used for simple state, useReducer is used for complex state",
                                        "useState is used for complex state, useReducer is used for simple state",
                                        "useState is used for state, useReducer is used for props",
                                        "useState is used for props, useReducer is used for state"
                                    ],
                                    "correct_answer": 0
                                }
                            ]
                        }
                    }
                ]
            }
        }
        
        # User progress tracking
        self.user_progress = {}
    
    def get_courses(self, level: str = None) -> List[Course]:
        """Get all courses or filter by level"""
        try:
            courses = list(self.courses.values())
            if level:
                courses = [course for course in courses if course["level"].lower() == level.lower()]
            logger.info(f"Returning {len(courses)} courses")
            return courses
        except Exception as e:
            logger.error(f"Error getting courses: {e}")
            return []

    def get_course(self, course_id: str) -> Course:
        """Get a specific course by ID"""
        if course_id not in self.courses:
            raise HTTPException(status_code=404, detail="Course not found")
        return self.courses[course_id]

    def get_module(self, course_id: str, module_id: str) -> Module:
        """Get a specific module from a course"""
        course = self.get_course(course_id)
        for module in course["modules"]:
            if module["id"] == module_id:
                return module
        raise HTTPException(status_code=404, detail="Module not found")

    def submit_quiz(self, course_id: str, module_id: str, user_id: str, answers: Dict[str, int]) -> Dict:
        """Submit quiz answers and get results"""
        module = self.get_module(course_id, module_id)
        quiz = module["quiz"]
        questions = quiz["questions"]
        
        total_questions = len(questions)
        correct_answers = 0
        
        for question in questions:
            question_id = question["id"]
            if question_id in answers and answers[question_id] == question["correct_answer"]:
                correct_answers += 1
        
        score = (correct_answers / total_questions) * 100
        passed = score >= 70  # Pass threshold is 70%
        
        # Update user progress
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        
        if course_id not in self.user_progress[user_id]:
            self.user_progress[user_id][course_id] = {
                "completed": False,
                "score": 0,
                "passed": False
            }
        
        self.user_progress[user_id][course_id]["score"] = max(
            self.user_progress[user_id][course_id]["score"],
            score
        )
        self.user_progress[user_id][course_id]["passed"] = (
            self.user_progress[user_id][course_id]["passed"] or passed
        )
        
        return {
            "score": score,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "passed": passed
        }

    def get_user_progress(self, user_id: str) -> Dict:
        """Get user's course progress"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {
                course_id: {
                    "completed": False,
                    "score": 0,
                    "passed": False
                }
                for course_id in self.courses.keys()
            }
        return self.user_progress[user_id]

# Create a singleton instance
course_library = CourseLibrary()
