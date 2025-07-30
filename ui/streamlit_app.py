import streamlit as st
from agents.controller import QuestionController  
import json
import time
import re
from typing import Dict
import logging
logging.basicConfig(
    level=logging.INFO,
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Fetch company-specific problems (mock) ---
def fetch_company_problems(company):
    """
    Mock function to fetch company-specific problems.
    Replace this with your actual Tavily or other API call.
    """
    problems_db = {
        "Amazon": [
            {'title': 'Two Sum', 'url': 'https://leetcode.com/problems/two-sum/'},
            {'title': 'Longest Substring Without Repeating Characters', 'url': 'https://leetcode.com/problems/longest-substring-without-repeating-characters/'},
            {'title': 'Median of Two Sorted Arrays', 'url': 'https://leetcode.com/problems/median-of-two-sorted-arrays/'},
            {'title': 'Merge Intervals', 'url': 'https://leetcode.com/problems/merge-intervals/'},
            {'title': 'Valid Parentheses', 'url': 'https://leetcode.com/problems/valid-parentheses/'},
            {'title': 'Search in Rotated Sorted Array', 'url': 'https://leetcode.com/problems/search-in-rotated-sorted-array/'},
            {'title': 'Trapping Rain Water', 'url': 'https://leetcode.com/problems/trapping-rain-water/'},
            {'title': 'Word Ladder', 'url': 'https://leetcode.com/problems/word-ladder/'},
            {'title': 'Minimum Window Substring', 'url': 'https://leetcode.com/problems/minimum-window-substring/'},
            {'title': 'LRU Cache', 'url': 'https://leetcode.com/problems/lru-cache/'},
            {'title': 'Course Schedule', 'url': 'https://leetcode.com/problems/course-schedule/'},
            {'title': 'Clone Graph', 'url': 'https://leetcode.com/problems/clone-graph/'},
            {'title': 'Number of Islands', 'url': 'https://leetcode.com/problems/number-of-islands/'},
            {'title': 'Kth Largest Element in an Array', 'url': 'https://leetcode.com/problems/kth-largest-element-in-an-array/'},
            {'title': 'Product of Array Except Self', 'url': 'https://leetcode.com/problems/product-of-array-except-self/'},
            {'title': 'Find Minimum in Rotated Sorted Array', 'url': 'https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/'},
            {'title': 'Maximum Subarray', 'url': 'https://leetcode.com/problems/maximum-subarray/'},
            {'title': 'Binary Tree Maximum Path Sum', 'url': 'https://leetcode.com/problems/binary-tree-maximum-path-sum/'},
            {'title': 'Serialize and Deserialize Binary Tree', 'url': 'https://leetcode.com/problems/serialize-and-deserialize-binary-tree/'},
            {'title': 'Subsets', 'url': 'https://leetcode.com/problems/subsets/'}
        ],
        "Wipro": [
            {'title': 'Find Peak Element', 'url': 'https://leetcode.com/problems/find-peak-element/'},
            {'title': 'Reverse Linked List', 'url': 'https://leetcode.com/problems/reverse-linked-list/'},
            {'title': 'Intersection of Two Linked Lists', 'url': 'https://leetcode.com/problems/intersection-of-two-linked-lists/'},
            {'title': 'Remove Nth Node From End of List', 'url': 'https://leetcode.com/problems/remove-nth-node-from-end-of-list/'},
            {'title': 'Linked List Cycle', 'url': 'https://leetcode.com/problems/linked-list-cycle/'},
            {'title': 'Binary Tree Inorder Traversal', 'url': 'https://leetcode.com/problems/binary-tree-inorder-traversal/'},
            {'title': 'Validate Binary Search Tree', 'url': 'https://leetcode.com/problems/validate-binary-search-tree/'},
            {'title': 'Symmetric Tree', 'url': 'https://leetcode.com/problems/symmetric-tree/'},
            {'title': 'Maximum Depth of Binary Tree', 'url': 'https://leetcode.com/problems/maximum-depth-of-binary-tree/'},
            {'title': 'Same Tree', 'url': 'https://leetcode.com/problems/same-tree/'},
            {'title': 'Invert Binary Tree', 'url': 'https://leetcode.com/problems/invert-binary-tree/'},
            {'title': 'Path Sum', 'url': 'https://leetcode.com/problems/path-sum/'},
            {'title': 'Best Time to Buy and Sell Stock', 'url': 'https://leetcode.com/problems/best-time-to-buy-and-sell-stock/'},
            {'title': 'Valid Anagram', 'url': 'https://leetcode.com/problems/valid-anagram/'},
            {'title': 'Group Anagrams', 'url': 'https://leetcode.com/problems/group-anagrams/'},
            {'title': 'Minimum Depth of Binary Tree', 'url': 'https://leetcode.com/problems/minimum-depth-of-binary-tree/'},
            {'title': 'Balanced Binary Tree', 'url': 'https://leetcode.com/problems/balanced-binary-tree/'},
            {'title': 'Convert Sorted Array to Binary Search Tree', 'url': 'https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/'},
            {'title': 'Pascal’s Triangle', 'url': 'https://leetcode.com/problems/pascals-triangle/'},
            {'title': 'Pascal’s Triangle II', 'url': 'https://leetcode.com/problems/pascals-triangle-ii/'}
        ]
        # Add more companies as needed
    }
    # Default fallback
    return {"questions": problems_db.get(company, problems_db["Amazon"])}

# Configure page
st.set_page_config(
    page_title="AI Placement Agent",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for better UI
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .stRadio > div {
        flex-direction: column;
    }
    .stRadio [role=radiogroup] label {
        margin-bottom: 10px;
    }
    .question-card {
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        margin-bottom: 25px;
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border: 1px solid #e3e6ea;
    }
    .question-card h3 {
        color: #2c3e50;
        margin-bottom: 20px;
        font-weight: 600;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    .question-card h4 {
        color: #2c3e50;
        font-weight: 500;
        line-height: 1.6;
        font-size: 1.1em;
    }
    .debug-info {
        font-family: monospace;
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        font-size: 0.85em;
        border: 1px solid #dee2e6;
    }
    .coding-problem {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #007bff;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        position: relative;
    }
    .coding-problem::before {
        content: "💻";
        position: absolute;
        top: 15px;
        right: 20px;
        font-size: 24px;
    }
    .coding-problem-text {
        color: #2c3e50 !important;
        line-height: 1.7;
        font-size: 1.05em;
        font-weight: 400;
        margin-bottom: 15px;
    }
    .concept-tags {
        margin: 15px 0;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    .concept-tag {
        background: linear-gradient(45deg, #3498db, #2980b9);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 500;
        display: inline-block;
    }
    .difficulty-badge {
        display: inline-block;
        padding: 6px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9em;
        margin: 10px 0;
    }
    .difficulty-easy {
        background: linear-gradient(45deg, #27ae60, #2ecc71);
        color: white;
    }
    .difficulty-medium {
        background: linear-gradient(45deg, #f39c12, #e67e22);
        color: white;
    }
    .difficulty-hard {
        background: linear-gradient(45deg, #e74c3c, #c0392b);
        color: white;
    }
    .leetcode-links {
        background: linear-gradient(145deg, #ecf0f1, #bdc3c7);
        padding: 20px;
        border-radius: 12px;
        margin-top: 15px;
        border: 1px solid #95a5a6;
    }
    .leetcode-links h4 {
        color: #2c3e50;
        margin-bottom: 15px;
        font-size: 1.1em;
        font-weight: 600;
    }
    .problem-link {
        display: inline-block;
        padding: 10px 20px;
        background: linear-gradient(45deg, #3498db, #2980b9);
        color: white !important;
        text-decoration: none;
        border-radius: 25px;
        font-weight: 500;
        margin: 5px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .problem-link:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        text-decoration: none;
        color: white !important;
    }
    .score-section {
        background: linear-gradient(145deg, #e8f5e8, #d4edda);
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #28a745;
        margin: 20px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .answer-review {
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    }
    .welcome-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
    }
    .welcome-section h3 {
        color: white;
        margin-bottom: 20px;
    }
    .tip-box {
        background: linear-gradient(145deg, #fff3cd, #fef2c0);
        border: 1px solid #f0ad4e;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Enhanced LeetCode problem mappings with more specific problems
LEETCODE_PROBLEM_MAP = {
    # Array and String Problems
    "two sum": "two-sum",
    "array sum": "two-sum",
    "pair sum": "two-sum",
    "add two numbers": "add-two-numbers",
    "longest substring": "longest-substring-without-repeating-characters",
    "substring": "longest-substring-without-repeating-characters",
    "median two sorted arrays": "median-of-two-sorted-arrays",
    "median": "median-of-two-sorted-arrays",
    "reverse string": "reverse-string",
    "string reverse": "reverse-string",
    "palindrome": "valid-palindrome",
    "palindromic": "valid-palindrome",
    "anagram": "valid-anagram",
    "anagrams": "group-anagrams",
    "group anagrams": "group-anagrams",
    "maximum subarray": "maximum-subarray",
    "max subarray": "maximum-subarray",
    "kadane": "maximum-subarray",
    "product except self": "product-of-array-except-self",
    "product array": "product-of-array-except-self",
    "container water": "container-with-most-water",
    "water container": "container-with-most-water",
    "3sum": "3sum",
    "three sum": "3sum",
    "trapping rain water": "trapping-rain-water",
    "rain water": "trapping-rain-water",
    
    # Linked List Problems
    "reverse linked list": "reverse-linked-list",
    "linked list reverse": "reverse-linked-list",
    "merge two sorted lists": "merge-two-sorted-lists",
    "merge sorted": "merge-two-sorted-lists",
    "linked list cycle": "linked-list-cycle",
    "cycle detection": "linked-list-cycle",
    "remove nth node": "remove-nth-node-from-end-of-list",
    "nth node": "remove-nth-node-from-end-of-list",
    "intersection two linked lists": "intersection-of-two-linked-lists",
    "linked list intersection": "intersection-of-two-linked-lists",
    
    # Tree Problems
    "binary tree inorder": "binary-tree-inorder-traversal",
    "inorder traversal": "binary-tree-inorder-traversal",
    "binary tree preorder": "binary-tree-preorder-traversal",
    "preorder traversal": "binary-tree-preorder-traversal",
    "binary tree postorder": "binary-tree-postorder-traversal",
    "postorder traversal": "binary-tree-postorder-traversal",
    "maximum depth": "maximum-depth-of-binary-tree",
    "tree depth": "maximum-depth-of-binary-tree",
    "validate bst": "validate-binary-search-tree",
    "binary search tree": "validate-binary-search-tree",
    "symmetric tree": "symmetric-tree",
    "tree symmetric": "symmetric-tree",
    "binary tree level order": "binary-tree-level-order-traversal",
    "level order": "binary-tree-level-order-traversal",
    "path sum": "path-sum",
    "tree path": "path-sum",
    "lowest common ancestor": "lowest-common-ancestor-of-a-binary-tree",
    "lca": "lowest-common-ancestor-of-a-binary-tree",
    
    # Dynamic Programming
    "climbing stairs": "climbing-stairs",
    "stairs": "climbing-stairs",
    "fibonacci": "fibonacci-number",
    "fib": "fibonacci-number",
    "coin change": "coin-change",
    "coins": "coin-change",
    "longest increasing subsequence": "longest-increasing-subsequence",
    "lis": "longest-increasing-subsequence",
    "edit distance": "edit-distance",
    "levenshtein": "edit-distance",
    "house robber": "house-robber",
    "robber": "house-robber",
    "knapsack": "partition-equal-subset-sum",
    "0/1 knapsack": "partition-equal-subset-sum",
    "subset sum": "partition-equal-subset-sum",
    
    # Graph Problems
    "number of islands": "number-of-islands",
    "islands": "number-of-islands",
    "course schedule": "course-schedule",
    "topological sort": "course-schedule",
    "clone graph": "clone-graph",
    "graph clone": "clone-graph",
    "word ladder": "word-ladder",
    "ladder": "word-ladder",
    "network delay time": "network-delay-time",
    "shortest path": "network-delay-time",
    
    # Sorting and Searching
    "merge sort": "sort-an-array",
    "mergesort": "sort-an-array",
    "quick sort": "sort-an-array",
    "quicksort": "sort-an-array",
    "heap sort": "sort-an-array",
    "binary search": "binary-search",
    "search": "binary-search",
    "search rotated array": "search-in-rotated-sorted-array",
    "rotated array": "search-in-rotated-sorted-array",
    "find peak element": "find-peak-element",
    "peak element": "find-peak-element",
    "search 2d matrix": "search-a-2d-matrix",
    "2d matrix": "search-a-2d-matrix",
    
    # Stack and Queue
    "valid parentheses": "valid-parentheses",
    "parentheses": "valid-parentheses",
    "brackets": "valid-parentheses",
    "implement queue using stacks": "implement-queue-using-stacks",
    "queue using stacks": "implement-queue-using-stacks",
    "implement stack using queues": "implement-stack-using-queues",
    "stack using queues": "implement-stack-using-queues",
    "min stack": "min-stack",
    "minimum stack": "min-stack",
    "evaluate reverse polish": "evaluate-reverse-polish-notation",
    "reverse polish": "evaluate-reverse-polish-notation",
    "rpn": "evaluate-reverse-polish-notation",
    
    # Hash Table
    "group anagrams": "group-anagrams",
    "top k frequent": "top-k-frequent-elements",
    "k frequent": "top-k-frequent-elements",
    "longest consecutive": "longest-consecutive-sequence",
    "consecutive sequence": "longest-consecutive-sequence",
    
    # Math and Bit Manipulation
    "reverse integer": "reverse-integer",
    "integer reverse": "reverse-integer",
    "palindrome number": "palindrome-number",
    "number palindrome": "palindrome-number",
    "power of two": "power-of-two",
    "power 2": "power-of-two",
    "single number": "single-number",
    "missing number": "missing-number",
    "counting bits": "counting-bits",
    "bit counting": "counting-bits"
}

# Initialize session state
def init_session_state():
    if "quiz" not in st.session_state:
        st.session_state.quiz = {
            "questions": [],
            "current": 0,
            "score": 0,
            "answers": [],
            "done": False,
            "generated": False,
            "start_time": None,
            "raw_response": None
        }
    
    # Initialize category state to ensure proper page switching
    if "current_category" not in st.session_state:
        st.session_state.current_category = None

# Helper function to clean and parse JSON
def parse_quiz_response(response: str):
    try:
        # Try direct JSON parsing first
        return json.loads(response)
    except json.JSONDecodeError:
        try:
            # Look for JSON in code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Look for JSON array pattern
            json_match = re.search(r'\[\s*{.*?}\s*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            # Clean common formatting issues
            cleaned = response.strip()
            cleaned = re.sub(r'^[^[{]*', '', cleaned)  # Remove text before JSON
            cleaned = re.sub(r'[^}\]]*$', '', cleaned)  # Remove text after JSON
            
            return json.loads(cleaned)
        except Exception as e:
            st.error(f"Failed to parse response: {str(e)}")
            return None

def handle_answer(selected: str, question: Dict):
    quiz = st.session_state.quiz
    is_correct = (selected == question["answer"])
    
    quiz["answers"].append({
        "question": question["question"],
        "selected": selected,
        "correct": question["answer"],
        "result": is_correct
    })
    
    if is_correct:
        quiz["score"] += 1
    
    if quiz["current"] + 1 < len(quiz["questions"]):
        quiz["current"] += 1
    else:
        quiz["done"] = True
    
    st.rerun()

def show_results():
    quiz = st.session_state.quiz
    time_taken = int(time.time() - quiz["start_time"])
    
    score_percentage = round(quiz['score']/len(quiz['questions'])*100)
    
    # Performance analysis
    if score_percentage >= 80:
        performance = "🎉 Excellent! You're well prepared."
        color = "#28a745"
    elif score_percentage >= 60:
        performance = "👍 Good work! Some areas need improvement."
        color = "#17a2b8"
    else:
        performance = "📚 Keep studying! Focus on weak areas."
        color = "#ffc107"
    
    st.markdown(f"""
    <div class="score-section">
        <h2 style="color: #2c3e50; margin-bottom: 20px;">🎉 Quiz Complete!</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
            <div class="metric-card">
                <h3 style="color: {color}; margin: 0;">Score</h3>
                <p style="font-size: 1.5em; font-weight: bold; margin: 10px 0; color: #2c3e50;">{quiz['score']}/{len(quiz['questions'])}</p>
                <p style="color: #6c757d; margin: 0;">({score_percentage}%)</p>
            </div>
            <div class="metric-card">
                <h3 style="color: #007bff; margin: 0;">Time Taken</h3>
                <p style="font-size: 1.5em; font-weight: bold; margin: 10px 0; color: #2c3e50;">{time_taken // 60}m {time_taken % 60}s</p>
            </div>
            <div class="metric-card">
                <h3 style="color: #28a745; margin: 0;">Performance</h3>
                <p style="font-size: 1.1em; font-weight: 500; margin: 10px 0; color: #2c3e50;">{performance.split('!')[0]}!</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Detailed Review")
    
    for i, ans in enumerate(quiz["answers"]):
        with st.expander(f"Q{i+1}: {ans['question'][:80]}{'...' if len(ans['question']) > 80 else ''}", expanded=False):
            st.markdown(f"""
            <div class="answer-review">
                <h4 style="color: #2c3e50; margin-bottom: 15px;">{ans['question']}</h4>
                <div style="margin: 10px 0;">
                    <strong>Your answer:</strong> 
                    <span style="color: {'#28a745' if ans['result'] else '#dc3545'}; font-weight: 500;">
                        {ans['selected']} {'✅' if ans['result'] else '❌'}
                    </span>
                </div>
                <div style="margin: 10px 0;">
                    <strong>Correct answer:</strong> 
                    <span style="color: #28a745; font-weight: 500;">{ans['correct']} ✅</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Restart Quiz", use_container_width=True):
            init_session_state()
            st.rerun()
    
    with col2:
        if st.button("🎯 Generate New Questions", use_container_width=True):
            st.session_state.quiz["generated"] = False
            st.rerun()

           

def render_aptitude_quiz():
    quiz = st.session_state.quiz
    
    if not quiz["questions"]:
        st.warning("No questions available. Please generate questions first.")
        return
    
    if not quiz["done"]:
        current_q = quiz["questions"][quiz["current"]]
        
        # Progress bar at top
        progress = (quiz["current"] + 1) / len(quiz["questions"])
        st.progress(progress, text=f"Question {quiz['current'] + 1} of {len(quiz['questions'])}")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div class="question-card">
                <h3>Question {quiz['current'] + 1} of {len(quiz['questions'])}</h3>
                <h4>{current_q['question']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Options as radio buttons
            selected = st.radio(
                "**Select your answer:**",
                current_q["options"],
                key=f"q_{quiz['current']}",
                index=None
            )
            
            col3, col4 = st.columns([1, 3])
            with col3:
                if st.button("Submit Answer", disabled=selected is None, use_container_width=True, type="primary"):
                    handle_answer(selected, current_q)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h4 style="color: #007bff; margin-bottom: 15px;">📊 Progress</h4>
            </div>
            """, unsafe_allow_html=True)
            
            if quiz["start_time"]:
                time_elapsed = int(time.time() - quiz["start_time"])
                st.metric("⏱️ Time", f"{time_elapsed // 60}:{time_elapsed % 60:02d}")
            
            # Question navigation
            answered = len(quiz["answers"])
            st.metric("✅ Answered", f"{answered}/{len(quiz['questions'])}")
            st.metric("🎯 Remaining", f"{len(quiz['questions']) - answered}")
    else:
        show_results()

def find_leetcode_problem(problem_text):
    """Find the most relevant LeetCode problem based on the problem text"""
    problem_text_lower = problem_text.lower()
    
    # Check for exact matches first with enhanced scoring
    best_match = None
    best_score = 0
    
    for keyword, leetcode_slug in LEETCODE_PROBLEM_MAP.items():
        if keyword in problem_text_lower:
            # Score based on keyword length and position
            score = len(keyword)
            if problem_text_lower.startswith(keyword):
                score += 10  # Bonus for starting with keyword
            if score > best_score:
                best_score = score
                best_match = leetcode_slug
    
    if best_match:
        return f"https://leetcode.com/problems/{best_match}/"
    
    # Enhanced fallback patterns for common problem types
    if any(word in problem_text_lower for word in ["array", "sum", "two"]):
        return "https://leetcode.com/problems/two-sum/"
    elif any(word in problem_text_lower for word in ["linked", "list", "node"]):
        return "https://leetcode.com/problems/reverse-linked-list/"
    elif any(word in problem_text_lower for word in ["tree", "binary", "traversal"]):
        return "https://leetcode.com/problems/binary-tree-inorder-traversal/"
    elif any(word in problem_text_lower for word in ["sort", "merge", "quick", "heap"]):
        return "https://leetcode.com/problems/sort-an-array/"
    elif any(word in problem_text_lower for word in ["search", "binary", "find"]):
        return "https://leetcode.com/problems/binary-search/"
    elif any(word in problem_text_lower for word in ["string", "substring", "character"]):
        return "https://leetcode.com/problems/longest-substring-without-repeating-characters/"
    elif any(word in problem_text_lower for word in ["palindrome", "palindromic"]):
        return "https://leetcode.com/problems/valid-palindrome/"
    elif any(word in problem_text_lower for word in ["parenthes", "bracket", "valid"]):
        return "https://leetcode.com/problems/valid-parentheses/"
    elif any(word in problem_text_lower for word in ["graph", "island", "connected"]):
        return "https://leetcode.com/problems/number-of-islands/"
    elif any(word in problem_text_lower for word in ["dynamic", "dp", "fibonacci", "stairs"]):
        return "https://leetcode.com/problems/climbing-stairs/"
    elif any(word in problem_text_lower for word in ["stack", "queue", "push", "pop"]):
        return "https://leetcode.com/problems/min-stack/"
    elif any(word in problem_text_lower for word in ["hash", "map", "frequency"]):
        return "https://leetcode.com/problems/two-sum/"
    
    # Default fallback
    return "https://leetcode.com/problemset/algorithms/"

def extract_problem_concepts(question_text):
    """Extract key concepts from the problem text with enhanced detection"""
    concepts = []
    question_lower = question_text.lower()
    
    concept_map = {
        "Array": ["array", "list", "element", "index", "subarray", "sum", "product"],
        "String": ["string", "character", "substring", "palindrome", "anagram", "text"],
        "Linked List": ["linked list", "node", "pointer", "next", "cycle", "reverse"],
        "Binary Tree": ["tree", "binary", "root", "leaf", "traversal", "inorder", "preorder", "postorder"],
        "Graph": ["graph", "vertex", "edge", "connected", "path", "island", "bfs", "dfs"],
        "Dynamic Programming": ["dynamic", "dp", "optimal", "subproblem", "fibonacci", "stairs", "coin"],
        "Sorting": ["sort", "merge", "quick", "heap", "bubble", "selection", "insertion"],
        "Binary Search": ["search", "binary search", "find", "locate", "target", "rotated"],
        "Stack": ["stack", "push", "pop", "lifo", "parentheses", "bracket"],
        "Queue": ["queue", "enqueue", "dequeue", "fifo", "level order"],
        "Hash Table": ["hash", "map", "dictionary", "key-value", "frequency", "count"],
        "Two Pointers": ["two pointer", "left", "right", "meet", "fast", "slow"],
        "Sliding Window": ["window", "substring", "subarray", "sliding", "maximum", "minimum"],
        "Recursion": ["recursive", "recursion", "base case", "divide", "conquer"],
        "Backtracking": ["backtrack", "permutation", "combination", "generate", "all possible"],
        "Greedy": ["greedy", "optimal", "local", "global", "activity", "interval"],
        "Bit Manipulation": ["bit", "xor", "and", "or", "shift", "binary", "power of 2"]
    }
    
    for concept, keywords in concept_map.items():
        if any(keyword in question_lower for keyword in keywords):
            concepts.append(concept)
    
    return concepts if concepts else ["General Algorithm"]

def get_difficulty_from_text(question_text):
    """Determine difficulty based on problem complexity indicators"""
    question_lower = question_text.lower()
    
    # Hard indicators
    hard_indicators = ["complex", "advanced", "optimize", "minimum time", "maximum efficiency", 
                      "hard", "challenging", "difficult", "expert", "o(log n)", "divide and conquer"]
    
    # Easy indicators  
    easy_indicators = ["simple", "basic", "easy", "straightforward", "beginner", "introduction",
                      "find", "check", "validate", "single pass"]
    
    hard_score = sum(1 for indicator in hard_indicators if indicator in question_lower)
    easy_score = sum(1 for indicator in easy_indicators if indicator in question_lower)
    
    if hard_score > easy_score and hard_score > 0:
        return "Hard"
    elif easy_score > 0:
        return "Easy"
    else:
        return "Medium"

def render_coding_questions():
    import json
    # Try to get the raw response (could be dict or string)
    questions_data = st.session_state.quiz.get("raw_response")
    if isinstance(questions_data, str):
        try:
            # Try to parse as JSON (handle single quotes if needed)
            questions_data = json.loads(questions_data.replace("'", '"'))
        except Exception:
            questions_data = {}
    elif not isinstance(questions_data, dict):
        questions_data = {}

    # Fallback to questions in session if not present
    if not questions_data or "questions" not in questions_data:
        questions = st.session_state.quiz.get("questions", [])
        if not questions:
            st.warning("No coding questions generated. Please try again.")
            return
        # Try to display as before if only titles/urls
        st.markdown("## 💻 Generated Coding Problems")
        st.markdown(f"### 📚 Tailored for {st.session_state.company} Interviews")
        st.markdown("Click on the problem links below to practice similar problems on LeetCode and other platforms.")
        st.write("")
        for i, q in enumerate(questions, 1):
            if isinstance(q, dict) and "title" in q and "url" in q:
                st.markdown(f"🔹 **Problem {i}: [{q['title']}]({q['url']})**")
            else:
                st.markdown(f"🔹 Problem {i}: {q}")
        st.markdown("---")
        return

    # Display from parsed JSON
    st.markdown("## 💻 Generated Coding Problems")
    st.markdown(f"### 📚 Tailored for {st.session_state.company} Interviews")
    st.markdown("Click on the problem links below to practice similar problems on LeetCode and other platforms.")
    st.write("")
    for i, q in enumerate(questions_data["questions"], 1):
        st.markdown(f"🔹 **Problem {i}: [{q['title']}]({q['url']})**")
    st.markdown("---")

def handle_generate_questions():
    logging.info(f"handle_generate_questions called: company={st.session_state.company}, category={st.session_state.category}, experience={st.session_state.experience}")
    # Persist controller in session state
    if 'controller' not in st.session_state or st.session_state.controller.company != st.session_state.company:
        st.session_state.controller = QuestionController(company=st.session_state.company)
    controller = st.session_state.controller
    
    # Determine category from UI selection
    category = "VQAR" if st.session_state.category.startswith("VQAR") else "Coding"
    
    # Reset quiz if category changed
    if st.session_state.get('current_category') != category:
        st.session_state.quiz = {
            "questions": [],
            "current": 0,
            "score": 0,
            "answers": [],
            "done": False,
            "generated": False,
            "start_time": None,
            "raw_response": None
        }
        st.session_state.current_category = category
    
    # Show loading spinner while generating
    with st.spinner(f"🔄 Generating {st.session_state.category} questions for {st.session_state.company}..."):
        try:
            # Map UI experience levels to backend values
            exp_mapping = {
                "Fresher (0-2 years)": "fresher",
                "Mid (2-5 years)": "mid", 
                "Senior (5+ years)": "senior"
            }
            experience = exp_mapping.get(st.session_state.experience, "fresher")
            
            # Generate questions using our controller
            result = controller.generate_questions(
                company=st.session_state.company,
                experience=experience,
                category=category
            )
            
            logging.info(f"Questions generated result: status={result.get('status', 'unknown')}, num_questions={len(result.get('questions', [])) if isinstance(result, dict) and 'questions' in result else 'N/A'}")
            
            # Handle API key errors specifically
            if isinstance(result, str) and ("API key" in result or "provide" in result):
                st.error(result)
                return
            
            # Store raw response for debugging
            st.session_state.quiz["raw_response"] = result
            
            # Process based on question type
            if category == "VQAR":
                _process_vqar_questions(result)
            else:
                _process_coding_questions(result)
                
        except Exception as e:
            logging.error(f"Error generating questions: {str(e)}")
            st.error(f"❌ Error generating questions: {str(e)}")
            if st.session_state.get('debug_mode', False):
                with st.expander("🐛 Error Details"):
                    st.exception(e)

def _process_vqar_questions(result):
    """Process and validate VQAR questions for Streamlit UI"""
    try:
        # If result is a dict with 'questions', use it directly
        if isinstance(result, dict) and 'questions' in result:
            questions = result['questions']
        else:
            questions = parse_quiz_response(result)
        
        logging.info(f"Processed VQAR questions: valid={len(questions)}")
        
        if not questions:
            logging.warning("No VQAR questions parsed.")
            st.error("❌ Could not parse questions. Please try again.")
            if st.session_state.debug_mode:
                with st.expander("Debug Raw Response"):
                    st.code(result, language='json')
            return
        
        # Validate question structure
        valid_questions = []
        for q in questions:
            if (isinstance(q, dict) and 
                'question' in q and q['question'].strip() and
                'options' in q and isinstance(q['options'], list) and
                len(q['options']) == 4 and all(isinstance(o, str) for o in q['options']) and
                'answer' in q and q['answer'] in q['options']):
                valid_questions.append(q)
        
        logging.info(f"Processed VQAR questions: valid={len(valid_questions)}")
        
        if not valid_questions:
            logging.warning("No valid VQAR questions generated.")
            st.error("❌ No valid questions generated. Please try again.")
            return
        
        # Apply question limit from UI slider
        num_questions = min(st.session_state.get('num_questions', 15), len(valid_questions))
        final_questions = valid_questions[:num_questions]
        
        # Update session state
        st.session_state.quiz.update({
            "questions": final_questions,
            "generated": True,
            "start_time": time.time(),
            "current": 0,
            "score": 0,
            "answers": [],
            "done": False
        })
        
        st.success(f"✅ Generated {len(final_questions)} valid aptitude questions!")
        st.rerun()
        
    except Exception as e:
        logging.error(f"Failed to process VQAR questions: {str(e)}")
        st.error(f"Failed to process VQAR questions: {str(e)}")
        if st.session_state.debug_mode:
            st.exception(e)

def _process_coding_questions(result: str):
    """Process and validate coding questions for Streamlit UI"""
    try:
        # Handle different response formats
        if isinstance(result, str):
            # Split by problem markers
            problem_split = re.split(r'\n---+\n|\n\*\*\*+\n', result)
            questions = [p.strip() for p in problem_split if p.strip()]
            
            # Fallback splitting if no markers found
            if len(questions) <= 1:
                questions = re.split(r'\n(?=Problem \d+|\d+\.)', result)
                questions = [q.strip() for q in questions if q.strip()]
        else:
            questions = [str(result)]
        
        # Filter and validate questions
        valid_questions = []
        for q in questions:
            if (isinstance(q, str) and len(q) >= 100 and 
                any(keyword in q.lower() for keyword in ["problem", "description", "input", "output"])):
                valid_questions.append(q)
        
        logging.info(f"Processed coding questions: valid={len(valid_questions)}")
        
        if not valid_questions:
            logging.warning("No valid coding questions generated.")
            st.error("❌ No valid coding questions generated. Please try again.")
            if st.session_state.debug_mode:
                with st.expander("Debug Raw Response"):
                    st.code(result, language='text')
            return
        
        # Limit to 15 questions max
        final_questions = valid_questions[:15]
        
        # Update session state
        st.session_state.quiz.update({
            "questions": final_questions,
            "generated": True,
            "start_time": time.time(),
            "current": 0,
            "score": 0,
            "answers": [],
            "done": False
        })
        
        st.success(f"✅ Generated {len(final_questions)} coding problems!")
        st.rerun()
        
    except Exception as e:
        logging.error(f"Failed to process coding questions: {str(e)}")
        st.error(f"Failed to process coding questions: {str(e)}")
        if st.session_state.debug_mode:
            st.exception(e)
# Initialize app
init_session_state()



# Sidebar controls
with st.sidebar:


    st.title("🧠 AI Placement Agent")
    st.markdown("---")
    
    st.markdown("### 🔑 API Configuration")
    
    # Gemini API Key Input
    gemini_api_key = st.text_input(
        "Enter Gemini API Key",
        type="password",
        help="Get your API key from https://ai.google.dev/"
    )
    
    if gemini_api_key:
        st.session_state.gemini_api_key = gemini_api_key
        st.success("✅ Gemini API key saved (not stored permanently)")
    
    # Tavily API Key Input
    tavily_api_key = st.text_input(
        "Enter Tavily API Key",
        type="password",
        help="Get your API key from https://app.tavily.com"
    )
    
    if tavily_api_key:
        st.session_state.tavily_api_key = tavily_api_key
        st.success("✅ Tavily API key saved (not stored permanently)")
    
    
    
    
    st.session_state.company = st.selectbox(
        "🏢 Target Company",
        ["Amazon", "Google", "Microsoft", "TCS", "Infosys", "Wipro", "Accenture", "Cognizant"],
        index=0,
        help="Select the company you're preparing for"
    )
    
    st.session_state.experience = st.selectbox(
        "👨‍💼 Experience Level",
        ["Fresher (0-2 years)", "Mid (2-5 years)", "Senior (5+ years)"],
        index=0,
        help="Your current experience level"
    )
    
    # Category selection with proper state management
    current_category = st.radio(
        "📋 Question Type",
        ["VQAR (Aptitude)", "Coding"],
        index=0,
        help="Choose between aptitude tests or coding problems"
    )
    
    # Reset quiz if category changed
    if st.session_state.get('category') != current_category:
        if st.session_state.get('category') is not None:  # Don't reset on first load
            st.session_state.quiz["generated"] = False
            st.session_state.quiz["questions"] = []
            st.session_state.quiz["answers"] = []
            st.session_state.quiz["current"] = 0
            st.session_state.quiz["score"] = 0
            st.session_state.quiz["done"] = False
        st.session_state.generate_questions_clicked = False  # Reset flag on category change
    
    st.session_state.category = current_category
    
    if st.session_state.category == "VQAR (Aptitude)":
        st.session_state.num_questions = st.slider(
            "📊 Number of Questions",
            min_value=5,
            max_value=25,
            value=15,
            step=5,
            help="Number of aptitude questions to generate"
        )
    
    st.markdown("---")
    st.markdown("### ⚙️ Advanced Options")
    st.session_state.debug_mode = st.checkbox("🐛 Debug Mode", help="Show detailed error information")
    
    st.markdown("---")
    
    if st.button("🚀 Generate Questions", use_container_width=True, type="primary"):
        st.session_state.generate_questions_clicked = True

    if st.session_state.get("generate_questions_clicked", False) and not st.session_state.quiz["generated"]:
        handle_generate_questions()
        st.session_state.generate_questions_clicked = False  # Reset after generation
    
    if st.session_state.quiz["generated"]:
        st.markdown("---")
        if st.button("🔄 Reset", use_container_width=True):
            init_session_state()
            st.session_state.generate_questions_clicked = False  # Reset flag on reset
            st.rerun()

# Main content area
st.title(f"🎯 AI Placement Preparation - {st.session_state.company}")

# Show content based on current category only - completely separate rendering
if not st.session_state.quiz["generated"]:
    st.markdown("### Welcome to AI Placement Agent! 👋")
    st.markdown("This advanced tool helps you prepare for placement interviews with personalized questions and direct problem links.")

    st.markdown("#### 📝 Aptitude Questions")
    st.markdown("Quantitative, Verbal, and Logical Reasoning with instant scoring")

    st.markdown("#### 💻 Coding Problems")
    st.markdown("Company-specific programming challenges with direct LeetCode links")

    st.markdown("### 🚀 Getting Started:")
    st.markdown("""
    1. 🏢 **Select your target company** from the sidebar  
    2. 👨‍💼 **Choose your experience level**  
    3. 📋 **Pick question type** (Aptitude or Coding)  
    4. 🚀 **Click "Generate Questions"** to begin!
    """)

    company_tips = {
        "Amazon": "Focus on Leadership Principles, system design, and coding efficiency",
        "Google": "Emphasize algorithms, data structures, and analytical thinking", 
        "Microsoft": "Practice problem-solving, coding, and behavioral questions",
        "TCS": "Prepare for aptitude, technical MCQs, and basic programming",
        "Infosys": "Focus on logical reasoning, basic programming, and communication",
        "Wipro": "Practice quantitative aptitude, verbal ability, and coding",
        "Accenture": "Prepare for cognitive abilities, technical skills, and communication",
        "Cognizant": "Focus on programming logic, aptitude, and English comprehension"
    }

    if st.session_state.company in company_tips:
        st.markdown(f"💡 **Tip for {st.session_state.company}**: {company_tips[st.session_state.company]}")

    st.markdown("👈 **Configure your preferences in the sidebar to get started!**")

else:
    # --- Dynamic Company-Specific Problems Section ---
    company = st.session_state.company
    problems_data = fetch_company_problems(company)
    st.markdown(f"## 📚 Tailored for {company} Interviews")
    st.markdown("Click on the problem links below to practice similar problems on LeetCode and other platforms.")
    st.write("")
    for i, q in enumerate(problems_data["questions"], 1):
        st.markdown(f"🔹 **Problem {i}: [{q['title']}]({q['url']})**")
    st.markdown("---")
    # Show appropriate content based on category and generation status
    if "VQAR" in st.session_state.category:
        render_aptitude_quiz()
    else:
        render_coding_questions()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 20px;">
    <p style="margin: 0;"><em>Built by KIRAN to help you ace your placement interviews! 🚀</em></p>
</div>
""", unsafe_allow_html=True)