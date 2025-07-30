from agents.vqar_search import vqar_search
from agents.vqar_quiz_formatter import format_quiz
from agents.coding_question_gen import generate_coding
import json
import logging
import os
import re
from dotenv import load_dotenv
from typing import Dict, List, Union, Optional
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class QuestionController:
    """
    Central controller for managing question generation workflows.
    Handles both aptitude (VQAR) and coding questions with proper validation and fallbacks.
    """
    
    def __init__(self, company=None):
        """Initialize with default fallback questions and configuration"""
        # print(f"Initializing QuestionController with company: {company}")
        self.company = company
        self.fallback_vqar = self._create_fallback_vqar_questions()
        self.fallback_coding = self._create_fallback_coding_questions(company or "default")
        self.min_vqar_questions = 5
        self.min_coding_length = 200
        
        
    def generate_questions(self, 
                         company: str, 
                         experience: str, 
                         category: str,
                         num_questions: int = 15) -> Dict[str, Union[str, List]]:
        """
        Main entry point for question generation
        
        Args:
            company: Target company name (e.g., "Google", "Amazon")
            experience: Experience level ("fresher", "mid", "senior")
            category: Question type ("VQAR" or "Coding")
            num_questions: Number of questions to generate (for VQAR)
            
        Returns:
            Dictionary containing:
            - 'status': 'success' or 'error'
            - 'message': Additional information
            - 'questions': Generated questions
            - 'source': 'api' or 'fallback'
        """
        try:
            # Validate inputs
            self._validate_inputs(company, experience, category)
            
            # Check API keys
            if not self._check_required_keys(category):
                return {
                    'status': 'error',
                    'message': 'Missing required API keys',
                    'questions': self._get_fallback(category, company),
                    'source': 'fallback'
                }
            
            # Generate questions
            if category == "VQAR":
                result = self._generate_vqar_questions(company, experience, num_questions)
            else:
                result = self._generate_coding_questions(company, experience)
            
            # Validate and return
            if result['status'] == 'success':
                return result
            return {
                'status': 'error',
                'message': result['message'],
                'questions': self._get_fallback(category, company),
                'source': 'fallback'
            }
            
        except Exception as e:
            logger.error(f"Controller error: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'questions': self._get_fallback(category, company),
                'source': 'fallback'
            }

    def _generate_vqar_questions(self, 
                               company: str, 
                               experience: str,
                               num_questions: int) -> Dict[str, Union[str, List]]:
        """Generate and validate VQAR questions"""
        try:
            # Step 1: Generate raw questions
            raw_questions = vqar_search(company, experience)
            if not raw_questions or len(raw_questions.strip()) < 100:
                return {
                    'status': 'error',
                    'message': 'Insufficient questions generated'
                }
            
            # Step 2: Format to JSON
            formatted = format_quiz(raw_questions)
            questions = json.loads(formatted)
            
            # Step 3: Validate structure
            valid_questions = self._validate_vqar_questions(questions)
            if len(valid_questions) < self.min_vqar_questions:
                return {
                    'status': 'error',
                    'message': f'Only {len(valid_questions)} valid questions generated'
                }
            
            return {
                'status': 'success',
                'message': '',
                'questions': valid_questions[:num_questions],
                'source': 'api'
            }
            
        except json.JSONDecodeError as e:
            return {
                'status': 'error',
                'message': f'JSON parsing error: {str(e)}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def _generate_coding_questions(self,
                                 company: str,
                                 experience: str) -> Dict[str, Union[str, List]]:
        """Generate and validate coding questions"""
        try:
            questions = generate_coding(company, experience)
            # If error returned as a dict
            if isinstance(questions, list) and questions and 'error' in questions[0]:
                return {
                    'status': 'error',
                    'message': questions[0]['error']
                }
            if not questions or len(questions) < 5:
                return {
                    'status': 'error',
                    'message': 'Insufficient coding questions generated'
                }
            # No need to parse further, pass as is
            return {
                'status': 'success',
                'message': '',
                'questions': questions,
                'source': 'api'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def _validate_inputs(self, company: str, experience: str, category: str):
        """Validate all input parameters"""
        valid_companies = ["Amazon", "Google", "Microsoft", "TCS", 
                          "Infosys", "Wipro", "Accenture", "Cognizant"]
        valid_experience = ["fresher", "mid", "senior"]
        valid_categories = ["VQAR", "Coding"]
        
        if company not in valid_companies:
            raise ValueError(f"Invalid company. Must be one of: {valid_companies}")
        if experience not in valid_experience:
            raise ValueError(f"Invalid experience. Must be one of: {valid_experience}")
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {valid_categories}")

    def _check_required_keys(self, category: str) -> bool:
        """Verify required API keys are available"""
        if category == "VQAR":
            return self._has_gemini_key()
        return self._has_tavily_key()

    def _has_gemini_key(self) -> bool:
        """Check for Gemini API key in env or session state"""
        return "GOOGLE_API_KEY" in os.environ or "gemini_api_key" in st.session_state

    def _has_tavily_key(self) -> bool:
        """Check for Tavily API key in env or session state"""
        return "TAVILY_API_KEY" in os.environ or "tavily_api_key" in st.session_state

    def _validate_vqar_questions(self, questions: List) -> List[Dict]:
        """Validate VQAR question structure"""
        valid = []
        for q in questions:
            if (isinstance(q, dict) and 
                q.get('question') and 
                isinstance(q.get('options'), list) and
                len(q['options']) == 4 and
                q.get('answer') in q['options']):
                valid.append({
                    'question': q['question'].strip(),
                    'options': [opt.strip() for opt in q['options']],
                    'answer': q['answer'].strip()
                })
        return valid

    def _parse_coding_questions(self, raw: str) -> List[str]:
        """Parse raw coding questions into individual problems"""
        # Try multiple splitting methods
        delimiters = [r'\n---+\n', r'\n\*\*\*+\n', r'\nProblem \d+:', r'\n\d+\.']
        for delim in delimiters:
            problems = re.split(delim, raw)
            if len(problems) > 1:
                return [p.strip() for p in problems if p.strip()]
        return [raw.strip()]

    def _get_fallback(self, category: str, company: str) -> Union[str, List]:
        """Get appropriate fallback content"""
        if category == "VQAR":
            return json.loads(self.fallback_vqar)
        return self._create_fallback_coding_questions(company)

    @staticmethod
    def _create_fallback_vqar_questions() -> str:
        """Default VQAR questions"""
        questions = [
            {
                "question": "If a train travels 300 km in 5 hours, what's its speed?",
                "options": ["50 km/h", "60 km/h", "70 km/h", "80 km/h"],
                "answer": "60 km/h"
            },
            {
                "question": "A shopkeeper sells an article for Rs. 200 and makes a profit of 25%. What was the cost price?",
                "options": ["Rs. 150", "Rs. 160", "Rs. 180", "Rs. 200"],
                "answer": "Rs. 160"
            },
            {
                "question": "If 15 workers can complete a job in 12 days, how many days will 20 workers take?",
                "options": ["8 days", "9 days", "10 days", "11 days"],
                "answer": "9 days"
            },
            {
                "question": "What comes next in the series: 2, 6, 12, 20, 30, ?",
                "options": ["40", "42", "44", "46"],
                "answer": "42"
            },
            {
                "question": "A rectangle has length 8 cm and breadth 6 cm. What is its area?",
                "options": ["14 cm²", "28 cm²", "48 cm²", "56 cm²"],
                "answer": "48 cm²"
            },
            {
                "question": "If 40% of a number is 80, what is the number?",
                "options": ["160", "180", "200", "220"],
                "answer": "200"
            },
            {
                "question": "A car travels 120 km in 2 hours. What is its speed in m/s?",
                "options": ["16.67 m/s", "20 m/s", "25 m/s", "30 m/s"],
                "answer": "16.67 m/s"
            },
            {
                "question": "What is the average of first 10 natural numbers?",
                "options": ["4.5", "5", "5.5", "6"],
                "answer": "5.5"
            },
            {
                "question": "If 3x + 5 = 20, what is the value of x?",
                "options": ["3", "4", "5", "6"],
                "answer": "5"
            },
            {
                "question": "A circle has radius 7 cm. What is its circumference?",
                "options": ["14π cm", "21π cm", "28π cm", "49π cm"],
                "answer": "14π cm"
            }
        ]
        return json.dumps(questions)

        

    @staticmethod
    def _create_fallback_coding_questions(company: str) -> str:
        """Default coding questions with company context"""
        templates = {
            "Amazon": "Implement a function to process e-commerce orders efficiently. The function should handle order validation, inventory checking, and payment processing.",
            "Google": "Write an algorithm to optimize search results ranking. Consider factors like relevance, user behavior, and content quality.",
            "Microsoft": "Create a function to manage user authentication and authorization in a cloud-based application.",
            "TCS": "Develop a data processing pipeline to handle large volumes of customer data for business intelligence.",
            "Infosys": "Implement a RESTful API service for managing employee information and project assignments.",
            "Wipro": "Create a system to monitor and analyze network performance metrics in real-time.",
            "Accenture": "Design a solution for integrating multiple enterprise systems and data sources.",
            "Cognizant": "Build a web application for managing customer relationships and sales pipeline."
        }
        return templates.get(company, "Solve this programming problem: Implement a function that demonstrates good coding practices and problem-solving skills.")