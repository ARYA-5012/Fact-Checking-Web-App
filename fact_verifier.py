"""
Fact Verification Module
Verifies claims against live web data using Tavily search API.
Uses OpenRouter API (OpenAI-compatible) for model access.
"""

import json
from typing import Dict, List, Optional
from tavily import TavilyClient
from openai import OpenAI
import streamlit as st


def get_tavily_client() -> TavilyClient:
    """Get Tavily client with API key from Streamlit secrets."""
    try:
        api_key = st.secrets.get("TAVILY_API_KEY", "")
    except Exception:
        api_key = ""
    if not api_key:
        raise ValueError("Tavily API key not found in secrets. Please configure TAVILY_API_KEY.")
    return TavilyClient(api_key=api_key)


def get_openai_client() -> OpenAI:
    """Get OpenAI-compatible client configured for OpenRouter."""
    try:
        api_key = st.secrets.get("OPENROUTER_API_KEY", "")
    except Exception:
        api_key = ""
    if not api_key:
        raise ValueError("API key not found in secrets. Please configure OPENROUTER_API_KEY.")
    
    # Use OpenRouter's base URL
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )


def get_model_name() -> str:
    """Get the model name to use from secrets."""
    try:
        model = st.secrets.get("OpenAi_API_KEY", "google/gemma-2-9b-it")
    except Exception:
        model = "google/gemma-2-9b-it"
    return model


def search_web(query: str, num_results: int = 5) -> List[Dict]:
    """
    Search the web using Tavily API.
    
    Args:
        query: Search query string
        num_results: Number of results to return
        
    Returns:
        List of search result dictionaries
    """
    client = get_tavily_client()
    
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=num_results,
            include_answer=True
        )
        return response
    except Exception as e:
        raise ValueError(f"Web search failed: {str(e)}")


VERIFICATION_PROMPT = """You are an expert fact-checker. Analyze the following claim against the search results and determine its accuracy.

CLAIM TO VERIFY:
{claim}

CLAIM CONTEXT:
{context}

SEARCH RESULTS:
{search_results}

Analyze the claim and search results, then provide your assessment in the following JSON format:
{{
    "status": "Verified" | "Inaccurate" | "False" | "Unverifiable",
    "confidence": 0.0-1.0,
    "explanation": "Brief explanation of why this claim is verified/inaccurate/false",
    "correct_information": "If the claim is inaccurate or false, provide the correct information found. Otherwise, leave empty.",
    "sources": ["List of source URLs that support your conclusion"]
}}

IMPORTANT GUIDELINES:
- "Verified": The claim matches current, reliable data
- "Inaccurate": The claim contains outdated or partially incorrect information (e.g., old statistics)
- "False": The claim is demonstrably wrong or no evidence supports it
- "Unverifiable": Cannot determine accuracy from available sources

Pay special attention to:
- Dates and whether information might be outdated
- Specific numbers that may have changed
- Events that may or may not have occurred

Return ONLY valid JSON, no additional text."""


def verify_claim(claim: Dict) -> Dict:
    """
    Verify a single claim using web search and LLM analysis.
    
    Args:
        claim: Dictionary with claim details
        
    Returns:
        Dictionary with verification results
    """
    claim_text = claim.get("claim", "")
    context = claim.get("context", "")
    query = claim.get("verification_query", claim_text)
    
    # Search the web
    try:
        search_results = search_web(query)
    except Exception as e:
        return {
            "claim": claim_text,
            "category": claim.get("category", "Unknown"),
            "status": "Unverifiable",
            "confidence": 0.0,
            "explanation": f"Could not search web: {str(e)}",
            "correct_information": "",
            "sources": []
        }
    
    # Format search results for the LLM
    formatted_results = []
    if search_results.get("answer"):
        formatted_results.append(f"AI Summary: {search_results['answer']}")
    
    for result in search_results.get("results", [])[:5]:
        formatted_results.append(
            f"Source: {result.get('url', 'Unknown')}\n"
            f"Title: {result.get('title', 'No title')}\n"
            f"Content: {result.get('content', 'No content')}\n"
        )
    
    search_text = "\n\n".join(formatted_results)
    
    # Use LLM to analyze via OpenRouter
    openai_client = get_openai_client()
    
    try:
        model_name = get_model_name()
        response = openai_client.chat.completions.create(
            model=model_name,  # Use model from secrets
            messages=[
                {
                    "role": "user",
                    "content": VERIFICATION_PROMPT.format(
                        claim=claim_text,
                        context=context,
                        search_results=search_text
                    )
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up response if wrapped in markdown code blocks
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        result = json.loads(content)
        
        # Add original claim info
        result["claim"] = claim_text
        result["category"] = claim.get("category", "Unknown")
        
        return result
        
    except Exception as e:
        return {
            "claim": claim_text,
            "category": claim.get("category", "Unknown"),
            "status": "Unverifiable",
            "confidence": 0.0,
            "explanation": f"Verification analysis failed: {str(e)}",
            "correct_information": "",
            "sources": []
        }


def verify_all_claims(claims: List[Dict], progress_callback=None) -> List[Dict]:
    """
    Verify all claims and return results.
    
    Args:
        claims: List of claim dictionaries
        progress_callback: Optional callback function for progress updates
        
    Returns:
        List of verification result dictionaries
    """
    results = []
    total = len(claims)
    
    for i, claim in enumerate(claims):
        if progress_callback:
            progress_callback(i, total, claim.get("claim", "")[:50] + "...")
        
        result = verify_claim(claim)
        results.append(result)
    
    return results


def get_status_emoji(status: str) -> str:
    """Return emoji indicator for verification status."""
    status_map = {
        "Verified": "✅",
        "Inaccurate": "⚠️",
        "False": "❌",
        "Unverifiable": "❓"
    }
    return status_map.get(status, "❓")


def get_status_color(status: str) -> str:
    """Return color for verification status."""
    status_map = {
        "Verified": "green",
        "Inaccurate": "orange",
        "False": "red",
        "Unverifiable": "gray"
    }
    return status_map.get(status, "gray")
