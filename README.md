# Automated Micro-Influencer Outreach System

An end-to-end, AI-powered system that discovers relevant micro-influencers, filters and classifies them based on quantitative criteria, enriches their profiles, generates personalized collaboration messages using Large Language Models (Google Gemini), and manages outreach tracking.

---

## 🏗️ System Architecture

```
                    ┌─────────────────────────┐
                    │   Influencer Discovery  │
                    │ YouTube Data API / Web  │
                    └────────────┬────────────┘
                                 │ 50+ Profiles
                                 ↓
                    ┌─────────────────────────┐
                    │ Filtering & Audit Engine│
                    │ 5K–100K Subs | 2%+ Eng  │
                    └────────────┬────────────┘
                                 │ Qualified List
                                 ↓
                    ┌─────────────────────────┐
                    │   Profile Enrichment    │
                    │ Contact Email + Themes  │
                    └────────────┬────────────┘
                                 │ Enriched Records
                                 ↓
                    ┌─────────────────────────┐
                    │ AI Personalization (LLM)│
                    │ Custom Email Pitch + DM │
                    └────────────┬────────────┘
                                 │ Unique Messages
                                 ↓
                    ┌─────────────────────────┐
                    │  Outreach Sending Layer │
                    │ Gmail SMTP / Simulation │
                    └────────────┬────────────┘
                                 │ Delivery Logs
                                 ↓
                    ┌─────────────────────────┐
                    │ Outreach Tracker & DB   │
                    │ SQLite + CSV Exports    │
                    └─────────────────────────┘
```

---

## 🛠️ Technology Stack

| Component | Technology / Tool |
|---|---|
| **Language** | Python 3.10+ |
| **Discovery** | YouTube Data API v3, BeautifulSoup4, requests |
| **Data Processing** | Pandas, Pydantic |
| **Database** | SQLite3 (WAL mode, Foreign Keys) |
| **Filtering Engine** | Python rule-based qualification logic |
| **LLM Personalization**| Google Gemini API (`gemini-2.0-flash`) |
| **Outreach / Email** | `smtplib`, Gmail SMTP (Simulation mode fallback) |
| **Dashboard** | Streamlit |
| **Configuration** | `python-dotenv` |

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/your-username/influencer-outreach-system.git
cd influencer-outreach-system
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and fill in your API credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```ini
YOUTUBE_API_KEY=your_youtube_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
TARGET_NICHE=Technology/AI
```

> **Note:** If API keys are omitted, the system will automatically populate and run using a realistic **50-influencer demonstration dataset**.

### 3. Run Pipeline via CLI

To run the complete end-to-end pipeline:

```bash
python run.py --action full
```

To populate the demonstration dataset (50 micro-influencers):

```bash
python run.py --action demo-data
```

Individual pipeline stage commands:
```bash
python run.py --action discover      # Stage 1: Discovery only
python run.py --action qualify       # Stage 2: Qualification only
python run.py --action enrich        # Stage 3: Enrichment & Contact Extraction
python run.py --action personalize   # Stage 4: AI Message Personalization
python run.py --action send          # Stage 5: Outreach Sending
python run.py --action stats         # View summary statistics
```

### 4. Launch Interactive Streamlit Dashboard

To launch the web dashboard:

```bash
streamlit run dashboard/app.py
```

Features included in the dashboard:
- **Overview & Analytics:** Pipeline metrics, status distribution, subscriber breakdown
- **Discovered Influencers:** Searchable, filterable table of all 50+ records
- **Filtering & Classification:** Audit log breakdown explaining why creators passed/failed
- **AI Personalization Preview:** Side-by-side preview of generated email pitches and Instagram DMs
- **Outreach Tracker:** Sent/Failed status log with timestamp tracking

---

## 🔍 Detailed Component Descriptions

### 1. Influencer Discovery (`src/discovery/`)
- Searches YouTube Data API v3 for creators in the configured niche (default: **Technology/AI**) across 15+ search queries.
- Extracts channel name, subscriber count, total video count, description, recent video titles, and country.
- Fallback web scraper collects public creator listings from GitHub directory aggregators.

### 2. Filtering & Classification (`src/filtering/`)
Evaluates each creator against 4 strict criteria:
- **Follower Range:** 5,000 – 100,000 subscribers (Micro-influencer criteria)
- **Engagement Rate:** ≥ 2.0% (calculated from view-to-subscriber ratios)
- **Content Relevance:** Keyword scoring against AI/ML/Software development terminology
- **Contact Email:** Verified contact email present

Outputs a clear **`QUALIFIED`** or **`DISQUALIFIED`** status along with audit logs for every decision.

### 3. Profile Enrichment & Contact Extraction (`src/enrichment/`)
- Extracts business emails from YouTube About pages, descriptions, and linked websites.
- Sets missing emails to **`"Not Found"`** (never fabricates or guesses emails).
- Infers audience age ranges and gender distribution from content signals.
- Extracts core content themes (e.g., *AI/ML, Python, Automation, Web Dev*).

### 4. AI Message Personalization (`src/personalization/`)
Uses **Google Gemini LLM** to generate unique outreach messages for each qualified creator:
- **Email Collaboration Pitch (60–90 words):** References specific video titles, content themes, audience alignment, and proposes a tailored collaboration.
- **Instagram DM (15–30 words):** Short, natural, conversational hook.

### 5. Sending Layer & Outreach Tracker (`src/outreach/`)
- Delivers emails via Gmail SMTP or runs in simulation mode.
- Includes **duplicate prevention** checks against the SQLite log to prevent double-contacting.
- Maintains outreach status (`SENT`, `FAILED`, `DUPLICATE`, `PENDING`).

---

## 📁 Output Artifacts & Dataset Files

All generated datasets are stored in `data/` and `outputs/`:

- `data/discovered_influencers.csv` — All 50+ discovered influencer records
- `data/qualified_influencers.csv` — Shortlisted/qualified micro-influencers
- `outputs/personalized_messages.csv` — AI-generated email pitches & Instagram DMs
- `data/outreach_log.csv` — Outreach sending logs and delivery status
- `data/outreach.db` — SQLite database storing relational records

---

## 🛡️ Ethics, Rate Limiting & Platform Restrictions

- **No Instagram DM Automation Bypass:** The system design explicitly avoids bypassing Meta/Instagram automated DM restrictions. For Instagram DMs, the system generates the personalized DM and stages it for manual review.
- **Respectful Scraping:** Implements rate limits (1-2s delays) and standard user-agent headers.
- **Data Integrity:** Never fabricates emails or engagement metrics. Unavailable data is marked as `"Not Found"`.

---

## 🤝 Project Structure

```
influencer-outreach-system/
├── README.md                         # Documentation
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
├── run.py                            # CLI entry point
├── dashboard/
│   └── app.py                        # Streamlit web app
└── src/
    ├── config.py                     # Configuration & parameters
    ├── pipeline.py                   # Pipeline orchestrator
    ├── database/
    │   └── models.py                 # SQLite schema & database functions
    ├── discovery/
    │   ├── base.py                   # Discovery base class
    │   ├── youtube.py                # YouTube API discovery agent
    │   └── scraper.py                # Web scraper discovery agent
    ├── filtering/
    │   └── qualification.py          # Qualification & audit engine
    ├── enrichment/
    │   ├── profile.py                # Profile enrichment
    │   └── contact.py                # Contact email extractor
    ├── personalization/
    │   ├── prompts.py                # LLM prompts
    │   └── generator.py              # Gemini LLM message generator
    └── outreach/
        ├── email_sender.py           # SMTP email sender & simulator
        └── tracker.py                # Outreach tracker & CSV export
```
