from utils.gemini_langchain import get_gemini_model, get_prompt

def vqar_search(company: str, experience: str):
    """Generate company-specific aptitude questions"""
    
    # Company-specific question focus
    company_focus = {
        "Amazon": "logical reasoning, data interpretation, and analytical thinking with e-commerce scenarios",
        "Google": "mathematical reasoning, pattern recognition, and analytical problems with tech scenarios", 
        "Microsoft": "logical puzzles, quantitative analysis, and problem-solving with software scenarios",
        "TCS": "basic quantitative aptitude, logical reasoning, and verbal ability",
        "Infosys": "mathematical reasoning, logical sequences, and English comprehension",
        "Wipro": "quantitative aptitude, logical reasoning, and verbal reasoning",
        "Accenture": "cognitive abilities, numerical reasoning, and abstract thinking",
        "Cognizant": "quantitative analysis, logical reasoning, and English language skills"
    }
    
    focus_area = company_focus.get(company, "general aptitude covering quantitative, logical, and verbal reasoning")
    
    # Experience-based difficulty
    difficulty_map = {
        "fresher": "beginner to intermediate level",
        "mid": "intermediate to advanced level", 
        "senior": "advanced level with complex problem-solving"
    }
    
    difficulty = difficulty_map.get(experience, "intermediate level")
    
    template = """
    Generate 25 high-quality aptitude questions specifically tailored for {company} placement interviews.
    
    Candidate Profile:
    - Experience Level: {experience} 
    - Target Company: {company}
    - Focus Areas: {focus_area}
    - Difficulty: {difficulty}
    
    Question Distribution:
    - 10 Quantitative Aptitude questions (arithmetic, algebra, geometry, data interpretation)
    - 8 Logical Reasoning questions (patterns, sequences, analytical reasoning)
    - 7 Verbal Ability questions (reading comprehension, grammar, vocabulary)
    
    Requirements:
    - Each question should be clear and unambiguous
    - Include realistic scenarios relevant to {company}'s domain when possible
    - Ensure questions are at {difficulty}
    - Questions should be solvable within 1-2 minutes each
    - Avoid overly complex calculations without calculators
    
    Format each question as:
    Question: [Clear question statement]
    A) [Option 1]
    B) [Option 2] 
    C) [Option 3]
    D) [Option 4]
    Answer: [Correct option letter]
    
    Generate exactly 25 questions following this format.
    """
    
    prompt = get_prompt(template)
    chain = prompt | get_gemini_model()
    
    return chain.invoke({
        "company": company,
        "experience": experience,
        "focus_area": focus_area,
        "difficulty": difficulty
    }).content