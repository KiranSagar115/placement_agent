from typing import List, Dict
import requests
import os
from dotenv import load_dotenv
import re
import streamlit as st
import logging

load_dotenv()

def fetch_tavily_search(query: str, api_key: str, max_results: int = 25) -> List[Dict]:
    """Fetch search results from Tavily API"""
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "include_answer": True,
        "include_raw_content": True,
        "max_results": max_results
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        logging.info(f"Tavily API raw response: {data}")
        return data.get("results", [])
    except Exception as e:
        logging.error(f"Tavily API error: {str(e)}")
        return []

def extract_leetcode_problems(results: List[Dict], max_count: int = 20) -> List[Dict]:
    """Extract individual LeetCode problems from Tavily results."""
    problems = []
    seen = set()
    # First, try to get direct LeetCode problem links
    for result in results:
        url = result.get('url', '')
        logging.info(f"Tavily result URL: {url}")
        match = re.match(r'https://leetcode.com/problems/([\w-]+)/?$', url)
        if match and url not in seen:
            seen.add(url)
            title = result.get('title', match.group(1).replace('-', ' ').title())
            description = result.get('content', '')
            problems.append({
                "title": title,
                "url": url,
                "description": description
            })
            if len(problems) >= max_count:
                break
    # If not enough, include any LeetCode problem URLs
    if len(problems) < max_count:
        for result in results:
            url = result.get('url', '')
            if url in seen:
                continue
            if url.startswith('https://leetcode.com/problems/'):
                seen.add(url)
                title = result.get('title', url.split('/problems/')[-1].replace('-', ' ').title())
                description = result.get('content', '')
                problems.append({
                    "title": title,
                    "url": url,
                    "description": description
                })
                if len(problems) >= max_count:
                    break
    return problems

