from typing import Dict, List, Optional, Any
from plugins.base import ASRPlugin
from plugins.whisper_api import WhisperAPIPlugin
from plugins.qwen_asr import QwenASRPlugin
from plugins.local_whisper import LocalWhisperPlugin


class PluginManager:
    """Manager for ASR plugins"""

    def __init__(self):
        self.plugins: Dict[str, ASRPlugin] = {}
        self._load_plugins()

    def _load_plugins(self):
        """Load all available plugins"""
        # Load Whisper API plugin
        whisper_api_plugin = WhisperAPIPlugin()
        self.plugins[whisper_api_plugin.name] = whisper_api_plugin

        # Load Qwen ASR plugin
        qwen_asr_plugin = QwenASRPlugin()
        self.plugins[qwen_asr_plugin.name] = qwen_asr_plugin

        # Load Local Whisper plugin
        local_whisper_plugin = LocalWhisperPlugin()
        self.plugins[local_whisper_plugin.name] = local_whisper_plugin

    def get_plugin(self, name: str) -> Optional[ASRPlugin]:
        """Get a plugin by name"""
        return self.plugins.get(name)

    def get_available_plugins(self) -> List[Dict[str, Any]]:
        """Get list of available plugins with their info"""
        return [
            {
                "name": plugin.name,
                "display_name": plugin.display_name,
                "description": plugin.description,
                "supported_languages": ["auto", "zh", "en", "ja", "ko", "yue"],
                "requires_api_key": hasattr(plugin, "api_key"),
                "requires_api_url": hasattr(plugin, "api_url"),
                "model_parameter": hasattr(plugin, "model"),
            }
            for plugin in self.plugins.values()
        ]

    def get_plugin_names(self) -> List[str]:
        """Get list of available plugin names"""
        return list(self.plugins.keys())

    def validate_plugin_config(self, plugin_name: str, config: Dict) -> bool:
        """Validate configuration for a specific plugin"""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return False
        return plugin.validate_config(config)


# Global plugin manager instance
plugin_manager = PluginManager()
