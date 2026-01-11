import logging
from typing import Dict
import json

class AITutor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.finance_keywords = {
            "money": ["saving", "spending", "earning", "budgeting", "income"],
            "investment": ["stocks", "bonds", "mutual funds", "portfolio", "diversification"],
            "risk": ["volatility", "market risk", "diversification", "risk management"],
            "technical": ["RSI", "moving average", "support", "resistance", "trend"],
            "fundamental": ["P/E ratio", "earnings", "revenue", "market cap", "valuation"]
        }

    def is_finance_related(self, query: str) -> bool:
        """Check if the query is related to finance"""
        query_lower = query.lower()
        
        # Check direct keywords
        for category, terms in self.finance_keywords.items():
            if category in query_lower or any(term in query_lower for term in terms):
                return True
                
        return False

    def get_response(self, query: str, course_context: str) -> dict:
        """Generate a response to a user query"""
        try:
            # Check if query is finance-related
            if not self.is_finance_related(query):
                return {
                    "response": "I can only answer questions related to finance and the current course material.",
                    "relevant": False
                }

            # Parse course context
            context = json.loads(course_context)
            query_lower = query.lower()
            
            # Find relevant module content
            relevant_content = []
            for module in context.get("modules", []):
                module_content = module.get("content", "").lower()
                if any(keyword in module_content for keyword in query_lower.split()):
                    relevant_content.append(module.get("content"))

            # Generate response based on context and predefined answers
            response = self._generate_contextual_response(query_lower, relevant_content)
            
            return {
                "response": response,
                "relevant": True
            }
            
        except Exception as e:
            self.logger.error(f"Error generating AI response: {str(e)}")
            return {
                "response": "I apologize, but I'm having trouble processing your question. Please try again later.",
                "relevant": False
            }

    def _generate_contextual_response(self, query: str, relevant_content: list) -> str:
        """Generate a contextual response based on the query and available content"""
        # Common financial questions and answers
        qa_pairs = {
            "what is": self._handle_definition_question,
            "how to": self._handle_how_to_question,
            "explain": self._handle_explanation_question,
            "difference between": self._handle_comparison_question
        }
        
        # Find matching question type
        for question_type, handler in qa_pairs.items():
            if question_type in query:
                return handler(query, relevant_content)
        
        # Default response using relevant content
        if relevant_content:
            return f"Based on the course material: {' '.join(relevant_content)}"
        else:
            return "I understand your question is about finance, but I need more specific information to provide a helpful answer."

    def _handle_definition_question(self, query: str, content: list) -> str:
        """Handle 'what is' type questions"""
        definitions = {
            "stock": "A stock represents ownership in a company and a claim on part of that company's earnings and assets.",
            "bond": "A bond is a fixed income instrument that represents a loan made by an investor to a borrower.",
            "mutual fund": "A mutual fund is a company that pools money from many investors and invests it in securities like stocks, bonds, and short-term debt.",
            "dividend": "A dividend is a distribution of profits by a corporation to its shareholders.",
            "market cap": "Market capitalization is the total value of a company's shares of stock."
        }
        
        for term, definition in definitions.items():
            if term in query:
                return definition
                
        return self._get_content_based_response(content)

    def _handle_how_to_question(self, query: str, content: list) -> str:
        """Handle 'how to' type questions"""
        how_to_guides = {
            "invest": "To start investing: 1. Set your goals 2. Determine your risk tolerance 3. Choose your investment strategy 4. Select appropriate investments 5. Monitor and adjust your portfolio",
            "save": "To save effectively: 1. Create a budget 2. Track your expenses 3. Set savings goals 4. Automate your savings 5. Reduce unnecessary expenses",
            "budget": "To create a budget: 1. Calculate your income 2. Track your expenses 3. Set financial goals 4. Create spending categories 5. Monitor and adjust regularly"
        }
        
        for topic, guide in how_to_guides.items():
            if topic in query:
                return guide
                
        return self._get_content_based_response(content)

    def _handle_explanation_question(self, query: str, content: list) -> str:
        """Handle 'explain' type questions"""
        explanations = {
            "risk": "Risk in investing refers to the possibility of losing some or all of your investment. It's often measured by volatility - how much an investment's value changes over time.",
            "diversification": "Diversification is a risk management strategy that involves spreading your investments across different assets to reduce exposure to any single asset or risk.",
            "compound interest": "Compound interest is when you earn interest on both your initial investment and previously earned interest, leading to exponential growth over time."
        }
        
        for topic, explanation in explanations.items():
            if topic in query:
                return explanation
                
        return self._get_content_based_response(content)

    def _handle_comparison_question(self, query: str, content: list) -> str:
        """Handle comparison questions"""
        comparisons = {
            "stocks bonds": "Stocks represent ownership in a company and typically offer higher potential returns with higher risk. Bonds are loans to companies or governments and typically offer lower, more stable returns with lower risk.",
            "saving investing": "Saving typically involves putting money in a safe place with minimal risk and lower returns. Investing involves putting money into assets with the potential for higher returns but also higher risk.",
            "bull bear": "A bull market is when stock prices are rising and market sentiment is optimistic. A bear market is when stock prices are falling and sentiment is pessimistic."
        }
        
        for terms, comparison in comparisons.items():
            if all(term in query for term in terms.split()):
                return comparison
                
        return self._get_content_based_response(content)

    def _get_content_based_response(self, content: list) -> str:
        """Generate a response based on available content"""
        if content:
            return f"Based on the course material: {' '.join(content)}"
        return "I understand your question, but I need more specific information to provide a helpful answer."

# Initialize AI Tutor
try:
    ai_tutor = AITutor()
except Exception as e:
    logging.error(f"Failed to initialize AI Tutor: {str(e)}")
    ai_tutor = None
