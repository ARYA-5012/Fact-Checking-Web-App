"""
Fact-Checking Web App
A Streamlit application that verifies claims from PDF documents against live web data.
"""

import streamlit as st
from io import BytesIO
import time

from pdf_processor import extract_text_from_pdf, get_pdf_info
from claim_extractor import extract_claims
from fact_verifier import verify_all_claims, get_status_emoji, get_status_color


def get_secret(key: str, default: str = "") -> str:
    """Safely get a secret value, returning default if not found."""
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

# Page configuration
st.set_page_config(
    page_title="Fact Checker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .result-card {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #475569;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Status badges */
    .status-verified {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .status-inaccurate {
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .status-false {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .status-unverifiable {
        background: linear-gradient(135deg, #4b5563 0%, #6b7280 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    /* Upload area */
    .uploadedFile {
        background: #1e293b !important;
        border: 2px dashed #6366f1 !important;
        border-radius: 16px !important;
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #475569;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .stat-label {
        color: #94a3b8;
        font-size: 0.85rem;
        margin: 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #1e293b;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


def display_header():
    """Display the app header."""
    st.markdown('<h1 class="main-header">🔍 Fact Checker</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Upload a PDF document to verify claims against real-time web data</p>',
        unsafe_allow_html=True
    )


def display_stats(results: list):
    """Display summary statistics."""
    verified = sum(1 for r in results if r.get("status") == "Verified")
    inaccurate = sum(1 for r in results if r.get("status") == "Inaccurate")
    false = sum(1 for r in results if r.get("status") == "False")
    unverifiable = sum(1 for r in results if r.get("status") == "Unverifiable")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number" style="color: #10b981;">✅ {verified}</p>
            <p class="stat-label">Verified</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number" style="color: #f59e0b;">⚠️ {inaccurate}</p>
            <p class="stat-label">Inaccurate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number" style="color: #ef4444;">❌ {false}</p>
            <p class="stat-label">False</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number" style="color: #6b7280;">❓ {unverifiable}</p>
            <p class="stat-label">Unverifiable</p>
        </div>
        """, unsafe_allow_html=True)


def get_status_badge(status: str) -> str:
    """Return HTML badge for status."""
    class_map = {
        "Verified": "status-verified",
        "Inaccurate": "status-inaccurate",
        "False": "status-false",
        "Unverifiable": "status-unverifiable"
    }
    css_class = class_map.get(status, "status-unverifiable")
    emoji = get_status_emoji(status)
    return f'<span class="{css_class}">{emoji} {status}</span>'


def display_result(result: dict, index: int):
    """Display a single verification result."""
    status = result.get("status", "Unknown")
    emoji = get_status_emoji(status)
    claim = result.get("claim", "Unknown claim")
    category = result.get("category", "Unknown")
    explanation = result.get("explanation", "No explanation available")
    correct_info = result.get("correct_information", "")
    sources = result.get("sources", [])
    confidence = result.get("confidence", 0)
    
    # Status color for border
    color_map = {
        "Verified": "#10b981",
        "Inaccurate": "#f59e0b", 
        "False": "#ef4444",
        "Unverifiable": "#6b7280"
    }
    border_color = color_map.get(status, "#6b7280")
    
    with st.expander(f"{emoji} **Claim {index + 1}**: {claim[:80]}{'...' if len(claim) > 80 else ''}", expanded=(status != "Verified")):
        # Status and category
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.markdown(f"**Status:** {get_status_badge(status)}", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**Category:** `{category}`")
        with col3:
            st.markdown(f"**Confidence:** {confidence:.0%}")
        
        st.divider()
        
        # Full claim
        st.markdown("**📝 Claim:**")
        st.info(claim)
        
        # Explanation
        st.markdown("**🔎 Analysis:**")
        st.write(explanation)
        
        # Correct information (if applicable)
        if correct_info and status in ["Inaccurate", "False"]:
            st.markdown("**✨ Correct Information:**")
            st.success(correct_info)
        
        # Sources
        if sources:
            st.markdown("**📚 Sources:**")
            for source in sources[:3]:
                st.markdown(f"- [{source}]({source})")


def main():
    """Main application function."""
    display_header()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        st.markdown("---")
        st.markdown("""
        **How it works:**
        1. Upload a PDF document
        2. AI extracts verifiable claims
        3. Claims are checked against live web data
        4. Results show verification status
        
        **Status Legend:**
        - ✅ **Verified**: Claim matches current data
        - ⚠️ **Inaccurate**: Outdated or partially wrong
        - ❌ **False**: No supporting evidence
        - ❓ **Unverifiable**: Cannot determine
        """)
        
        st.markdown("---")
        st.markdown("### 🔑 API Status")
        
        # Check API keys
        openai_ok = bool(get_secret("OPENROUTER_API_KEY"))
        tavily_ok = bool(get_secret("TAVILY_API_KEY"))
        
        if openai_ok:
            st.success("✅ OpenAI API configured")
        else:
            st.error("❌ OpenAI API key missing")
            
        if tavily_ok:
            st.success("✅ Tavily API configured")
        else:
            st.error("❌ Tavily API key missing")
    
    # Main content area
    st.markdown("### 📄 Upload Document")
    
    uploaded_file = st.file_uploader(
        "Drag and drop a PDF file here",
        type=["pdf"],
        help="Upload a PDF document to extract and verify claims"
    )
    
    if uploaded_file is not None:
        # Show file info
        st.markdown(f"**📁 File:** `{uploaded_file.name}` ({uploaded_file.size / 1024:.1f} KB)")
        
        # Process button
        if st.button("🚀 Analyze & Verify Claims", type="primary", use_container_width=True):
            
            # Check API keys first
            openai_key = get_secret("OPENROUTER_API_KEY")
            if not openai_key or not get_secret("TAVILY_API_KEY"):
                st.error("⚠️ Please configure API keys in Streamlit secrets to use this app.")
                st.info("Add OPENROUTER_API_KEY and TAVILY_API_KEY to your secrets.toml file or Streamlit Cloud secrets.")
                return
            
            # Process the PDF
            with st.status("🔄 Processing document...", expanded=True) as status:
                try:
                    # Step 1: Extract text
                    st.write("📖 Extracting text from PDF...")
                    pdf_bytes = BytesIO(uploaded_file.read())
                    document_text = extract_text_from_pdf(pdf_bytes)
                    st.write(f"✅ Extracted {len(document_text):,} characters of text")
                    
                    # Step 2: Extract claims
                    st.write("🔍 Identifying verifiable claims...")
                    claims = extract_claims(document_text)
                    st.write(f"✅ Found {len(claims)} verifiable claims")
                    
                    # Step 3: Verify claims
                    st.write("🌐 Verifying claims against web data...")
                    progress_bar = st.progress(0)
                    
                    def update_progress(current, total, claim_preview):
                        progress_bar.progress((current + 1) / total)
                        st.write(f"  Checking: {claim_preview}")
                    
                    results = verify_all_claims(claims, update_progress)
                    
                    status.update(label="✅ Analysis complete!", state="complete", expanded=False)
                    
                except Exception as e:
                    status.update(label="❌ Error occurred", state="error")
                    st.error(f"An error occurred: {str(e)}")
                    return
            
            # Display results
            st.markdown("---")
            st.markdown("## 📊 Verification Results")
            
            # Summary statistics
            display_stats(results)
            
            st.markdown("---")
            st.markdown("### 📋 Detailed Results")
            
            # Sort results: False and Inaccurate first
            priority_order = {"False": 0, "Inaccurate": 1, "Unverifiable": 2, "Verified": 3}
            sorted_results = sorted(results, key=lambda x: priority_order.get(x.get("status", ""), 4))
            
            # Display each result
            for i, result in enumerate(sorted_results):
                display_result(result, i)
            
            # Download results as JSON
            st.markdown("---")
            st.download_button(
                label="📥 Download Results (JSON)",
                data=str(results),
                file_name="fact_check_results.json",
                mime="application/json",
                use_container_width=True
            )
    
    else:
        # Placeholder when no file is uploaded
        st.markdown("""
        <div style="text-align: center; padding: 3rem; border: 2px dashed #475569; border-radius: 16px; margin: 2rem 0;">
            <p style="font-size: 3rem; margin: 0;">📄</p>
            <p style="color: #94a3b8; margin: 1rem 0 0 0;">Drop a PDF file above to get started</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
