from typing import Dict, List, Optional
from plugins.base import ASRPlugin
from plugins.faster_whisper import FasterWhisperPlugin
from plugins.qwen_asr import QwenASRPlugin


class PluginManager:
    """Manager for ASR plugins"""

    def __init__(self):
        self.plugins: Dict[str, ASRPlugin] = {}
        self._load_plugins()

    def _load_plugins(self):
        """Load all available plugins"""
        # Load Faster Whisper plugin
        faster_whisper_plugin = FasterWhisperPlugin()
        self.plugins[faster_whisper_plugin.name] = faster_whisper_plugin

        # Load Qwen ASR plugin
        qwen_asr_plugin = QwenASRPlugin()
        self.plugins[qwen_asr_plugin.name] = qwen_asr_plugin

    def get_plugin(self, name: str) -> Optional[ASRPlugin]:
        """Get a plugin by name"""
        return self.plugins.get(name)

    def get_available_plugins(self) -> List[str]:
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
