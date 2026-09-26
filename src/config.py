"""
Configuration parameters for the Influencer Outreach System.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_secret(key: str, default: str = "") -> str:
    """Retrieve key from environment variables or Streamlit secrets (for cloud deployment)."""
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default

# --- Project Paths ---
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
DB_PATH = PROJECT_ROOT / "data" / "outreach.db"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# --- API Keys ---
YOUTUBE_API_KEY = get_secret("YOUTUBE_API_KEY", "")
GEMINI_API_KEY = get_secret("GEMINI_API_KEY", "")
GROQ_API_KEY = get_secret("GROQ_API_KEY", "")
LLM_PROVIDER = get_secret("LLM_PROVIDER", "auto")  # "groq", "gemini", or "auto"

# --- Email (SMTP) ---
SMTP_EMAIL = get_secret("SMTP_EMAIL", "")
SMTP_PASSWORD = get_secret("SMTP_PASSWORD", "")
SMTP_HOST = get_secret("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(get_secret("SMTP_PORT", "587"))

# --- Discovery Configuration ---
TARGET_NICHE = get_secret("TARGET_NICHE", "Technology/AI")
MIN_FOLLOWERS = int(get_secret("MIN_FOLLOWERS", "5000"))
MAX_FOLLOWERS = int(get_secret("MAX_FOLLOWERS", "100000"))
MIN_ENGAGEMENT_RATE = float(get_secret("MIN_ENGAGEMENT_RATE", "2.0"))
DISCOVERY_TARGET = int(get_secret("DISCOVERY_TARGET", "50"))

# --- YouTube Search Keywords ---
NICHE_KEYWORDS = {
    "Technology/AI": [
        "artificial intelligence tutorial",
        "machine learning explained",
        "python programming tutorial",
        "AI tools review",
        "deep learning tutorial",
        "data science tutorial",
        "tech review",
        "coding tutorial",
        "AI news",
        "automation tutorial",
        "ChatGPT tutorial",
        "generative AI",
        "LLM tutorial",
        "neural network explained",
        "computer vision tutorial",
    ],
    "Fitness": [
        "home workout",
        "fitness tips",
        "gym routine",
        "nutrition guide",
        "weight loss tips",
    ],
    "Fintech": [
        "fintech explained",
        "digital banking",
        "payment technology",
        "financial technology",
        "investing tips",
    ],
    "Beauty": [
        "skincare routine",
        "makeup tutorial",
        "beauty tips",
        "product review beauty",
        "hair care tips",
    ],
    "Fashion": [
        "outfit ideas",
        "fashion haul",
        "style tips",
        "fashion trends",
        "thrift shopping",
    ],
    "Gaming": [
        "gaming setup",
        "game review",
        "let's play",
        "gaming tips",
        "esports",
    ],
}

# Get keywords for the configured niche
SEARCH_KEYWORDS = NICHE_KEYWORDS.get(TARGET_NICHE, NICHE_KEYWORDS["Technology/AI"])

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