STATIC_COMPANY_QUESTIONS = {
    "Amazon": [
        {"title": "Two Sum", "url": "https://leetcode.com/problems/two-sum/"},
        {"title": "Longest Substring Without Repeating Characters", "url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/"},
        {"title": "Median of Two Sorted Arrays", "url": "https://leetcode.com/problems/median-of-two-sorted-arrays/"},
        {"title": "Merge Intervals", "url": "https://leetcode.com/problems/merge-intervals/"},
        {"title": "Valid Parentheses", "url": "https://leetcode.com/problems/valid-parentheses/"},
        {"title": "Search in Rotated Sorted Array", "url": "https://leetcode.com/problems/search-in-rotated-sorted-array/"},
        {"title": "Trapping Rain Water", "url": "https://leetcode.com/problems/trapping-rain-water/"},
        {"title": "Word Ladder", "url": "https://leetcode.com/problems/word-ladder/"},
        {"title": "Minimum Window Substring", "url": "https://leetcode.com/problems/minimum-window-substring/"},
        {"title": "LRU Cache", "url": "https://leetcode.com/problems/lru-cache/"},
        {"title": "Course Schedule", "url": "https://leetcode.com/problems/course-schedule/"},
        {"title": "Clone Graph", "url": "https://leetcode.com/problems/clone-graph/"},
        {"title": "Number of Islands", "url": "https://leetcode.com/problems/number-of-islands/"},
        {"title": "Kth Largest Element in an Array", "url": "https://leetcode.com/problems/kth-largest-element-in-an-array/"},
        {"title": "Product of Array Except Self", "url": "https://leetcode.com/problems/product-of-array-except-self/"},
        {"title": "Find Minimum in Rotated Sorted Array", "url": "https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/"},
        {"title": "Maximum Subarray", "url": "https://leetcode.com/problems/maximum-subarray/"},
        {"title": "Binary Tree Maximum Path Sum", "url": "https://leetcode.com/problems/binary-tree-maximum-path-sum/"},
        {"title": "Serialize and Deserialize Binary Tree", "url": "https://leetcode.com/problems/serialize-and-deserialize-binary-tree/"},
        {"title": "Subsets", "url": "https://leetcode.com/problems/subsets/"}
    ],
    "Google": [
        {"title": "Add Two Numbers", "url": "https://leetcode.com/problems/add-two-numbers/"},
        {"title": "Word Search", "url": "https://leetcode.com/problems/word-search/"},
        {"title": "Longest Palindromic Substring", "url": "https://leetcode.com/problems/longest-palindromic-substring/"},
        {"title": "Regular Expression Matching", "url": "https://leetcode.com/problems/regular-expression-matching/"},
        {"title": "Jump Game", "url": "https://leetcode.com/problems/jump-game/"},
        {"title": "Insert Interval", "url": "https://leetcode.com/problems/insert-interval/"},
        {"title": "Minimum Window Substring", "url": "https://leetcode.com/problems/minimum-window-substring/"},
        {"title": "Word Break", "url": "https://leetcode.com/problems/word-break/"},
        {"title": "Find Median from Data Stream", "url": "https://leetcode.com/problems/find-median-from-data-stream/"},
        {"title": "Alien Dictionary", "url": "https://leetcode.com/problems/alien-dictionary/"},
        {"title": "Course Schedule II", "url": "https://leetcode.com/problems/course-schedule-ii/"},
        {"title": "Meeting Rooms II", "url": "https://leetcode.com/problems/meeting-rooms-ii/"},
        {"title": "Sliding Window Maximum", "url": "https://leetcode.com/problems/sliding-window-maximum/"},
        {"title": "Find All Anagrams in a String", "url": "https://leetcode.com/problems/find-all-anagrams-in-a-string/"},
        {"title": "Longest Consecutive Sequence", "url": "https://leetcode.com/problems/longest-consecutive-sequence/"},
        {"title": "Merge k Sorted Lists", "url": "https://leetcode.com/problems/merge-k-sorted-lists/"},
        {"title": "Median of Two Sorted Arrays", "url": "https://leetcode.com/problems/median-of-two-sorted-arrays/"},
        {"title": "Binary Tree Right Side View", "url": "https://leetcode.com/problems/binary-tree-right-side-view/"},
        {"title": "Unique Paths", "url": "https://leetcode.com/problems/unique-paths/"},
        {"title": "Search a 2D Matrix", "url": "https://leetcode.com/problems/search-a-2d-matrix/"}
    ],
    "Microsoft": [
        {"title": "Set Matrix Zeroes", "url": "https://leetcode.com/problems/set-matrix-zeroes/"},
        {"title": "Spiral Matrix", "url": "https://leetcode.com/problems/spiral-matrix/"},
        {"title": "Rotate Image", "url": "https://leetcode.com/problems/rotate-image/"},
        {"title": "Group Anagrams", "url": "https://leetcode.com/problems/group-anagrams/"},
        {"title": "Pow(x, n)", "url": "https://leetcode.com/problems/powx-n/"},
        {"title": "Search a 2D Matrix II", "url": "https://leetcode.com/problems/search-a-2d-matrix-ii/"},
        {"title": "Word Ladder II", "url": "https://leetcode.com/problems/word-ladder-ii/"},
        {"title": "Binary Tree Level Order Traversal", "url": "https://leetcode.com/problems/binary-tree-level-order-traversal/"},
        {"title": "Validate Binary Search Tree", "url": "https://leetcode.com/problems/validate-binary-search-tree/"},
        {"title": "Lowest Common Ancestor of a Binary Tree", "url": "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/"},
        {"title": "House Robber", "url": "https://leetcode.com/problems/house-robber/"},
        {"title": "House Robber II", "url": "https://leetcode.com/problems/house-robber-ii/"},
        {"title": "Number of Islands", "url": "https://leetcode.com/problems/number-of-islands/"},
        {"title": "Reverse Linked List", "url": "https://leetcode.com/problems/reverse-linked-list/"},
        {"title": "Merge Two Sorted Lists", "url": "https://leetcode.com/problems/merge-two-sorted-lists/"},
        {"title": "Intersection of Two Linked Lists", "url": "https://leetcode.com/problems/intersection-of-two-linked-lists/"},
        {"title": "Linked List Cycle", "url": "https://leetcode.com/problems/linked-list-cycle/"},
        {"title": "Copy List with Random Pointer", "url": "https://leetcode.com/problems/copy-list-with-random-pointer/"},
        {"title": "LRU Cache", "url": "https://leetcode.com/problems/lru-cache/"},
        {"title": "Find Minimum in Rotated Sorted Array", "url": "https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/"}
    ],
    "TCS": [
        {"title": "Remove Duplicates from Sorted Array", "url": "https://leetcode.com/problems/remove-duplicates-from-sorted-array/"},
        {"title": "Best Time to Buy and Sell Stock", "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/"},
        {"title": "Valid Anagram", "url": "https://leetcode.com/problems/valid-anagram/"},
        {"title": "Intersection of Two Arrays II", "url": "https://leetcode.com/problems/intersection-of-two-arrays-ii/"},
        {"title": "Majority Element", "url": "https://leetcode.com/problems/majority-element/"},
        {"title": "Move Zeroes", "url": "https://leetcode.com/problems/move-zeroes/"},
        {"title": "Contains Duplicate", "url": "https://leetcode.com/problems/contains-duplicate/"},
        {"title": "Single Number", "url": "https://leetcode.com/problems/single-number/"},
        {"title": "Maximum Subarray", "url": "https://leetcode.com/problems/maximum-subarray/"},
        {"title": "Merge Sorted Array", "url": "https://leetcode.com/problems/merge-sorted-array/"},
        {"title": "Reverse String", "url": "https://leetcode.com/problems/reverse-string/"},
        {"title": "First Unique Character in a String", "url": "https://leetcode.com/problems/first-unique-character-in-a-string/"},
        {"title": "Valid Palindrome", "url": "https://leetcode.com/problems/valid-palindrome/"},
        {"title": "Palindrome Number", "url": "https://leetcode.com/problems/palindrome-number/"},
        {"title": "Roman to Integer", "url": "https://leetcode.com/problems/roman-to-integer/"},
        {"title": "Implement strStr()", "url": "https://leetcode.com/problems/implement-strstr/"},
        {"title": "Count and Say", "url": "https://leetcode.com/problems/count-and-say/"},
        {"title": "Maximum Depth of Binary Tree", "url": "https://leetcode.com/problems/maximum-depth-of-binary-tree/"},
        {"title": "Symmetric Tree", "url": "https://leetcode.com/problems/symmetric-tree/"},
        {"title": "Path Sum", "url": "https://leetcode.com/problems/path-sum/"}
    ],
    "Infosys": [
        {"title": "Reverse Linked List", "url": "https://leetcode.com/problems/reverse-linked-list/"},
        {"title": "Merge Two Sorted Lists", "url": "https://leetcode.com/problems/merge-two-sorted-lists/"},
        {"title": "Remove Nth Node From End of List", "url": "https://leetcode.com/problems/remove-nth-node-from-end-of-list/"},
        {"title": "Linked List Cycle", "url": "https://leetcode.com/problems/linked-list-cycle/"},
        {"title": "Intersection of Two Linked Lists", "url": "https://leetcode.com/problems/intersection-of-two-linked-lists/"},
        {"title": "Palindrome Linked List", "url": "https://leetcode.com/problems/palindrome-linked-list/"},
        {"title": "Add Two Numbers", "url": "https://leetcode.com/problems/add-two-numbers/"},
        {"title": "Remove Duplicates from Sorted List", "url": "https://leetcode.com/problems/remove-duplicates-from-sorted-list/"},
        {"title": "Reverse String", "url": "https://leetcode.com/problems/reverse-string/"},
        {"title": "Valid Parentheses", "url": "https://leetcode.com/problems/valid-parentheses/"},
        {"title": "Valid Palindrome", "url": "https://leetcode.com/problems/valid-palindrome/"},
        {"title": "Best Time to Buy and Sell Stock", "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/"},
        {"title": "Maximum Subarray", "url": "https://leetcode.com/problems/maximum-subarray/"},
        {"title": "Contains Duplicate", "url": "https://leetcode.com/problems/contains-duplicate/"},
        {"title": "Single Number", "url": "https://leetcode.com/problems/single-number/"},
        {"title": "Majority Element", "url": "https://leetcode.com/problems/majority-element/"},
        {"title": "Move Zeroes", "url": "https://leetcode.com/problems/move-zeroes/"},
        {"title": "Intersection of Two Arrays II", "url": "https://leetcode.com/problems/intersection-of-two-arrays-ii/"},
        {"title": "First Unique Character in a String", "url": "https://leetcode.com/problems/first-unique-character-in-a-string/"},
        {"title": "Roman to Integer", "url": "https://leetcode.com/problems/roman-to-integer/"}
    ],
    "Wipro": [
        {"title": "Valid Parentheses", "url": "https://leetcode.com/problems/valid-parentheses/"},
        {"title": "Merge Two Sorted Lists", "url": "https://leetcode.com/problems/merge-two-sorted-lists/"},
        {"title": "Remove Duplicates from Sorted Array", "url": "https://leetcode.com/problems/remove-duplicates-from-sorted-array/"},
        {"title": "Best Time to Buy and Sell Stock", "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/"},
        {"title": "Valid Anagram", "url": "https://leetcode.com/problems/valid-anagram/"},
        {"title": "Intersection of Two Arrays II", "url": "https://leetcode.com/problems/intersection-of-two-arrays-ii/"},
        {"title": "Majority Element", "url": "https://leetcode.com/problems/majority-element/"},
        {"title": "Move Zeroes", "url": "https://leetcode.com/problems/move-zeroes/"},
        {"title": "Contains Duplicate", "url": "https://leetcode.com/problems/contains-duplicate/"},
        {"title": "Single Number", "url": "https://leetcode.com/problems/single-number/"},
        {"title": "Maximum Subarray", "url": "https://leetcode.com/problems/maximum-subarray/"},
        {"title": "Merge Sorted Array", "url": "https://leetcode.com/problems/merge-sorted-array/"},
        {"title": "Reverse String", "url": "https://leetcode.com/problems/reverse-string/"},
        {"title": "First Unique Character in a String", "url": "https://leetcode.com/problems/first-unique-character-in-a-string/"},
        {"title": "Valid Palindrome", "url": "https://leetcode.com/problems/valid-palindrome/"},
        {"title": "Palindrome Number", "url": "https://leetcode.com/problems/palindrome-number/"},
        {"title": "Roman to Integer", "url": "https://leetcode.com/problems/roman-to-integer/"},
        {"title": "Implement strStr()", "url": "https://leetcode.com/problems/implement-strstr/"},
        {"title": "Count and Say", "url": "https://leetcode.com/problems/count-and-say/"},
        {"title": "Maximum Depth of Binary Tree", "url": "https://leetcode.com/problems/maximum-depth-of-binary-tree/"}
    ],
    "Accenture": [
        {"title": "Valid Parentheses", "url": "https://leetcode.com/problems/valid-parentheses/"},
        {"title": "Merge Two Sorted Lists", "url": "https://leetcode.com/problems/merge-two-sorted-lists/"},
        {"title": "Remove Duplicates from Sorted Array", "url": "https://leetcode.com/problems/remove-duplicates-from-sorted-array/"},
        {"title": "Best Time to Buy and Sell Stock", "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/"},
        {"title": "Valid Anagram", "url": "https://leetcode.com/problems/valid-anagram/"},
        {"title": "Intersection of Two Arrays II", "url": "https://leetcode.com/problems/intersection-of-two-arrays-ii/"},
        {"title": "Majority Element", "url": "https://leetcode.com/problems/majority-element/"},
        {"title": "Move Zeroes", "url": "https://leetcode.com/problems/move-zeroes/"},
        {"title": "Contains Duplicate", "url": "https://leetcode.com/problems/contains-duplicate/"},
        {"title": "Single Number", "url": "https://leetcode.com/problems/single-number/"},
        {"title": "Maximum Subarray", "url": "https://leetcode.com/problems/maximum-subarray/"},
        {"title": "Merge Sorted Array", "url": "https://leetcode.com/problems/merge-sorted-array/"},
        {"title": "Reverse String", "url": "https://leetcode.com/problems/reverse-string/"},
        {"title": "First Unique Character in a String", "url": "https://leetcode.com/problems/first-unique-character-in-a-string/"},
        {"title": "Valid Palindrome", "url": "https://leetcode.com/problems/valid-palindrome/"},
        {"title": "Palindrome Number", "url": "https://leetcode.com/problems/palindrome-number/"},
        {"title": "Roman to Integer", "url": "https://leetcode.com/problems/roman-to-integer/"},
        {"title": "Implement strStr()", "url": "https://leetcode.com/problems/implement-strstr/"},
        {"title": "Count and Say", "url": "https://leetcode.com/problems/count-and-say/"},
        {"title": "Maximum Depth of Binary Tree", "url": "https://leetcode.com/problems/maximum-depth-of-binary-tree/"}
    ],
    "Cognizant": [
        {"title": "Valid Parentheses", "url": "https://leetcode.com/problems/valid-parentheses/"},
        {"title": "Merge Two Sorted Lists", "url": "https://leetcode.com/problems/merge-two-sorted-lists/"},
        {"title": "Remove Duplicates from Sorted Array", "url": "https://leetcode.com/problems/remove-duplicates-from-sorted-array/"},
        {"title": "Best Time to Buy and Sell Stock", "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/"},
        {"title": "Valid Anagram", "url": "https://leetcode.com/problems/valid-anagram/"},
        {"title": "Intersection of Two Arrays II", "url": "https://leetcode.com/problems/intersection-of-two-arrays-ii/"},
        {"title": "Majority Element", "url": "https://leetcode.com/problems/majority-element/"},
        {"title": "Move Zeroes", "url": "https://leetcode.com/problems/move-zeroes/"},
        {"title": "Contains Duplicate", "url": "https://leetcode.com/problems/contains-duplicate/"},
        {"title": "Single Number", "url": "https://leetcode.com/problems/single-number/"},
        {"title": "Maximum Subarray", "url": "https://leetcode.com/problems/maximum-subarray/"},
        {"title": "Merge Sorted Array", "url": "https://leetcode.com/problems/merge-sorted-array/"},
        {"title": "Reverse String", "url": "https://leetcode.com/problems/reverse-string/"},
        {"title": "First Unique Character in a String", "url": "https://leetcode.com/problems/first-unique-character-in-a-string/"},
        {"title": "Valid Palindrome", "url": "https://leetcode.com/problems/valid-palindrome/"},
        {"title": "Palindrome Number", "url": "https://leetcode.com/problems/palindrome-number/"},
        {"title": "Roman to Integer", "url": "https://leetcode.com/problems/roman-to-integer/"},
        {"title": "Implement strStr()", "url": "https://leetcode.com/problems/implement-strstr/"},
        {"title": "Count and Say", "url": "https://leetcode.com/problems/count-and-say/"},
        {"title": "Maximum Depth of Binary Tree", "url": "https://leetcode.com/problems/maximum-depth-of-binary-tree/"}
    ]
}

def generate_coding(company: str, experience: str) -> List[Dict]:
    """Generate company-specific coding questions using Tavily API, returning a list of dicts."""
    tavily_api_key = os.getenv("TAVILY_API_KEY") or st.session_state.get("tavily_api_key")
    if not tavily_api_key:
        return [{"error": "Please provide a Tavily API key in the sidebar to fetch coding questions."}]
    query = f"20 most frequently asked LeetCode problems in {company} interviews with direct LeetCode links"
    results = fetch_tavily_search(query, tavily_api_key, max_results=30)
    problems = extract_leetcode_problems(results, max_count=20)
    if not problems:
        # Use static fallback if available
        static = STATIC_COMPANY_QUESTIONS.get(company)
        if static:
            return static
        return [{"error": "Failed to fetch LeetCode problems. Please check your API key or try again later."}]
    return problems