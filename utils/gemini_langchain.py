import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

def get_gemini_model():
    # Get API key from environment or session state
    api_key = os.getenv("GOOGLE_API_KEY") or st.session_state.get("gemini_api_key")
    
    if not api_key:
        raise ValueError("Gemini API key not found. Please provide one in the sidebar.")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        convert_system_message_to_human=True,
        temperature=0.7
    )

def get_prompt(template: str):
    return ChatPromptTemplate.from_template(template)