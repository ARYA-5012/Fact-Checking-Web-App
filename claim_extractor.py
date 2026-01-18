"""
Claim Extraction Module
Uses LLM to identify and extract verifiable claims from document text.
Uses OpenRouter API (OpenAI-compatible) for model access.
"""

import json
from typing import List, Dict
from openai import OpenAI
import streamlit as st


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


CLAIM_EXTRACTION_PROMPT = """You are an expert fact-checker. Analyze the following document text and extract ALL verifiable claims that can be fact-checked against real-world data.

Focus on extracting:
1. Statistics and numerical data (percentages, amounts, counts)
2. Dates and timelines (when events occurred or will occur)
3. Financial figures (prices, GDP, market values, stock prices)
4. Technical specifications and product details
5. Company/organization statements and announcements
6. Scientific or factual assertions

For EACH claim, provide:
- claim: The exact claim as stated in the document
- category: One of [Statistics, Date/Timeline, Financial, Technical, Organizational, Scientific]
- context: Brief context about what the claim relates to
- verification_query: A specific search query to verify this claim

Return your response as a JSON array of claim objects.

DOCUMENT TEXT:
{document_text}

IMPORTANT: Extract ALL factual claims, especially those involving specific numbers, dates, or named entities. Be thorough - the goal is to verify every checkable fact in the document.

Return ONLY valid JSON array, no additional text."""


def extract_claims(document_text: str) -> List[Dict]:
    """
    Extract verifiable claims from document text using LLM via OpenRouter.
    
    Args:
        document_text: The text content to analyze
        
    Returns:
        List of claim dictionaries with claim, category, context, and verification_query
    """
    client = get_openai_client()
    
    # Truncate if too long (keep within context limits)
    max_chars = 50000
    if len(document_text) > max_chars:
        document_text = document_text[:max_chars] + "\n...[truncated]"
    
    try:
        model_name = get_model_name()
        response = client.chat.completions.create(
            model=model_name,  # Use model from secrets
            messages=[
                {
                    "role": "user",
                    "content": CLAIM_EXTRACTION_PROMPT.format(document_text=document_text)
                }
            ],
            temperature=0.1,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up response if wrapped in markdown code blocks
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        claims = json.loads(content)
        
        if not isinstance(claims, list):
            claims = [claims]
            
        return claims
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
    except Exception as e:
        raise ValueError(f"Claim extraction failed: {str(e)}")


def format_claim_for_display(claim: Dict) -> str:
    """Format a claim dictionary for display."""
    return f"**{claim.get('category', 'Unknown')}**: {claim.get('claim', 'N/A')}"
