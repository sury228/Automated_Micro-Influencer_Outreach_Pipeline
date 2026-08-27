"""
Web scraper for supplementing influencer discovery from public directories.
Uses requests + BeautifulSoup to scrape permitted public sources.
"""

import re
import logging
import time
import requests
from bs4 import BeautifulSoup
from typing import Optional

from src.discovery.base import BaseDiscovery

logger = logging.getLogger(__name__)

# Common headers to avoid blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


class DirectoryScraper(BaseDiscovery):
    """
    Scrape public influencer directories and creator pages.
    This is a supplementary discovery source to YouTube API.
    """

    def __init__(self, niche: str, target_count: int = 20):
        super().__init__(niche, target_count)
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def discover(self) -> list[dict]:
        """
        Discover influencers from public directory sources.
        Uses GitHub awesome lists and public creator databases.
        """
        logger.info(f"Starting directory scraping for niche: {self.niche}")

        # Scrape from public GitHub awesome lists for tech/AI creators
        sources = self._get_sources_for_niche()

        for source_name, source_url in sources:
            if len(self.discovered) >= self.target_count:
                break

            logger.info(f"Scraping source: {source_name}")
            try:
                profiles = self._scrape_source(source_url, source_name)
                for profile in profiles:
                    if len(self.discovered) >= self.target_count:
                        break
                    if self._validate_record(profile):
                        self.discovered.append(profile)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
                continue

        logger.info(f"Directory scraping complete: {len(self.discovered)} influencers found")
        return self.discovered

    def _get_sources_for_niche(self) -> list[tuple]:
        """Get list of sources for the configured niche."""
        # These are public, freely accessible pages
        sources = [
            ("GitHub Tech YouTubers", "https://raw.githubusercontent.com/JoseDeFreitas/awesome-youtubers/main/readme.md"),
        ]
        return sources

    def _scrape_source(self, url: str, source_name: str) -> list[dict]:
        """Scrape a single source URL."""
        profiles = []

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            content = response.text

            if "github" in url.lower() and url.endswith(".md"):
                profiles = self._parse_github_awesome_list(content)
            else:
                profiles = self._parse_html_directory(content)

        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")

        return profiles

    def _parse_github_awesome_list(self, markdown_content: str) -> list[dict]:
        """Parse a GitHub awesome-youtubers style markdown list."""
        profiles = []

        # Pattern to match YouTube channel links
        yt_pattern = re.compile(
            r'\[([^\]]+)\]\((https?://(?:www\.)?youtube\.com/(?:c/|channel/|@|user/)[^\s\)]+)\)',
            re.IGNORECASE
        )

        matches = yt_pattern.findall(markdown_content)

        for name, url in matches:
            name = name.strip()
            url = url.strip().rstrip(')')

            if not name or len(name) < 2:
                continue

            # Skip common non-channel links
            if any(skip in name.lower() for skip in ["badge", "icon", "logo", "link", "subscribe"]):
                continue

            profile = {
                "name": name,
                "platform": "YouTube",
                "profile_url": url,
                "followers": 0,
                "subscriber_count": 0,
                "engagement_rate": 0.0,
                "niche": self.niche,
                "content_themes": "Technology",
                "email": "Not Found",
                "website": "",
                "instagram_url": "",
                "youtube_url": url,
                "tiktok_url": "",
                "description": f"Discovered from {self.niche} creator directory",
                "recent_content": "",
                "video_count": 0,
                "avg_views": 0,
                "audience_age": "",
                "audience_gender": "",
                "audience_geography": "",
            }

            profiles.append(profile)
            logger.info(f"  Found from directory: {name}")

        return profiles

    def _parse_html_directory(self, html_content: str) -> list[dict]:
        """Parse an HTML directory page for influencer profiles."""
        profiles = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Look for links to YouTube, Instagram, TikTok profiles
        social_links = soup.find_all("a", href=re.compile(
            r"(youtube\.com|instagram\.com|tiktok\.com)",
            re.IGNORECASE
        ))

        for link in social_links:
            url = link.get("href", "")
            name = link.get_text(strip=True)

            if not name or len(name) < 2:
                continue

            platform = "YouTube"
            if "instagram.com" in url:
                platform = "Instagram"
            elif "tiktok.com" in url:
                platform = "TikTok"

            profile = {
                "name": name,
                "platform": platform,
                "profile_url": url,
                "followers": 0,
                "subscriber_count": 0,
                "engagement_rate": 0.0,
                "niche": self.niche,
                "content_themes": "Technology",
                "email": "Not Found",
                "website": "",
                "instagram_url": url if platform == "Instagram" else "",
                "youtube_url": url if platform == "YouTube" else "",
                "tiktok_url": url if platform == "TikTok" else "",
                "description": "",
                "recent_content": "",
                "video_count": 0,
                "avg_views": 0,
                "audience_age": "",
                "audience_gender": "",
                "audience_geography": "",
            }

            profiles.append(profile)

        return profiles
