"""
LLM-based message generator using Google Gemini API.
Generates personalized email pitches and Instagram DMs for each influencer.
"""

import logging
import time
import re
from typing import Optional

import google.generativeai as genai

from src.config import GEMINI_API_KEY
from src.personalization.prompts import EMAIL_PROMPT_TEMPLATE, DM_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class MessageGenerator:
    """
    Generate personalized outreach messages using Google Gemini.
    Each message is unique to the influencer based on their actual data.
    """

    def __init__(self):
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini model: {e}. Using fallback generator.")
                self.model = None
        else:
            logger.info("GEMINI_API_KEY not set. Using intelligent fallback message generator.")
            self.model = None

    def generate_email(self, influencer: dict) -> dict:
        """
        Generate a personalized email pitch for an influencer.
        Returns dict with 'subject' and 'body'.
        """
        if not self.model:
            return self._fallback_email(influencer)

        name = influencer.get("name", "Creator")

        prompt = EMAIL_PROMPT_TEMPLATE.format(
            name=name,
            platform=influencer.get("platform", "YouTube"),
            followers=influencer.get("followers", 0),
            niche=influencer.get("niche", "Technology"),
            content_themes=influencer.get("content_themes", "Technology"),
            engagement_rate=influencer.get("engagement_rate", 0.0),
            recent_content=influencer.get("recent_content", "")[:300],
            description=influencer.get("description", "")[:300],
        )

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Parse subject and body
            subject, body = self._parse_email_response(text, name)

            logger.info(f"  Email generated for {name}: '{subject[:50]}...'")
            return {"subject": subject, "body": body, "full_email": text}

        except Exception as e:
            logger.error(f"  Email generation failed for {name}: {e}")
            return self._fallback_email(influencer)

    def generate_dm(self, influencer: dict) -> str:
        """
        Generate a personalized Instagram DM for an influencer.
        Returns the DM text.
        """
        if not self.model:
            return self._fallback_dm(influencer)

        name = influencer.get("name", "Creator")

        prompt = DM_PROMPT_TEMPLATE.format(
            name=name,
            niche=influencer.get("niche", "Technology"),
            content_themes=influencer.get("content_themes", "Technology"),
            recent_content=influencer.get("recent_content", "")[:200],
            description=influencer.get("description", "")[:200],
        )

        try:
            response = self.model.generate_content(prompt)
            dm_text = response.text.strip().strip('"')

            logger.info(f"  DM generated for {name}: '{dm_text[:50]}...'")
            return dm_text

        except Exception as e:
            logger.error(f"  DM generation failed for {name}: {e}")
            return self._fallback_dm(influencer)

    def generate_messages(self, influencer: dict) -> dict:
        """
        Generate both email and DM for an influencer.
        Returns dict with email_message, instagram_dm, and message_generated flag.
        """
        email_data = self.generate_email(influencer)
        time.sleep(1)  # Rate limiting for API
        dm_text = self.generate_dm(influencer)

        return {
            "email_message": email_data["full_email"],
            "instagram_dm": dm_text,
            "message_generated": 1,
        }

    def generate_batch(self, influencers: list[dict]) -> list[dict]:
        """Generate messages for a batch of influencers."""
        logger.info(f"Generating personalized messages for {len(influencers)} influencers...")
        results = []

        for i, inf in enumerate(influencers):
            logger.info(f"  [{i+1}/{len(influencers)}] Generating messages for {inf.get('name', 'Unknown')}")

            messages = self.generate_messages(inf)
            updated = {**inf, **messages}
            results.append(updated)

            # Rate limiting — 1 second between calls
            if i < len(influencers) - 1:
                time.sleep(1)

        generated = sum(1 for r in results if r.get("message_generated"))
        logger.info(f"Message generation complete: {generated}/{len(influencers)} generated")
        return results

    def _parse_email_response(self, text: str, name: str) -> tuple[str, str]:
        """Parse the LLM response into subject and body."""
        subject = ""
        body = text

        # Try to extract subject line
        subject_match = re.search(r'Subject:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if subject_match:
            subject = subject_match.group(1).strip()
            # Remove subject line from body
            body = text[subject_match.end():].strip()
        else:
            subject = f"Collaboration Opportunity with {name}"

        # Clean up body
        body = body.strip()
        if body.startswith("---"):
            body = body.lstrip("-").strip()

        return subject, body

    def _fallback_email(self, influencer: dict) -> dict:
        """Generate a fallback email if LLM fails."""
        name = influencer.get("name", "Creator").split()[0]
        themes = influencer.get("content_themes", "technology")

        subject = f"Collaboration Opportunity — {influencer.get('name', 'Creator')}"
        body = (
            f"Hi {name},\n\n"
            f"I've been following your {themes} content and really appreciate "
            f"your approach to making complex topics accessible. Your audience "
            f"of {influencer.get('followers', 0):,} engaged followers aligns well "
            f"with our upcoming AI-focused campaign.\n\n"
            f"We'd love to explore a sponsored content or UGC collaboration "
            f"that fits your content style. Would you be open to discussing details?\n\n"
            f"Best,\n[Your Name]"
        )

        return {"subject": subject, "body": body, "full_email": f"Subject: {subject}\n\n{body}"}

    def _fallback_dm(self, influencer: dict) -> str:
        """Generate a fallback DM if LLM fails."""
        name = influencer.get("name", "Creator").split()[0]
        themes = influencer.get("content_themes", "tech")
        return (
            f"Hi {name}! Love your {themes} content. "
            f"Your audience looks like a great fit for our AI campaign. Open to collaborating?"
        )
