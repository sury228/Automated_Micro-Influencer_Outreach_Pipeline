"""
End-to-end pipeline orchestrator for the Influencer Outreach System.
Connects Discovery -> Filtering -> Enrichment -> AI Personalization -> Sending -> Tracking.
"""

import logging
import time
from typing import Optional

from src.config import TARGET_NICHE, DISCOVERY_TARGET, YOUTUBE_API_KEY, GEMINI_API_KEY
from src.database.models import (
    init_db,
    insert_influencer,
    get_all_influencers,
    get_qualified_influencers,
    get_influencers_for_outreach,
    update_influencer,
    log_pipeline_run,
    complete_pipeline_run,
)
from src.discovery.youtube import YouTubeDiscovery
from src.discovery.scraper import DirectoryScraper
from src.filtering.qualification import InfluencerQualifier
from src.enrichment.profile import ProfileEnricher
from src.enrichment.contact import ContactExtractor
from src.personalization.generator import MessageGenerator
from src.outreach.email_sender import EmailSender
from src.outreach.tracker import OutreachTracker

logger = logging.getLogger(__name__)


class OutreachPipeline:
    """
    Master pipeline orchestrating all stages of the influencer outreach system.
    """

    def __init__(self, simulate_email: bool = True):
        init_db()
        self.simulate_email = simulate_email
        self.tracker = OutreachTracker()

    def run_full_pipeline(self, target_count: int = DISCOVERY_TARGET) -> dict:
        """Run all pipeline stages in sequence."""
        logger.info("=" * 60)
        logger.info("Starting Full Influencer Outreach Pipeline")
        logger.info("=" * 60)

        run_id = log_pipeline_run("FULL_PIPELINE")
        start_time = time.time()

        try:
            # Stage 1: Discovery
            logger.info("\n--- STAGE 1: INFLUENCER DISCOVERY ---")
            discovered = self.run_discovery(target_count)

            # Stage 2: Qualification & Filtering
            logger.info("\n--- STAGE 2: FILTERING & QUALIFICATION ---")
            qualified = self.run_qualification()

            # Stage 3: Profile Enrichment & Contact Extraction
            logger.info("\n--- STAGE 3: PROFILE ENRICHMENT & CONTACT EXTRACTION ---")
            enriched = self.run_enrichment()

            # Stage 4: AI Personalization
            logger.info("\n--- STAGE 4: AI MESSAGE PERSONALIZATION ---")
            messages = self.run_personalization()

            # Stage 5: Sending Layer
            logger.info("\n--- STAGE 5: OUTREACH SENDING LAYER ---")
            outreach = self.run_outreach()

            # Stage 6: Export Tracking Data
            logger.info("\n--- STAGE 6: EXPORT & TRACKING ---")
            exports = self.tracker.export_all()

            duration = round(time.time() - start_time, 2)
            complete_pipeline_run(run_id, "SUCCESS", len(discovered))

            logger.info("=" * 60)
            logger.info(f"Pipeline Completed Successfully in {duration}s!")
            logger.info("=" * 60)
            self.tracker.print_summary()

            return {
                "success": True,
                "duration": duration,
                "discovered": len(discovered),
                "qualified": len(qualified),
                "messages_generated": len(messages),
                "emails_sent": outreach.get("sent", 0),
                "exports": exports,
            }

        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}", exc_info=True)
            complete_pipeline_run(run_id, "FAILED", 0, str(e))
            return {"success": False, "error": str(e)}

    def run_discovery(self, target_count: int = DISCOVERY_TARGET) -> list[dict]:
        """Stage 1: Discover micro-influencers from sources."""
        run_id = log_pipeline_run("DISCOVERY")
        discovered_records = []

        # Try YouTube discovery first if key is available
        if YOUTUBE_API_KEY:
            try:
                yt_discovery = YouTubeDiscovery(TARGET_NICHE, target_count)
                yt_records = yt_discovery.discover()
                discovered_records.extend(yt_records)
            except Exception as e:
                logger.error(f"YouTube discovery failed: {e}")

        # Supplement with web directory scraping if needed
        if len(discovered_records) < target_count:
            try:
                remaining = target_count - len(discovered_records)
                scraper = DirectoryScraper(TARGET_NICHE, remaining)
                scraped_records = scraper.discover()
                discovered_records.extend(scraped_records)
            except Exception as e:
                logger.error(f"Directory scraping failed: {e}")

        # Save to database
        saved_count = 0
        for record in discovered_records:
            inf_id = insert_influencer(record)
            if inf_id:
                saved_count += 1

        complete_pipeline_run(run_id, "SUCCESS", saved_count)
        self.tracker.export_discovered_csv()
        return get_all_influencers()

    def run_qualification(self) -> list[dict]:
        """Stage 2: Filter and qualify discovered influencers."""
        run_id = log_pipeline_run("QUALIFICATION")
        influencers = get_all_influencers()

        qualifier = InfluencerQualifier(target_niche=TARGET_NICHE)
        qualified_records = qualifier.qualify_batch(influencers)

        # Update database with qualification verdicts
        for inf in qualified_records:
            if "id" in inf:
                update_influencer(inf["id"], {
                    "qualification_status": inf["qualification_status"],
                    "qualification_reason": inf["qualification_reason"],
                })

        complete_pipeline_run(run_id, "SUCCESS", len(qualified_records))
        self.tracker.export_qualified_csv()
        return get_qualified_influencers()

    def run_enrichment(self) -> list[dict]:
        """Stage 3: Enrich profiles and extract emails."""
        run_id = log_pipeline_run("ENRICHMENT")
        qualified = get_qualified_influencers()

        enricher = ProfileEnricher()
        extractor = ContactExtractor()

        enriched = enricher.enrich_batch(qualified)
        with_contacts = extractor.extract_batch(enriched)

        # Save updates to database
        for inf in with_contacts:
            if "id" in inf:
                update_influencer(inf["id"], {
                    "email": inf.get("email", "Not Found"),
                    "content_themes": inf.get("content_themes", ""),
                    "audience_age": inf.get("audience_age", ""),
                    "audience_gender": inf.get("audience_gender", ""),
                })

        complete_pipeline_run(run_id, "SUCCESS", len(with_contacts))
        return get_qualified_influencers()

    def run_personalization(self) -> list[dict]:
        """Stage 4: Generate personalized LLM outreach messages."""
        run_id = log_pipeline_run("PERSONALIZATION")
        qualified = get_qualified_influencers()

        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set. Using fallback message generator.")

        generator = MessageGenerator()
        personalized = generator.generate_batch(qualified)

        for inf in personalized:
            if "id" in inf:
                update_influencer(inf["id"], {
                    "email_message": inf.get("email_message", ""),
                    "instagram_dm": inf.get("instagram_dm", ""),
                    "message_generated": inf.get("message_generated", 0),
                })

        complete_pipeline_run(run_id, "SUCCESS", len(personalized))
        self.tracker.export_personalized_messages_csv()
        return [inf for inf in personalized if inf.get("message_generated")]

    def run_outreach(self) -> dict:
        """Stage 5: Send email outreach and log results."""
        run_id = log_pipeline_run("OUTREACH")
        target_influencers = get_influencers_for_outreach()

        sender = EmailSender(simulate=self.simulate_email)
        results = sender.send_batch(target_influencers)

        complete_pipeline_run(run_id, "SUCCESS", results.get("sent", 0))
        self.tracker.export_outreach_log_csv()
        return results
