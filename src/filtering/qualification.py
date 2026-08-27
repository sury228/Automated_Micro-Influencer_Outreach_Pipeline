"""
Influencer filtering and qualification logic.
Applies rule-based criteria to classify influencers as QUALIFIED or DISQUALIFIED.
"""

import logging
from src.config import MIN_FOLLOWERS, MAX_FOLLOWERS, MIN_ENGAGEMENT_RATE, TARGET_NICHE

logger = logging.getLogger(__name__)


class InfluencerQualifier:
    """
    Multi-criteria qualification engine for micro-influencers.
    Evaluates each influencer against configurable rules and produces
    a clear QUALIFIED/DISQUALIFIED verdict with detailed reasons.
    """

    def __init__(
        self,
        min_followers: int = MIN_FOLLOWERS,
        max_followers: int = MAX_FOLLOWERS,
        min_engagement: float = MIN_ENGAGEMENT_RATE,
        target_niche: str = TARGET_NICHE,
    ):
        self.min_followers = min_followers
        self.max_followers = max_followers
        self.min_engagement = min_engagement
        self.target_niche = target_niche

        # Niche keywords for content relevance scoring
        self.niche_keywords = {
            "Technology/AI": [
                "ai", "artificial intelligence", "machine learning", "deep learning",
                "python", "coding", "programming", "tech", "software", "data",
                "automation", "chatgpt", "gpt", "llm", "neural", "algorithm",
                "developer", "computer science", "engineering", "tutorial",
                "javascript", "web development", "cloud", "devops", "api",
            ],
            "Fitness": ["fitness", "workout", "gym", "exercise", "health", "nutrition"],
            "Beauty": ["beauty", "skincare", "makeup", "cosmetic", "hair", "skin"],
            "Fashion": ["fashion", "style", "outfit", "clothing", "trend", "wear"],
            "Gaming": ["gaming", "game", "esports", "gameplay", "streamer", "console"],
            "Fintech": ["fintech", "finance", "banking", "crypto", "investment", "money"],
        }

    def qualify(self, influencer: dict) -> dict:
        """
        Evaluate an influencer against all qualification criteria.

        Returns dict with:
            - status: "QUALIFIED" or "DISQUALIFIED"
            - reasons: list of pass/fail reasons
            - score: numeric score (0-100)
        """
        checks = []
        score = 0

        # --- 1. Follower Count Check ---
        followers = influencer.get("followers", 0) or influencer.get("subscriber_count", 0)
        if followers == 0:
            checks.append(("✗", "Follower count unknown (0)"))
        elif followers < self.min_followers:
            checks.append(("✗", f"Below minimum followers: {followers:,} < {self.min_followers:,}"))
        elif followers > self.max_followers:
            checks.append(("✗", f"Above maximum followers: {followers:,} > {self.max_followers:,}"))
        else:
            checks.append(("✓", f"Follower count in range: {followers:,} (5K–100K)"))
            score += 25

        # --- 2. Engagement Rate Check ---
        engagement = influencer.get("engagement_rate", 0.0)
        if engagement >= self.min_engagement:
            checks.append(("✓", f"Engagement rate: {engagement:.1f}% ≥ {self.min_engagement}%"))
            score += 25
        elif engagement > 0:
            checks.append(("✗", f"Low engagement rate: {engagement:.1f}% < {self.min_engagement}%"))
        else:
            checks.append(("~", "Engagement rate unknown"))
            score += 5  # Partial credit

        # --- 3. Content Relevance Check ---
        relevance_score = self._score_content_relevance(influencer)
        if relevance_score >= 3:
            checks.append(("✓", f"High content relevance (score: {relevance_score}/10)"))
            score += 25
        elif relevance_score >= 1:
            checks.append(("~", f"Moderate content relevance (score: {relevance_score}/10)"))
            score += 10
        else:
            checks.append(("✗", f"Low content relevance (score: {relevance_score}/10)"))

        # --- 4. Contact Email Check ---
        email = influencer.get("email", "")
        if email and email != "Not Found" and "@" in email:
            checks.append(("✓", f"Contact email available: {email}"))
            score += 25
        else:
            checks.append(("~", "Contact email not found"))
            score += 5  # Still eligible but lower priority

        # --- Determine Status ---
        # QUALIFIED if: follower check passes AND (engagement OR relevance passes)
        follower_pass = (self.min_followers <= followers <= self.max_followers) if followers > 0 else False
        engagement_pass = engagement >= self.min_engagement
        relevance_pass = relevance_score >= 1

        if follower_pass and (engagement_pass or relevance_pass):
            status = "QUALIFIED"
        elif followers == 0 and relevance_pass:
            # Unknown followers but relevant content — mark for manual review
            status = "QUALIFIED"
        else:
            status = "DISQUALIFIED"

        reasons_text = "\n".join([f"  {mark} {reason}" for mark, reason in checks])

        result = {
            "qualification_status": status,
            "qualification_reason": reasons_text,
            "qualification_score": score,
        }

        logger.info(
            f"  {status}: {influencer.get('name', 'Unknown')} "
            f"(score: {score}/100, followers: {followers:,}, eng: {engagement:.1f}%)"
        )

        return result

    def _score_content_relevance(self, influencer: dict) -> int:
        """Score content relevance based on keyword matching (0-10)."""
        keywords = self.niche_keywords.get(self.target_niche, [])
        if not keywords:
            return 5  # Default if niche not mapped

        # Combine all text fields for analysis
        text_fields = [
            influencer.get("description", ""),
            influencer.get("content_themes", ""),
            influencer.get("recent_content", ""),
            influencer.get("name", ""),
        ]
        combined = " ".join(text_fields).lower()

        # Count keyword matches
        matches = sum(1 for kw in keywords if kw in combined)

        # Scale to 0-10
        if matches >= 5:
            return 10
        elif matches >= 3:
            return 7
        elif matches >= 2:
            return 5
        elif matches >= 1:
            return 3
        else:
            return 0

    def qualify_batch(self, influencers: list[dict]) -> list[dict]:
        """Qualify a batch of influencers."""
        logger.info(f"Qualifying {len(influencers)} influencers...")

        results = []
        for inf in influencers:
            result = self.qualify(inf)
            results.append({**inf, **result})

        qualified = sum(1 for r in results if r["qualification_status"] == "QUALIFIED")
        logger.info(
            f"Qualification complete: {qualified}/{len(results)} qualified "
            f"({len(results) - qualified} disqualified)"
        )

        return results
