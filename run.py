"""
CLI entry point for the Influencer Outreach System.
Allows running the full pipeline, individual stages, or generating demo datasets.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import TARGET_NICHE, YOUTUBE_API_KEY, GEMINI_API_KEY
from src.pipeline import OutreachPipeline
from src.database.models import init_db, clear_all_data, get_stats
from src.outreach.tracker import OutreachTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("run")


def populate_demo_data():
    """Populate sample micro-influencer data for demonstration if API keys are missing."""
    logger.info("Populating demonstration dataset (50 micro-influencers)...")

    from src.database.models import insert_influencer, get_connection

    sample_creators = [
        {
            "name": "Sarah Sharma - AI Explained",
            "platform": "YouTube",
            "profile_url": "https://www.youtube.com/channel/UC_sarah_ai_demo",
            "followers": 42300,
            "subscriber_count": 42300,
            "engagement_rate": 4.8,
            "niche": "Technology/AI",
            "content_themes": "AI/ML, Python, Tutorials",
            "email": "sarah.sharma@example.com",
            "website": "https://sarahai.dev",
            "instagram_url": "https://instagram.com/sarah_ai_tech",
            "youtube_url": "https://www.youtube.com/channel/UC_sarah_ai_demo",
            "description": "Practical machine learning tutorials, Python automation scripts, and beginner-friendly AI explanations.",
            "recent_content": "Build your first LLM Agent with Python | Fine-tuning Llama 3 Tutorial | Top 5 Free AI Tools 2026",
            "video_count": 128,
            "avg_views": 15400,
            "audience_age": "18-34",
            "audience_gender": "Mixed",
            "audience_geography": "United States",
        },
        {
            "name": "Alex Tech & Code",
            "platform": "YouTube",
            "profile_url": "https://www.youtube.com/channel/UC_alex_code_demo",
            "followers": 18500,
            "subscriber_count": 18500,
            "engagement_rate": 6.2,
            "niche": "Technology/AI",
            "content_themes": "Programming, Automation, Web Dev",
            "email": "alex.builds@example.com",
            "website": "https://alexcodes.io",
            "instagram_url": "https://instagram.com/alex_codes",
            "youtube_url": "https://www.youtube.com/channel/UC_alex_code_demo",
            "description": "Coding tutorials, web development walkthroughs, and building AI tools from scratch.",
            "recent_content": "Building a Full-stack AI App in React & FastAPI | Python Web Scraping 101 | n8n Automation Guide",
            "video_count": 64,
            "avg_views": 8200,
            "audience_age": "18-34",
            "audience_gender": "Male-leaning",
            "audience_geography": "Canada",
        },
        {
            "name": "Priya Patel - Data & AI",
            "platform": "YouTube",
            "profile_url": "https://www.youtube.com/channel/UC_priya_data_demo",
            "followers": 76000,
            "subscriber_count": 76000,
            "engagement_rate": 3.5,
            "niche": "Technology/AI",
            "content_themes": "Data Science, AI/ML, Career",
            "email": "priya.data@example.com",
            "website": "https://priyadata.com",
            "instagram_url": "https://instagram.com/priyadata_ai",
            "youtube_url": "https://www.youtube.com/channel/UC_priya_data_demo",
            "description": "Helping you master Data Science and Machine Learning. Career advice, portfolio projects, and code reviews.",
            "recent_content": "How I landed a Data Scientist job | PyTorch vs TensorFlow in 2026 | Complete Pandas Crash Course",
            "video_count": 210,
            "avg_views": 22000,
            "audience_age": "25-44",
            "audience_gender": "Mixed",
            "audience_geography": "India",
        },
        {
            "name": "David Miller - AI Automation",
            "platform": "YouTube",
            "profile_url": "https://www.youtube.com/channel/UC_david_auto_demo",
            "followers": 12400,
            "subscriber_count": 12400,
            "engagement_rate": 7.1,
            "niche": "Technology/AI",
            "content_themes": "Automation, AI Tools, Productivity",
            "email": "david@automations.dev",
            "website": "https://automations.dev",
            "instagram_url": "https://instagram.com/david_automates",
            "youtube_url": "https://www.youtube.com/channel/UC_david_auto_demo",
            "description": "Automating workflows with AI, n8n, Make, and Python. Boost your productivity with smart agents.",
            "recent_content": "Automate 90% of your repetitive tasks with AI | n8n + OpenAI Complete Guide | Custom AI Assistants",
            "video_count": 45,
            "avg_views": 6100,
            "audience_age": "25-44",
            "audience_gender": "Male-leaning",
            "audience_geography": "United Kingdom",
        },
        {
            "name": "Elena Rostova - ML Engineer",
            "platform": "YouTube",
            "profile_url": "https://www.youtube.com/channel/UC_elena_ml_demo",
            "followers": 89000,
            "subscriber_count": 89000,
            "engagement_rate": 2.9,
            "niche": "Technology/AI",
            "content_themes": "AI/ML, Deep Learning, Cloud",
            "email": "elena.ml@example.com",
            "website": "https://elenaml.com",
            "instagram_url": "https://instagram.com/elena_ml_engineer",
            "youtube_url": "https://www.youtube.com/channel/UC_elena_ml_demo",
            "description": "Deep learning research papers explained simply. Computer vision, NLP, and MLOps tutorials.",
            "recent_content": "Transformers Explained from Scratch | Deploying ML Models to AWS | Vision-Language Models Benchmark",
            "video_count": 175,
            "avg_views": 31000,
            "audience_age": "25-44",
            "audience_gender": "Mixed",
            "audience_geography": "Germany",
        },
    ]

    # Generate additional 45 synthetic realistic micro-influencer records
    niche_names = [
        "Tech Bytes with Tom", "Code Craft", "AI Insights", "Neural Networks Daily",
        "Python Power", "DevOps Digest", "Algorithm Academy", "Smart Automation",
        "Generative AI Hub", "Prompt Engineering 101", "Cloud & Code", "Robotics Realm",
        "Data Viz Guy", "Frontend Focused", "Backend Blueprint", "ML Paper Club",
        "CyberSec Simplified", "Future of Tech", "AI Product Reviews", "No-Code AI Builder",
        "Fullstack Mentor", "Data Engineering Lab", "Applied Machine Learning", "Computer Vision Pro",
        "LLM Developer", "Quantum Computing Basics", "AI Ethics & Tech", "Open Source AI",
        "Mobile App Dev", "Rust & WebAssembly", "Go Lang Tech", "Linux & Self-Hosting",
        "AI Hardware Reviews", "Embedded Systems Today", "Database Design Tips", "Software Architect Notes",
        "Microservices Hub", "API First Tech", "Dev Life Vlog", "Tech Career Roadmap",
        "Kaggle Grandmaster Tips", "Deep Tech Daily", "AI Startup Journal", "Edge AI Projects",
        "Agentic AI Studio",
    ]

    for i, name in enumerate(niche_names):
        followers = 5200 + (i * 2100) % 92000
        eng_rate = round(2.1 + ((i * 37) % 55) / 10, 2)
        has_email = (i % 5 != 0)  # 80% have emails
        email = f"{name.lower().replace(' ', '.').replace('&', 'and')[:15]}@example.com" if has_email else "Not Found"

        sample_creators.append({
            "name": name,
            "platform": "YouTube",
            "profile_url": f"https://www.youtube.com/channel/UC_demo_{i+6}",
            "followers": followers,
            "subscriber_count": followers,
            "engagement_rate": eng_rate,
            "niche": "Technology/AI",
            "content_themes": "AI/ML, Programming, Tech",
            "email": email,
            "website": f"https://{name.lower().replace(' ', '')[:12]}.io" if has_email else "",
            "instagram_url": f"https://instagram.com/{name.lower().replace(' ', '_')[:15]}",
            "youtube_url": f"https://www.youtube.com/channel/UC_demo_{i+6}",
            "description": f"{name} creates tutorials and content about AI, programming, and software engineering.",
            "recent_content": f"Latest tech trends | {name} tutorial | AI tools review 2026",
            "video_count": 30 + (i * 7) % 150,
            "avg_views": int(followers * (eng_rate / 100)),
            "audience_age": "18-34" if i % 2 == 0 else "25-44",
            "audience_gender": "Mixed",
            "audience_geography": ["United States", "India", "Germany", "United Kingdom", "Canada"][i % 5],
        })

    for creator in sample_creators:
        insert_influencer(creator)

    logger.info(f"Populated {len(sample_creators)} demonstration influencers in SQLite database!")


def main():
    parser = argparse.ArgumentParser(
        description="Micro-Influencer Discovery & Outreach Pipeline"
    )

    parser.add_argument(
        "--action",
        choices=["full", "discover", "qualify", "enrich", "personalize", "send", "demo-data", "stats", "reset"],
        default="full",
        help="Action to perform (default: full pipeline)",
    )
    parser.add_argument(
        "--target",
        type=int,
        default=50,
        help="Target number of influencers to discover (default: 50)",
    )
    parser.add_argument(
        "--real-email",
        action="store_true",
        help="Send real emails via SMTP instead of simulating (requires SMTP credentials in .env)",
    )

    args = parser.parse_args()

    pipeline = OutreachPipeline(simulate_email=not args.real_email)

    if args.action == "reset":
        clear_all_data()
        print("Database cleared!")
        return

    if args.action == "demo-data":
        clear_all_data()
        populate_demo_data()

        # Run qualification & personalization on demo data
        pipeline.run_qualification()
        pipeline.run_enrichment()
        pipeline.run_personalization()
        pipeline.tracker.export_all()
        pipeline.tracker.print_summary()
        return

    if args.action == "stats":
        pipeline.tracker.print_summary()
        return

    if args.action == "full":
        # Check if database is empty and no API keys are provided
        stats = get_stats()
        if stats["total_discovered"] == 0 and not YOUTUBE_API_KEY:
            logger.info("No API keys found and database is empty. Populating demo data first...")
            populate_demo_data()

        pipeline.run_full_pipeline(target_count=args.target)

    elif args.action == "discover":
        pipeline.run_discovery(target_count=args.target)
    elif args.action == "qualify":
        pipeline.run_qualification()
    elif args.action == "enrich":
        pipeline.run_enrichment()
    elif args.action == "personalize":
        pipeline.run_personalization()
    elif args.action == "send":
        pipeline.run_outreach()


if __name__ == "__main__":
    main()
