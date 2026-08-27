"""
Configuration parameters for the Influencer Outreach System.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Project Paths ---
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
DB_PATH = PROJECT_ROOT / "data" / "outreach.db"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# --- API Keys ---
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --- Email (SMTP) ---
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# --- Discovery Configuration ---
TARGET_NICHE = os.getenv("TARGET_NICHE", "Technology/AI")
MIN_FOLLOWERS = int(os.getenv("MIN_FOLLOWERS", "5000"))
MAX_FOLLOWERS = int(os.getenv("MAX_FOLLOWERS", "100000"))
MIN_ENGAGEMENT_RATE = float(os.getenv("MIN_ENGAGEMENT_RATE", "2.0"))
DISCOVERY_TARGET = int(os.getenv("DISCOVERY_TARGET", "50"))

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
