"""
VAD Provider Manager.

This module provides a centralized manager for VAD providers, handling
provider discovery, loading, and validation.
"""

from typing import List, Dict, Any, Optional

from app.vad.base import VADProvider
from app.vad.silero import SileroVADProvider
from app.core.logger import get_logger

logger = get_logger(__name__)


class VADManager:
    """
    Manager for VAD providers.

    Handles provider loading, retrieval, and configuration validation.
    """

    def __init__(self):
        """Initialize the VAD manager and load available providers."""
        self._providers: Dict[str, VADProvider] = {}
        self._load_providers()

    def _load_providers(self) -> None:
        """
        Load all available VAD providers.

        Silero VAD is always available. TEN VAD is loaded if its dependencies
        are available, otherwise a warning is logged.
        """
        # Silero VAD is always available
        self._providers["silero"] = SileroVADProvider()
        logger.info("Loaded Silero VAD provider")

        # Try to load TEN VAD (may fail if dependencies not available)
        try:
            from app.vad.ten import TenVADProvider

            self._providers["ten"] = TenVADProvider()
            logger.info("Loaded TEN VAD provider")
        except Exception as e:
            logger.warning(f"TEN VAD provider not available: {e}")

    def get_provider(self, name: str) -> Optional[VADProvider]:
        """
        Get a VAD provider by name.

        Args:
            name: The name of the provider to retrieve.

        Returns:
            The VAD provider instance, or None if not found.
        """
        return self._providers.get(name)

    def get_available_providers(self) -> List[Dict[str, str]]:
        """
        Get information about all available providers.

        Returns:
            List of dictionaries containing provider information:
            - name: Unique identifier for the provider
            - display_name: Human-readable name
            - description: Description of the provider
        """
        providers = []
        for provider in self._providers.values():
            providers.append({
                "name": provider.name,
                "display_name": provider.display_name,
                "description": provider.description,
            })
        return providers

    def get_provider_names(self) -> List[str]:
        """
        Get list of available provider names.

        Returns:
            List of provider name strings.
        """
        return list(self._providers.keys())

    def validate_provider_config(self, provider_name: str, config: Dict[str, Any]) -> bool:
        """
        Validate configuration for a specific provider.

        Args:
            provider_name: The name of the provider.
            config: Configuration dictionary to validate.

        Returns:
            True if configuration is valid, False otherwise.
        """
        provider = self.get_provider(provider_name)
        if provider is None:
            logger.warning(f"Unknown provider: {provider_name}")
            return False
        return provider.validate_config(config)


# Global singleton instance
vad_manager = VADManager()
