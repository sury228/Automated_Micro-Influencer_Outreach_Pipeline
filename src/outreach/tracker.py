"""
Outreach tracking module.
Exports tracking data to CSV and provides summary statistics.
"""

import csv
import logging
from pathlib import Path

from src.config import DATA_DIR, OUTPUTS_DIR
from src.database.models import get_all_influencers, get_qualified_influencers, get_outreach_logs, get_stats

logger = logging.getLogger(__name__)


class OutreachTracker:
    """Track and export outreach status for all influencers."""

    def export_discovered_csv(self, filepath: Path = None) -> str:
        """Export all discovered influencers to CSV."""
        filepath = filepath or DATA_DIR / "discovered_influencers.csv"
        influencers = get_all_influencers()
        return self._export_influencers_csv(influencers, filepath, "discovered")

    def export_qualified_csv(self, filepath: Path = None) -> str:
        """Export qualified influencers to CSV."""
        filepath = filepath or DATA_DIR / "qualified_influencers.csv"
        influencers = get_qualified_influencers()
        return self._export_influencers_csv(influencers, filepath, "qualified")

    def export_outreach_log_csv(self, filepath: Path = None) -> str:
        """Export outreach log to CSV."""
        filepath = filepath or DATA_DIR / "outreach_log.csv"
        logs = get_outreach_logs()

        if not logs:
            logger.info("No outreach logs to export")
            return str(filepath)

        fieldnames = [
            "name", "platform", "email", "channel",
            "status", "sent_at", "created_at", "error_message",
        ]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for log in logs:
                writer.writerow(log)

        logger.info(f"Exported {len(logs)} outreach logs to {filepath}")
        return str(filepath)

    def export_personalized_messages_csv(self, filepath: Path = None) -> str:
        """Export personalized messages to CSV."""
        filepath = filepath or OUTPUTS_DIR / "personalized_messages.csv"
        influencers = get_qualified_influencers()

        fieldnames = [
            "name", "platform", "email", "followers",
            "engagement_rate", "niche", "content_themes",
            "email_message", "instagram_dm", "message_generated",
        ]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for inf in influencers:
                if inf.get("message_generated"):
                    writer.writerow(inf)

        count = sum(1 for inf in influencers if inf.get("message_generated"))
        logger.info(f"Exported {count} personalized messages to {filepath}")
        return str(filepath)

    def export_all(self) -> dict:
        """Export all CSV files."""
        return {
            "discovered": self.export_discovered_csv(),
            "qualified": self.export_qualified_csv(),
            "outreach_log": self.export_outreach_log_csv(),
            "personalized_messages": self.export_personalized_messages_csv(),
        }

    def print_summary(self):
        """Print a summary of the outreach pipeline."""
        stats = get_stats()

        print("\n" + "=" * 60)
        print("   OUTREACH PIPELINE SUMMARY")
        print("=" * 60)
        print(f"  [*] Total Discovered:       {stats['total_discovered']}")
        print(f"  [+] Qualified:              {stats['qualified']}")
        print(f"  [-] Disqualified:           {stats['disqualified']}")
        print(f"  [~] Pending Qualification:  {stats['pending_qualification']}")
        print(f"  [>] Messages Generated:     {stats['messages_generated']}")
        print(f"  [+] Emails Sent:            {stats['emails_sent']}")
        print(f"  [-] Emails Failed:          {stats['emails_failed']}")
        print(f"  [~] Emails Pending:         {stats['emails_pending']}")
        print("=" * 60)

    def _export_influencers_csv(self, influencers: list[dict], filepath: Path, label: str) -> str:
        """Export influencer list to CSV."""
        if not influencers:
            logger.info(f"No {label} influencers to export")
            return str(filepath)

        fieldnames = [
            "name", "platform", "profile_url", "followers",
            "engagement_rate", "niche", "content_themes", "email",
            "website", "instagram_url", "youtube_url",
            "audience_age", "audience_gender", "audience_geography",
            "qualification_status", "qualification_reason",
            "outreach_status",
        ]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for inf in influencers:
                writer.writerow(inf)

        logger.info(f"Exported {len(influencers)} {label} influencers to {filepath}")
        return str(filepath)
