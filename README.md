# 🔍 Fact Checker - Claim Verification Web App

A web application that automatically verifies claims from PDF documents against live web data using AI and real-time web search.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

- **PDF Processing**: Drag-and-drop PDF upload with automatic text extraction
- **AI-Powered Claim Extraction**: Identifies verifiable claims (statistics, dates, financial data, etc.)
- **Real-Time Verification**: Cross-references claims against live web data using Tavily Search
- **Smart Classification**: Categorizes each claim as:
  - ✅ **Verified** - Matches current, reliable data
  - ⚠️ **Inaccurate** - Contains outdated or partially incorrect information
  - ❌ **False** - No evidence supports the claim
  - ❓ **Unverifiable** - Cannot determine accuracy
- **Source Citations**: Provides source URLs for every verification
- **Downloadable Reports**: Export results as JSON


## 🚀 Live Demo

**Deployed App**: [Fact Checker App](https://fact-checker-app.streamlit.app/)
## 🔧 How It Works

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  PDF Upload │ -> │ Text Extract │ -> │ Claim       │ -> │ Web Search   │ -> │ Results     │
│             │    │ (pdfplumber) │    │ Extraction  │    │ + Verify     │    │ Display     │
│             │    │              │    │ (LLM)       │    │ (Tavily+LLM) │    │             │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘    └─────────────┘
```

1. **Upload**: User uploads a PDF document
2. **Extract Text**: `pdfplumber` extracts text content from the PDF
3. **Identify Claims**: LLM analyzes text and extracts verifiable claims
4. **Search & Verify**: Each claim is verified against live web data using Tavily Search API
5. **Classify**: LLM compares claims against search results and determines accuracy
6. **Report**: Results displayed with status badges, explanations, and source citations

## 📋 Prerequisites

- Python 3.10+
- OpenRouter API Key ([Get one here](https://openrouter.ai)) - or any OpenAI-compatible API
- Tavily API Key ([Get one here](https://tavily.com)) - Free tier available

## 🛠️ Installation

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/fact-checker.git
   cd fact-checker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys** - Create `.streamlit/secrets.toml`:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-your-openrouter-key"
   OpenAi_API_KEY = "google/gemma-2-9b-it"  # Model to use
   TAVILY_API_KEY = "tvly-your-tavily-key"
   ```

4. **Run the app**:
   ```bash
   streamlit run app.py
   ```

5. Open your browser to `http://localhost:8501`

## ☁️ Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `app.py` as the main file
5. Add your secrets in **Advanced settings**:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-your-key"
   OpenAi_API_KEY = "google/gemma-2-9b-it"
   TAVILY_API_KEY = "tvly-your-key"
   ```
6. Click **Deploy**!

## 📁 Project Structure

```
fact-checker/
├── app.py                 # Main Streamlit application
├── pdf_processor.py       # PDF text extraction module
├── claim_extractor.py     # LLM-based claim identification
├── fact_verifier.py       # Web search & verification engine
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── .streamlit/
    └── secrets.toml.example  # API keys template
```

## 🔑 Configuration

| Secret Key | Description |
|------------|-------------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key for LLM access |
| `OpenAi_API_KEY` | Model name to use (e.g., `google/gemma-2-9b-it`, `openai/gpt-4o`) |
| `TAVILY_API_KEY` | Tavily API key for web search |

## 📊 Example Use Case

Upload a document containing claims like:
- "Bitcoin is trading at $42,500"
- "US unemployment is 6.2%"
- "GPT-5 has been delayed indefinitely"

The app will verify each claim against current web data and flag outdated or false information.

## 📝 License

MIT License - feel free to use this project for any purpose.

---

Built with ❤️ using [Streamlit](https://streamlit.io), [OpenRouter](https://openrouter.ai), and [Tavily](https://tavily.com)

## 👨‍💻 Author

**ARYA YADAV**
