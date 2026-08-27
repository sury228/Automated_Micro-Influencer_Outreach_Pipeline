"""
Contact extraction module.
Attempts to find email addresses for influencers from their online presence.
Never guesses or fabricates emails — marks as "Not Found" if unavailable.
"""

import re
import logging
import time
import requests
from bs4 import BeautifulSoup
from typing import Optional

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
}


class ContactExtractor:
    """
    Extract contact information (primarily email) from influencer profiles.
    Sources: YouTube About page, linked websites, social media bios.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def extract_email(self, influencer: dict) -> str:
        """
        Attempt to find email for an influencer. Returns the email
        or 'Not Found'. Never fabricates addresses.
        """
        # Already have an email?
        existing = influencer.get("email", "")
        if existing and existing != "Not Found" and "@" in existing:
            return existing

        name = influencer.get("name", "Unknown")

        # Try YouTube About page
        youtube_url = influencer.get("youtube_url", "") or influencer.get("profile_url", "")
        if youtube_url and "youtube.com" in youtube_url:
            email = self._try_youtube_about(youtube_url)
            if email:
                logger.info(f"  Email found for {name} via YouTube About: {email}")
                return email

        # Try linked website
        website = influencer.get("website", "")
        if website:
            email = self._try_website(website)
            if email:
                logger.info(f"  Email found for {name} via website: {email}")
                return email

        # Try from description
        description = influencer.get("description", "")
        if description:
            email = self._extract_email_from_text(description)
            if email:
                logger.info(f"  Email found for {name} via description: {email}")
                return email

        logger.info(f"  No email found for {name}")
        return "Not Found"

    def extract_batch(self, influencers: list[dict]) -> list[dict]:
        """Extract emails for a batch of influencers."""
        logger.info(f"Extracting contacts for {len(influencers)} influencers...")
        results = []
        found = 0

        for inf in influencers:
            email = self.extract_email(inf)
            updated = dict(inf)
            updated["email"] = email
            results.append(updated)

            if email != "Not Found":
                found += 1

            time.sleep(0.5)  # Rate limiting

        logger.info(f"Contact extraction complete: {found}/{len(influencers)} emails found")
        return results

    def _try_youtube_about(self, youtube_url: str) -> Optional[str]:
        """Try to extract email from YouTube channel About page."""
        try:
            # Normalize URL to About page
            about_url = youtube_url.rstrip("/") + "/about"
            response = self.session.get(about_url, timeout=10)
            if response.status_code == 200:
                return self._extract_email_from_text(response.text)
        except Exception:
            pass
        return None

    def _try_website(self, website_url: str) -> Optional[str]:
        """Try to extract email from a linked website."""
        try:
            response = self.session.get(website_url, timeout=10)
            if response.status_code == 200:
                # Check common contact pages
                email = self._extract_email_from_text(response.text)
                if email:
                    return email

                # Try /contact page
                soup = BeautifulSoup(response.text, "html.parser")
                contact_links = soup.find_all("a", href=re.compile(r"contact|about", re.I))
                for link in contact_links[:2]:
                    href = link.get("href", "")
                    if href.startswith("/"):
                        href = website_url.rstrip("/") + href
                    elif not href.startswith("http"):
                        continue

                    try:
                        sub_response = self.session.get(href, timeout=10)
                        email = self._extract_email_from_text(sub_response.text)
                        if email:
                            return email
                    except Exception:
                        continue

        except Exception:
            pass
        return None

    def _extract_email_from_text(self, text: str) -> Optional[str]:
        """Extract a valid email address from text."""
        email_pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
        matches = re.findall(email_pattern, text)

        # Filter out common false positives
        skip_patterns = [
            "example.com", "email.com", "youremail", "noreply",
            "sentry.io", "wixpress", "schema.org", "googleapis",
            "w3.org", "privacy", "support@", "info@youtube",
            "creativecommons",
        ]

        for match in matches:
            lower = match.lower()
            if not any(skip in lower for skip in skip_patterns):
                # Basic validation
                if len(match) < 50 and "." in match.split("@")[1]:
                    return match

        return None
