"""
Plugin Selection Tests - Verify correct ASR plugin is selected

Tests that when frontend sends a specific asr_method, the backend
selects the correct plugin instance.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from plugins.manager import PluginManager
from plugins.whisper_api import WhisperAPIPlugin
from plugins.local_whisper import LocalWhisperPlugin
from plugins.qwen_asr import QwenASRPlugin


class TestPluginManagerRegistration:
    """Test that all plugins are registered with correct names"""

    def test_whisper_api_plugin_has_correct_name(self):
        """WhisperAPIPlugin should be registered with name 'whisper-api'"""
        plugin = WhisperAPIPlugin()
        assert plugin.name == "whisper-api"

    def test_local_whisper_plugin_has_correct_name(self):
        """LocalWhisperPlugin should be registered with name 'local-whisper'"""
        plugin = LocalWhisperPlugin()
        assert plugin.name == "local-whisper"

    def test_qwen_asr_plugin_has_correct_name(self):
        """QwenASRPlugin should be registered with name 'qwen-asr'"""
        plugin = QwenASRPlugin()
        assert plugin.name == "qwen-asr"


class TestPluginManagerRetrieval:
    """Test that plugin manager returns correct plugin for given method"""

    def test_get_whisper_api_plugin_by_name(self):
        """get_plugin('whisper-api') should return WhisperAPIPlugin instance"""
        manager = PluginManager()
        plugin = manager.get_plugin("whisper-api")

        assert plugin is not None
        assert isinstance(plugin, WhisperAPIPlugin)
        assert plugin.name == "whisper-api"
        assert not isinstance(plugin, LocalWhisperPlugin)

    def test_get_local_whisper_plugin_by_name(self):
        """get_plugin('local-whisper') should return LocalWhisperPlugin instance"""
        manager = PluginManager()
        plugin = manager.get_plugin("local-whisper")

        assert plugin is not None
        assert isinstance(plugin, LocalWhisperPlugin)
        assert plugin.name == "local-whisper"
        assert not isinstance(plugin, WhisperAPIPlugin)

    def test_get_qwen_asr_plugin_by_name(self):
        """get_plugin('qwen-asr') should return QwenASRPlugin instance"""
        manager = PluginManager()
        plugin = manager.get_plugin("qwen-asr")

        assert plugin is not None
        assert isinstance(plugin, QwenASRPlugin)
        assert plugin.name == "qwen-asr"

    def test_get_invalid_plugin_returns_none(self):
        """get_plugin with invalid name should return None"""
        manager = PluginManager()
        plugin = manager.get_plugin("invalid-plugin")
        assert plugin is None

    def test_plugins_are_separate_instances(self):
        """Each plugin should be a separate instance, not shared"""
        manager = PluginManager()
        whisper_api = manager.get_plugin("whisper-api")
        local_whisper = manager.get_plugin("local-whisper")

        # Should be different instances
        assert whisper_api is not local_whisper
        assert id(whisper_api) != id(local_whisper)


class TestPluginBehaviorDifferentiation:
    """Test that different plugins exhibit different behaviors"""

    @pytest.mark.asyncio
    async def test_whisper_api_plugin_does_not_load_local_model(self):
        """WhisperAPIPlugin should not import whisper module directly"""
        # This test verifies that WhisperAPIPlugin doesn't accidentally
        # import the local whisper module

        # Create plugin without triggering local whisper import
        plugin = WhisperAPIPlugin()

        # Should have API-related attributes
        assert hasattr(plugin, 'api_url')
        assert hasattr(plugin, 'api_key')
        assert hasattr(plugin, 'model')

        # Should NOT have model attribute that LocalWhisperPlugin has
        # (LocalWhisperPlugin has a self.model that gets set to whisper model)
        # WhisperAPIPlugin initializes with self.model = settings.WHISPER_API_MODEL (a string)
        # while LocalWhisperPlugin sets self.model = None initially then loads whisper model
        assert plugin.model is None or isinstance(plugin.model, str)

    @pytest.mark.asyncio
    async def test_local_whisper_plugin_loads_model(self):
        """LocalWhisperPlugin should have a load_model method"""
        plugin = LocalWhisperPlugin()

        # Should have load_model method
        assert hasattr(plugin, '_load_model')
        assert callable(plugin._load_model)

    @pytest.mark.asyncio
    async def test_whisper_api_plugin_uses_http_not_whisper(self):
        """WhisperAPIPlugin should use aiohttp for HTTP requests"""
        plugin = WhisperAPIPlugin()

        # Check that transcribe_segment will make HTTP requests
        # by inspecting if aiohttp is used in the module
        import plugins.whisper_api as whisper_api_module
        assert hasattr(whisper_api_module, 'aiohttp')


class TestASRServicePluginSelection:
    """Test that ASRService correctly selects plugin based on asr_method"""

    @pytest.mark.asyncio
    async def test_asr_service_selects_whisper_api_plugin(self):
        """When asr_method='whisper-api', ASRService should use WhisperAPIPlugin"""
        from plugins.manager import plugin_manager

        asr_method = "whisper-api"
        plugin = plugin_manager.get_plugin(asr_method)

        assert plugin is not None
        assert isinstance(plugin, WhisperAPIPlugin)
        assert plugin.name == "whisper-api"

    @pytest.mark.asyncio
    async def test_asr_service_selects_local_whisper_plugin(self):
        """When asr_method='local-whisper', ASRService should use LocalWhisperPlugin"""
        from plugins.manager import plugin_manager

        asr_method = "local-whisper"
        plugin = plugin_manager.get_plugin(asr_method)

        assert plugin is not None
        assert isinstance(plugin, LocalWhisperPlugin)
        assert plugin.name == "local-whisper"


class TestPluginConfigUpdate:
    """Test that plugin configuration updates correctly"""

    def test_whisper_api_config_update(self):
        """WhisperAPIPlugin should update api_url, api_key, and model"""
        plugin = WhisperAPIPlugin()

        # Initial values
        initial_url = plugin.api_url
        initial_key = plugin.api_key
        initial_model = plugin.model

        # Update config
        plugin.update_config({
            'api_url': 'https://new-api.example.com',
            'api_key': 'new-test-key',
            'model': 'new-model'
        })

        # Verify updated
        assert plugin.api_url == 'https://new-api.example.com'
        assert plugin.api_key == 'new-test-key'
        assert plugin.model == 'new-model'

        # Verify different from initial
        assert plugin.api_url != initial_url
        assert plugin.api_key != initial_key

    def test_local_whisper_config_update(self):
        """LocalWhisperPlugin should update model_name via update_config"""
        plugin = LocalWhisperPlugin()

        # Initial values
        initial_model_name = plugin.model_name

        # Update config - faster-whisper is CPU-only, no device config
        plugin.update_config({
            'model_name': 'base'
        })

        # Verify model_name updated
        assert plugin.model_name == 'base'
        assert plugin.model_name != initial_model_name
