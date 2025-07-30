from typing import List, Dict
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_tavily_search(query: str, api_key: str) -> List[Dict]:
    """Fetch search results from Tavily API"""
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "include_answer": True,
        "include_raw_content": True,
        "max_results": 5
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        print(f"Error fetching from Tavily: {str(e)}")
        return []

def generate_coding(company: str, experience: str) -> str:
    """Generate company-specific coding questions using Tavily API"""
    # Get API key from environment or session state
    tavily_api_key = os.getenv("TAVILY_API_KEY") or st.session_state.get("tavily_api_key")
    
    if not tavily_api_key:
        return "Please provide a Tavily API key in the sidebar to fetch coding questions."
    
    # Company-specific search queries
    company_queries = {
        "Amazon": f"site:leetcode.com Amazon coding interview questions {experience} level",
        "Google": f"site:leetcode.com Google coding interview questions {experience} level",
        "Microsoft": f"site:leetcode.com Microsoft coding interview questions {experience} level",
        "TCS": f"site:geeksforgeeks.org TCS coding interview questions {experience} level",
        "Infosys": f"site:geeksforgeeks.org Infosys coding interview questions {experience} level",
        "Wipro": f"site:geeksforgeeks.org Wipro coding interview questions {experience} level",
        "Accenture": f"site:geeksforgeeks.org Accenture coding interview questions {experience} level",
        "Cognizant": f"site:geeksforgeeks.org Cognizant coding interview questions {experience} level"
    }
    
    query = company_queries.get(company, f"site:leetcode.com {company} coding interview questions")
    results = fetch_tavily_search(query, tavily_api_key)
    
    if not results:
        return "Failed to fetch questions. Please check your API key or try again later."
    
    # Format the results into a clean output
    output = []
    for i, result in enumerate(results[:5], 1):
        output.append(f"""
**Problem {i}: {result.get('title', 'Coding Problem')}**

**Source:** [{result.get('url', '')}]({result.get('url', '')})

**Content:**
{result.get('content', 'No content available')}

---
""")
    
    return "\n".join(output)