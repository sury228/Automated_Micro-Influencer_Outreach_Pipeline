"""
Profile enrichment module.
Enriches influencer profiles with additional data: content themes,
audience estimates, and platform cross-references.
"""

import logging

logger = logging.getLogger(__name__)


class ProfileEnricher:
    """
    Enrich influencer profiles with additional contextual data.
    Analyzes existing data to derive audience insights and content themes.
    """

    def enrich(self, influencer: dict) -> dict:
        """
        Enrich a single influencer profile with derived data.
        Returns updated dict with enriched fields.
        """
        enriched = dict(influencer)

        # Estimate audience demographics from content/geography signals
        enriched["audience_age"] = self._estimate_audience_age(influencer)
        enriched["audience_gender"] = self._estimate_audience_gender(influencer)

        # Refine content themes if not already set
        if not enriched.get("content_themes"):
            enriched["content_themes"] = self._derive_content_themes(influencer)

        # Estimate engagement quality
        enriched["engagement_quality"] = self._assess_engagement_quality(influencer)

        logger.info(
            f"  Enriched: {influencer.get('name', 'Unknown')} | "
            f"Themes: {enriched.get('content_themes', 'N/A')} | "
            f"Audience: {enriched.get('audience_age', 'N/A')}"
        )

        return enriched

    def enrich_batch(self, influencers: list[dict]) -> list[dict]:
        """Enrich a batch of influencer profiles."""
        logger.info(f"Enriching {len(influencers)} profiles...")
        results = [self.enrich(inf) for inf in influencers]
        logger.info(f"Enrichment complete for {len(results)} profiles")
        return results

    def _estimate_audience_age(self, influencer: dict) -> str:
        """Estimate primary audience age range from content signals."""
        combined = " ".join([
            influencer.get("description", ""),
            influencer.get("content_themes", ""),
            influencer.get("recent_content", ""),
        ]).lower()

        # Educational/tutorial content skews younger
        if any(kw in combined for kw in ["beginner", "learn", "tutorial", "student", "course"]):
            return "18-34"
        # Professional/enterprise content skews older
        elif any(kw in combined for kw in ["enterprise", "business", "leadership", "career", "manager"]):
            return "25-44"
        # General tech content
        elif any(kw in combined for kw in ["tech", "code", "programming", "ai", "data"]):
            return "18-35"
        # Default
        return "18-44"

    def _estimate_audience_gender(self, influencer: dict) -> str:
        """Estimate audience gender distribution from content signals."""
        # Tech/AI content typically skews male but is becoming more diverse
        niche = influencer.get("niche", "").lower()
        if any(kw in niche for kw in ["beauty", "skincare", "fashion"]):
            return "Primarily Female"
        elif any(kw in niche for kw in ["gaming", "crypto"]):
            return "Primarily Male"
        elif any(kw in niche for kw in ["tech", "ai", "programming"]):
            return "Male-leaning, Growing Female"
        return "Mixed"

    def _derive_content_themes(self, influencer: dict) -> str:
        """Derive content themes from available data."""
        combined = " ".join([
            influencer.get("description", ""),
            influencer.get("recent_content", ""),
            influencer.get("name", ""),
        ]).lower()

        themes = []
        theme_map = {
            "AI/ML": ["ai", "machine learning", "deep learning", "neural", "llm", "gpt"],
            "Programming": ["python", "javascript", "coding", "code", "programming"],
            "Data Science": ["data science", "analytics", "pandas", "statistics"],
            "Tech Reviews": ["review", "unboxing", "gadget"],
            "Tutorials": ["tutorial", "how to", "learn", "guide"],
            "Web Dev": ["web", "frontend", "backend", "react", "html"],
            "DevOps/Cloud": ["devops", "docker", "kubernetes", "aws", "cloud"],
            "Career": ["career", "job", "interview", "salary"],
        }

        for theme, keywords in theme_map.items():
            if any(kw in combined for kw in keywords):
                themes.append(theme)

        return ", ".join(themes[:3]) if themes else "Technology"

    def _assess_engagement_quality(self, influencer: dict) -> str:
        """Assess engagement quality based on available metrics."""
        engagement = influencer.get("engagement_rate", 0.0)
        followers = influencer.get("followers", 0)

        if engagement >= 5.0:
            return "Excellent"
        elif engagement >= 3.0:
            return "Good"
        elif engagement >= 1.5:
            return "Average"
        elif engagement > 0:
            return "Below Average"
        else:
            return "Unknown"
