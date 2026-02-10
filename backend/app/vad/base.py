"""
Base class for VAD providers.

This module defines the abstract base class that all VAD providers
must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from app.core.logger import get_logger

logger = get_logger(__name__)


class VADProvider(ABC):
    """
    Abstract base class for Voice Activity Detection providers.

    VAD providers are responsible for detecting speech segments in audio
    and returning timestamps for those segments.
    """

    def __init__(self, name: str, display_name: str, description: str):
        """
        Initialize the VAD provider.

        Args:
            name: Unique identifier for the VAD provider
            display_name: Human-readable name for display in UI
            description: Description of the VAD provider
        """
        self.name = name
        self.display_name = display_name
        self.description = description
        logger.info(f"Initialized VAD provider: {name}")

    @abstractmethod
    def process_audio(self, audio_path: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process audio file and detect speech segments.

        Args:
            audio_path: Path to the audio file to process
            config: Configuration options for VAD processing

        Returns:
            List of speech segment dictionaries, each containing:
            - start: Start time in seconds
            - end: End time in seconds
            - duration: Duration of the segment in seconds
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate VAD configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        pass

    def reset(self):
        """Reset VAD internal state (if applicable)."""
        pass

    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update provider configuration dynamically.

        Args:
            config: Configuration dictionary with new values
        """
        # Default implementation - subclasses can override
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
        logger.info(f"Updated config for {self.name}: {list(config.keys())}")
