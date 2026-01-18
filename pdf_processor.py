"""
PDF Processing Module
Handles text extraction from uploaded PDF documents.
"""

import pdfplumber
from io import BytesIO
from typing import Optional


def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_file: BytesIO object containing the PDF data
        
    Returns:
        Extracted text as a string
    """
    text_content = []
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(f"--- Page {page_num} ---\n{page_text}")
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    if not text_content:
        raise ValueError("No text could be extracted from the PDF. The document may be scanned or image-based.")
    
    return "\n\n".join(text_content)


def get_pdf_info(pdf_file: BytesIO) -> dict:
    """
    Get basic information about a PDF file.
    
    Args:
        pdf_file: BytesIO object containing the PDF data
        
    Returns:
        Dictionary with PDF metadata
    """
    info = {
        "num_pages": 0,
        "has_text": False
    }
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            info["num_pages"] = len(pdf.pages)
            # Check if first page has extractable text
            if pdf.pages:
                first_page_text = pdf.pages[0].extract_text()
                info["has_text"] = bool(first_page_text and first_page_text.strip())
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {str(e)}")
    
    return info
