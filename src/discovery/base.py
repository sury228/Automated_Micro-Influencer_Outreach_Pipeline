"""
Base discovery interface for influencer discovery agents.
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseDiscovery(ABC):
    """Abstract base class for influencer discovery sources."""

    def __init__(self, niche: str, target_count: int = 50):
        self.niche = niche
        self.target_count = target_count
        self.discovered = []

    @abstractmethod
    def discover(self) -> list[dict]:
        """
        Discover influencers from the source.
        Returns a list of dicts with influencer data.
        """
        pass

    def _validate_record(self, record: dict) -> bool:
        """Validate that a record has minimum required fields."""
        required = ["name", "platform", "profile_url"]
        for field in required:
            if not record.get(field):
                logger.warning(f"Skipping record missing '{field}': {record.get('name', 'unknown')}")
                return False
        return True
