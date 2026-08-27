"""
YouTube Data API v3 based influencer discovery.
Searches for channels in the target niche and extracts profile data.
"""

import re
import logging
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config import YOUTUBE_API_KEY, SEARCH_KEYWORDS, MIN_FOLLOWERS, MAX_FOLLOWERS
from src.discovery.base import BaseDiscovery

logger = logging.getLogger(__name__)


class YouTubeDiscovery(BaseDiscovery):
    """Discover micro-influencers via YouTube Data API v3."""

    def __init__(self, niche: str, target_count: int = 50):
        super().__init__(niche, target_count)
        if not YOUTUBE_API_KEY:
            raise ValueError("YOUTUBE_API_KEY not set. Please add it to your .env file.")
        self.youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        self.seen_channel_ids = set()

    def discover(self) -> list[dict]:
        """Discover influencers by searching YouTube for niche keywords."""
        logger.info(f"Starting YouTube discovery for niche: {self.niche}")
        logger.info(f"Target: {self.target_count} influencers")

        for keyword in SEARCH_KEYWORDS:
            if len(self.discovered) >= self.target_count:
                break

            logger.info(f"Searching keyword: '{keyword}' ({len(self.discovered)}/{self.target_count} found)")

            try:
                self._search_keyword(keyword)
            except HttpError as e:
                logger.error(f"YouTube API error for '{keyword}': {e}")
                if "quotaExceeded" in str(e):
                    logger.error("YouTube API quota exceeded. Stopping discovery.")
                    break
                continue
            except Exception as e:
                logger.error(f"Unexpected error for '{keyword}': {e}")
                continue

        logger.info(f"YouTube discovery complete: {len(self.discovered)} influencers found")
        return self.discovered

    def _search_keyword(self, keyword: str):
        """Search YouTube for a keyword and extract channel data."""
        next_page_token = None

        for _ in range(3):  # Max 3 pages per keyword
            if len(self.discovered) >= self.target_count:
                break

            request = self.youtube.search().list(
                q=keyword,
                part="snippet",
                type="channel",
                maxResults=25,
                order="relevance",
                pageToken=next_page_token,
            )
            response = request.execute()

            for item in response.get("items", []):
                if len(self.discovered) >= self.target_count:
                    break

                channel_id = item["snippet"]["channelId"]
                if channel_id in self.seen_channel_ids:
                    continue
                self.seen_channel_ids.add(channel_id)

                channel_data = self._get_channel_details(channel_id)
                if channel_data and self._validate_record(channel_data):
                    self.discovered.append(channel_data)

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

    def _get_channel_details(self, channel_id: str) -> Optional[dict]:
        """Fetch detailed channel information."""
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics,brandingSettings",
                id=channel_id,
            )
            response = request.execute()

            if not response.get("items"):
                return None

            channel = response["items"][0]
            snippet = channel.get("snippet", {})
            stats = channel.get("statistics", {})
            branding = channel.get("brandingSettings", {}).get("channel", {})

            subscriber_count = int(stats.get("subscriberCount", 0))
            video_count = int(stats.get("videoCount", 0))
            view_count = int(stats.get("viewCount", 0))

            # Calculate average views and engagement rate
            avg_views = view_count // video_count if video_count > 0 else 0
            engagement_rate = (avg_views / subscriber_count * 100) if subscriber_count > 0 else 0.0

            # Extract email from description
            description = snippet.get("description", "")
            email = self._extract_email(description)

            # Extract social links from description
            instagram_url = self._extract_instagram(description)
            website = self._extract_website(description)

            # Get recent video titles for content themes
            recent_content = self._get_recent_videos(channel_id)

            # Determine content themes from video titles and description
            content_themes = self._analyze_content_themes(description, recent_content)

            record = {
                "name": snippet.get("title", ""),
                "platform": "YouTube",
                "profile_url": f"https://www.youtube.com/channel/{channel_id}",
                "followers": subscriber_count,
                "subscriber_count": subscriber_count,
                "engagement_rate": round(engagement_rate, 2),
                "niche": self.niche,
                "content_themes": content_themes,
                "email": email if email else "Not Found",
                "website": website,
                "instagram_url": instagram_url,
                "youtube_url": f"https://www.youtube.com/channel/{channel_id}",
                "tiktok_url": "",
                "description": description[:500],
                "recent_content": recent_content,
                "video_count": video_count,
                "avg_views": avg_views,
                "audience_age": "",
                "audience_gender": "",
                "audience_geography": branding.get("country", ""),
            }

            logger.info(
                f"  Found: {record['name']} | "
                f"Subs: {subscriber_count:,} | "
                f"Eng: {engagement_rate:.1f}% | "
                f"Email: {'✓' if email else '✗'}"
            )

            return record

        except HttpError as e:
            logger.error(f"Error fetching channel {channel_id}: {e}")
            return None

    def _get_recent_videos(self, channel_id: str, max_results: int = 5) -> str:
        """Get recent video titles from a channel."""
        try:
            request = self.youtube.search().list(
                channelId=channel_id,
                part="snippet",
                order="date",
                maxResults=max_results,
                type="video",
            )
            response = request.execute()

            titles = []
            for item in response.get("items", []):
                title = item["snippet"]["title"]
                titles.append(title)

            return " | ".join(titles) if titles else ""

        except HttpError:
            return ""

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        email_pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
        matches = re.findall(email_pattern, text)
        # Filter out common non-personal emails
        for match in matches:
            lower = match.lower()
            if not any(skip in lower for skip in ["example.com", "email.com", "youremail"]):
                return match
        return None

    def _extract_instagram(self, text: str) -> str:
        """Extract Instagram URL from text."""
        patterns = [
            r'(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9_.]+)',
            r'@([a-zA-Z0-9_.]+)\s*(?:on\s+)?(?:instagram|ig|insta)',
            r'(?:instagram|ig|insta)\s*[:\-]?\s*@?([a-zA-Z0-9_.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                username = match.group(1)
                return f"https://instagram.com/{username}"
        return ""

    def _extract_website(self, text: str) -> str:
        """Extract website URL from text."""
        url_pattern = r'https?://(?:www\.)?(?!(?:youtube|instagram|twitter|facebook|tiktok|t\.co)\.)[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}[^\s]*'
        match = re.search(url_pattern, text)
        return match.group(0) if match else ""

    def _analyze_content_themes(self, description: str, recent_content: str) -> str:
        """Analyze content themes from description and recent videos."""
        combined = f"{description} {recent_content}".lower()

        theme_keywords = {
            "AI/ML": ["ai", "artificial intelligence", "machine learning", "deep learning", "neural network"],
            "Programming": ["python", "javascript", "coding", "programming", "developer", "code"],
            "Data Science": ["data science", "data analysis", "analytics", "pandas", "statistics"],
            "Tech Reviews": ["review", "unboxing", "gadget", "tech", "smartphone", "laptop"],
            "Tutorials": ["tutorial", "how to", "learn", "beginner", "guide", "course"],
            "Automation": ["automation", "automate", "workflow", "no-code", "n8n", "zapier"],
            "Cybersecurity": ["security", "hacking", "cybersecurity", "privacy", "ethical hacking"],
            "Cloud/DevOps": ["cloud", "aws", "azure", "devops", "docker", "kubernetes"],
            "Web Development": ["web", "frontend", "backend", "react", "html", "css"],
            "Career/Education": ["career", "job", "interview", "salary", "education", "university"],
        }

        detected_themes = []
        for theme, keywords in theme_keywords.items():
            if any(kw in combined for kw in keywords):
                detected_themes.append(theme)

        return ", ".join(detected_themes[:4]) if detected_themes else "Technology"
