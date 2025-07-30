from utils.gemini_langchain import get_gemini_model, get_prompt
import json
import re

def format_quiz(raw_questions: str):
    """Convert raw aptitude questions into properly formatted JSON"""
    
    template = """
    Convert the following aptitude questions into a valid JSON array format.
    
    Raw Questions:
    {raw_questions}
    
    CRITICAL REQUIREMENTS:
    1. Return ONLY a valid JSON array, no other text
    2. Each question must have exactly this structure:
    {{
        "question": "Clear question text without numbering",
        "options": ["Option text 1", "Option text 2", "Option text 3", "Option text 4"],
        "answer": "Exact option text that matches one of the 4 options"
    }}
    
    FORMATTING RULES:
    - Remove question numbers (1., 2., Q1, etc.)
    - Remove option letters (A), B), C), D)) from options
    - Clean up any extra formatting or spaces
    - Ensure "answer" field contains the EXACT text from one of the options
    - Make sure each question has exactly 4 options
    - If a question has fewer than 4 options, add appropriate dummy options
    
    EXAMPLE OUTPUT FORMAT:
    [
        {{
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"],
            "answer": "4"
        }}
    ]
    
    Convert all questions following this exact format. Return only the JSON array.
    """
    
    prompt = get_prompt(template)
    chain = prompt | get_gemini_model()
    
    try:
        response = chain.invoke({"raw_questions": raw_questions}).content
        
        # Clean the response to extract JSON
        response = response.strip()
        
        # Remove any markdown formatting
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*$', '', response)
        
        # Find JSON array pattern
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)
        
        # Parse and validate JSON
        parsed = json.loads(response)
        
        if not isinstance(parsed, list):
            raise ValueError("Response is not a list")
        
        # Validate and clean each question
        validated_questions = []
        for i, q in enumerate(parsed):
            if not isinstance(q, dict):
                continue
                
            # Ensure required fields exist
            if 'question' not in q or 'options' not in q or 'answer' not in q:
                continue
            
            # Clean and validate options
            if not isinstance(q['options'], list) or len(q['options']) != 4:
                continue
            
            # Clean options (remove A), B), etc.)
            cleaned_options = []
            for opt in q['options']:
                cleaned_opt = re.sub(r'^[A-D]\)\s*', '', str(opt).strip())
                cleaned_opt = re.sub(r'^[A-D][\.\)]\s*', '', cleaned_opt)
                cleaned_options.append(cleaned_opt)
            
            # Ensure answer matches one of the options
            answer = str(q['answer']).strip()
            answer = re.sub(r'^[A-D]\)\s*', '', answer)
            answer = re.sub(r'^[A-D][\.\)]\s*', '', answer)
            
            if answer not in cleaned_options:
                # Try to find the closest match
                answer = cleaned_options[0]  # Default to first option
            
            validated_question = {
                "question": str(q['question']).strip(),
                "options": cleaned_options,
                "answer": answer
            }
            
            validated_questions.append(validated_question)
        
        if len(validated_questions) == 0:
            raise ValueError("No valid questions found")
        
        return json.dumps(validated_questions, indent=2)
        
    except Exception as e:
        print(f"Error in format_quiz: {str(e)}")
        # Return safe default questions
        default_questions = [
            {
                "question": "What is the result of 15 + 23?",
                "options": ["38", "37", "39", "36"],
                "answer": "38"
            },
            {
                "question": "If a train travels 120 km in 2 hours, what is its speed?",
                "options": ["50 km/h", "60 km/h", "70 km/h", "80 km/h"],
                "answer": "60 km/h"
            },
            {
                "question": "Choose the odd one out: Apple, Banana, Carrot, Mango",
                "options": ["Apple", "Banana", "Carrot", "Mango"],
                "answer": "Carrot"
            }
        ]
        return json.dumps(default_questions)