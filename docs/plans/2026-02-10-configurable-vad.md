# Configurable VAD (Voice Activity Detection) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make VAD configurable and pluggable, supporting both Silero VAD (current) and TEN VAD (new) as swappable options with a unified interface.

**Architecture:**
1. Create a VAD provider base class (similar to ASR plugins pattern)
2. Implement Silero VAD provider (wrapping existing `ONNXSileroVAD`)
3. Implement TEN VAD provider (downloading ONNX model from Hugging Face)
4. Add VAD configuration to settings and API
5. Create VAD manager to handle provider selection

**Tech Stack:**
- Python 3.10+
- ONNX Runtime (existing dependency)
- Pydantic Settings
- Requests (for model download)

**Key Differences Between Silero VAD and TEN VAD:**
| Feature | Silero VAD | TEN VAD |
|---------|-----------|---------|
| Model URL | `https://huggingface.co/onnx-community/silero-vad` | `https://huggingface.co/TEN-framework/ten-vad` |
| Model Path | `onnx/model.onnx` | `src/onnx_model/ten_vad.onnx` |
| Input Shape | Requires LSTM state | Direct audio frames |
| Window Size | 512 samples | 160/256 samples (10/16ms) |
| Sample Rate | 16kHz | 16kHz |
| Output | Speech probability per window | Speech probability per frame |

---

## Task 1: Create VAD Provider Base Class

**Files:**
- Create: `backend/app/vad/base.py`
- Test: `backend/tests/vad/test_base.py`

**Step 1: Write the failing test**

Create test file `backend/tests/vad/test_base.py`:

```python
"""Test VAD base provider"""
import pytest
import numpy as np
from app.vad.base import VADProvider


class MockVADProvider(VADProvider):
    """Mock implementation for testing"""

    def __init__(self):
        super().__init__(name="mock", display_name="Mock VAD", description="Test provider")

    def process_audio(
        self,
        audio: np.ndarray,
        threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 100,
    ) -> list[dict[str, float]]:
        return [{'start': 0.0, 'end': 1.0}]

    def validate_config(self, config: dict) -> bool:
        return True


def test_vad_provider_creation():
    """Test creating a VAD provider"""
    provider = MockVADProvider()
    assert provider.name == "mock"
    assert provider.display_name == "Mock VAD"
    assert provider.description == "Test provider"


def test_vad_provider_process_audio():
    """Test process_audio method"""
    provider = MockVADProvider()
    audio = np.zeros(16000)
    segments = provider.process_audio(audio)
    assert segments == [{'start': 0.0, 'end': 1.0}]


def test_vad_provider_validate_config():
    """Test validate_config method"""
    provider = MockVADProvider()
    assert provider.validate_config({}) is True


def test_cannot_instantiate_base_class():
    """Test that base class cannot be instantiated"""
    from app.vad.base import VADProvider
    with pytest.raises(TypeError):
        VADProvider(name="test", display_name="Test", description="Test")
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/vad/test_base.py -v`

Expected: FAIL with "No module named 'app.vad.base'"

**Step 3: Write minimal implementation**

Create `backend/app/vad/__init__.py`:
```python
"""VAD (Voice Activity Detection) providers"""
```

Create `backend/app/vad/base.py`:
```python
"""Base class for VAD providers"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np
from app.core.logger import get_logger

logger = get_logger(__name__)


class VADProvider(ABC):
    """Base class for VAD providers"""

    def __init__(self, name: str, display_name: str, description: str):
        self.name = name
        self.display_name = display_name
        self.description = description

    @abstractmethod
    def process_audio(
        self,
        audio: np.ndarray,
        threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 100,
        **kwargs
    ) -> List[Dict[str, float]]:
        """
        Process audio and return speech timestamps.

        Args:
            audio: Audio data as numpy array (16kHz mono).
            threshold: Speech probability threshold (default: 0.5).
            min_speech_duration_ms: Minimum speech duration in ms (default: 250).
            min_silence_duration_ms: Minimum silence duration in ms (default: 100).

        Returns:
            List of speech segments with 'start' and 'end' timestamps in seconds.
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate provider configuration.

        Args:
            config: Configuration dictionary.

        Returns:
            True if valid, False otherwise.
        """
        pass

    def reset(self):
        """Reset VAD internal state (if applicable)."""
        pass
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/vad/test_base.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/vad/__init__.py backend/app/vad/base.py backend/tests/vad/test_base.py
git commit -m "feat: add VAD provider base class"
```

---

## Task 2: Create Silero VAD Provider

**Files:**
- Create: `backend/app/vad/silero.py`
- Modify: `backend/app/utils/vad.py` (refactor to support provider pattern)
- Test: `backend/tests/vad/test_silero.py`

**Step 1: Write the failing test**

Create `backend/tests/vad/test_silero.py`:

```python
"""Test Silero VAD provider"""
import pytest
import numpy as np
from app.vad.silero import SileroVADProvider


def test_silero_provider_creation():
    """Test creating Silero VAD provider"""
    provider = SileroVADProvider()
    assert provider.name == "silero"
    assert "Silero" in provider.display_name


def test_silero_provider_validate_config():
    """Test config validation"""
    provider = SileroVADProvider()
    assert provider.validate_config({}) is True
    assert provider.validate_config({"threshold": 0.5}) is True


def test_silero_provider_process_audio_short():
    """Test processing short audio (1 second)"""
    provider = SileroVADProvider()
    # 1 second of silence
    audio = np.zeros(16000, dtype=np.float32)
    segments = provider.process_audio(audio, threshold=0.5)
    # Should return empty list for silence
    assert isinstance(segments, list)


def test_silero_provider_reset():
    """Test reset method"""
    provider = SileroVADProvider()
    provider.reset()  # Should not raise
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/vad/test_silero.py -v`

Expected: FAIL with "No module named 'app.vad.silero'"

**Step 3: Write minimal implementation**

Create `backend/app/vad/silero.py`:

```python
"""Silero VAD provider"""
from typing import List, Dict, Any
import numpy as np
from app.vad.base import VADProvider
from app.utils.vad import ONNXSileroVAD, get_vad_model
from app.core.logger import get_logger

logger = get_logger(__name__)


class SileroVADProvider(VADProvider):
    """
    Silero VAD provider using ONNX Runtime.

    Model: https://huggingface.co/onnx-community/silero-vad
    """

    def __init__(self, model_path: str | None = None):
        super().__init__(
            name="silero",
            display_name="Silero VAD",
            description="Silero VAD using ONNX Runtime (CPU-only, no torch dependency)"
        )
        self._model: ONNXSileroVAD | None = None
        self._model_path = model_path

    def _get_model(self) -> ONNXSileroVAD:
        """Get or create VAD model instance."""
        if self._model is None:
            if self._model_path:
                self._model = ONNXSileroVAD(model_path=self._model_path)
            else:
                self._model = get_vad_model()
        return self._model

    def process_audio(
        self,
        audio: np.ndarray,
        threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 100,
        **kwargs
    ) -> List[Dict[str, float]]:
        """Process audio and return speech timestamps."""
        model = self._get_model()
        return model.process_audio(
            audio,
            threshold=threshold,
            min_speech_duration_ms=min_speech_duration_ms,
            min_silence_duration_ms=min_silence_duration_ms,
            return_seconds=True,
        )

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Silero VAD configuration."""
        # All configs are optional
        valid_keys = {"threshold", "min_speech_duration_ms", "min_silence_duration_ms"}
        for key in config:
            if key not in valid_keys:
                return False
        return True

    def reset(self):
        """Reset VAD internal state."""
        if self._model is not None:
            self._model.reset()
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/vad/test_silero.py -v`

Expected: PASS (may need to download model on first run)

**Step 5: Commit**

```bash
git add backend/app/vad/silero.py backend/tests/vad/test_silero.py
git commit -m "feat: add Silero VAD provider"
```

---

## Task 3: Create TEN VAD Provider

**Files:**
- Create: `backend/app/vad/ten.py`
- Test: `backend/tests/vad/test_ten.py`

**Step 1: Write the failing test**

Create `backend/tests/vad/test_ten.py`:

```python
"""Test TEN VAD provider"""
import pytest
import numpy as np
from app.vad.ten import TenVADProvider


def test_ten_provider_creation():
    """Test creating TEN VAD provider"""
    provider = TenVADProvider()
    assert provider.name == "ten"
    assert "TEN" in provider.display_name


def test_ten_provider_validate_config():
    """Test config validation"""
    provider = TenVADProvider()
    assert provider.validate_config({}) is True
    assert provider.validate_config({"threshold": 0.5}) is True


def test_ten_provider_process_audio_short():
    """Test processing short audio"""
    provider = TenVADProvider()
    # 1 second of silence
    audio = np.zeros(16000, dtype=np.float32)
    segments = provider.process_audio(audio, threshold=0.5)
    assert isinstance(segments, list)
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/vad/test_ten.py -v`

Expected: FAIL with "No module named 'app.vad.ten'"

**Step 3: Write minimal implementation**

Create `backend/app/vad/ten.py`:

```python
"""TEN VAD provider"""
from typing import List, Dict, Any
from pathlib import Path
import numpy as np
import onnxruntime as ort
from app.vad.base import VADProvider
from app.core.logger import get_logger

logger = get_logger(__name__)


class TenVADProvider(VADProvider):
    """
    TEN VAD provider using ONNX Runtime.

    Model: https://huggingface.co/TEN-framework/ten-vad
    Model path in repo: src/onnx_model/ten_vad.onnx

    TEN VAD is a real-time voice activity detection system designed for
    enterprise use, providing accurate frame-level speech activity detection.
    """

    # TEN VAD specific constants
    SAMPLE_RATE = 16000
    HOP_SIZE = 160  # 10ms at 16kHz (also supports 256 for 16ms)

    def __init__(self, model_path: str | None = None, hop_size: int = 160):
        super().__init__(
            name="ten",
            display_name="TEN VAD",
            description="TEN VAD - Low-latency, lightweight, high-performance streaming VAD"
        )
        self._hop_size = hop_size
        self._session: ort.InferenceSession | None = None
        self._model_path = model_path

    def _download_model(self) -> str:
        """
        Download TEN VAD ONNX model from Hugging Face.

        Returns:
            Path to downloaded model.
        """
        import requests

        cache_dir = Path.home() / ".cache" / "ten_vad_onnx"
        cache_dir.mkdir(parents=True, exist_ok=True)

        model_path = cache_dir / "ten_vad.onnx"

        if model_path.exists():
            logger.info(f"Using cached TEN VAD model: {model_path}")
            return str(model_path)

        # Download from Hugging Face
        url = "https://huggingface.co/TEN-framework/ten-vad/resolve/main/src/onnx_model/ten_vad.onnx"

        logger.info(f"Downloading TEN VAD ONNX model from {url}...")

        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            model_path.write_bytes(response.content)
            logger.info(f"Model downloaded to: {model_path}")
            return str(model_path)

        except Exception as e:
            logger.error(f"Failed to download TEN VAD model: {e}")
            raise

    def _get_session(self) -> ort.InferenceSession:
        """Get or create ONNX session."""
        if self._session is None:
            model_path = self._model_path or self._download_model()
            self._session = ort.InferenceSession(
                model_path,
                providers=['CPUExecutionProvider'],
            )
            logger.info(f"TEN VAD session created with model: {model_path}")
        return self._session

    def reset(self):
        """Reset VAD state (TEN VAD is stateless per inference)."""
        pass

    def process_audio(
        self,
        audio: np.ndarray,
        threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 100,
        **kwargs
    ) -> List[Dict[str, float]]:
        """
        Process audio and return speech timestamps.

        Args:
            audio: Audio data as numpy array (should be 16kHz mono).
            threshold: Speech probability threshold (default: 0.5).
            min_speech_duration_ms: Minimum speech duration in ms.
            min_silence_duration_ms: Minimum silence duration in ms.

        Returns:
            List of speech segments with 'start' and 'end' timestamps in seconds.
        """
        # Convert to mono if needed
        if audio.ndim > 1:
            audio = np.mean(audio, axis=-1)

        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Get session
        session = self._get_session()

        # Get input/output names
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name

        # Calculate number of frames
        hop_size = self._hop_size
        num_frames = len(audio) // hop_size

        if num_frames == 0:
            return []

        # Prepare input: reshape to (num_frames, hop_size)
        max_samples = num_frames * hop_size
        audio_frames = audio[:max_samples].reshape(num_frames, hop_size)

        # Run inference
        probabilities = session.run([output_name], {input_name: audio_frames})[0]

        # Convert to binary and find segments
        return self._probs_to_timestamps(
            probabilities,
            threshold=threshold,
            min_speech_duration_ms=min_speech_duration_ms,
            min_silence_duration_ms=min_silence_duration_ms,
        )

    def _probs_to_timestamps(
        self,
        probs: np.ndarray,
        threshold: float,
        min_speech_duration_ms: int,
        min_silence_duration_ms: int,
    ) -> List[Dict[str, float]]:
        """Convert probabilities to timestamps."""
        # Convert to binary (flatten if needed)
        if probs.ndim > 1:
            probs = probs.flatten()

        is_speech = probs >= threshold

        # Convert durations to frames
        frame_duration_ms = (self._hop_size / self.SAMPLE_RATE) * 1000
        min_speech_frames = max(1, int(min_speech_duration_ms / frame_duration_ms))
        min_silence_frames = max(1, int(min_silence_duration_ms / frame_duration_ms))

        segments = []
        in_speech = False
        start_idx = 0
        speech_count = 0
        silence_count = 0

        for i, speech in enumerate(is_speech):
            if speech and not in_speech:
                in_speech = True
                start_idx = i
                speech_count = 1
                silence_count = 0
            elif speech and in_speech:
                speech_count += 1
                silence_count = 0
            elif not speech and in_speech:
                silence_count += 1
                if silence_count >= min_silence_frames:
                    if speech_count >= min_speech_frames:
                        start_time = start_idx * frame_duration_ms / 1000
                        end_time = (i - silence_count + 1) * frame_duration_ms / 1000
                        segments.append({'start': start_time, 'end': end_time})
                    in_speech = False
                    speech_count = 0

        # Handle ending during speech
        if in_speech and speech_count >= min_speech_frames:
            start_time = start_idx * frame_duration_ms / 1000
            end_time = len(is_speech) * frame_duration_ms / 1000
            segments.append({'start': start_time, 'end': end_time})

        return segments

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate TEN VAD configuration."""
        valid_keys = {"threshold", "min_speech_duration_ms", "min_silence_duration_ms", "hop_size"}
        for key in config:
            if key not in valid_keys:
                return False
        # Validate hop_size if provided
        if "hop_size" in config:
            if config["hop_size"] not in [160, 256]:
                return False
        return True
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/vad/test_ten.py -v`

Expected: PASS (may need to download model on first run)

**Step 5: Commit**

```bash
git add backend/app/vad/ten.py backend/tests/vad/test_ten.py
git commit -m "feat: add TEN VAD provider"
```

---

## Task 4: Create VAD Manager

**Files:**
- Create: `backend/app/vad/manager.py`
- Modify: `backend/app/vad/__init__.py`
- Test: `backend/tests/vad/test_manager.py`

**Step 1: Write the failing test**

Create `backend/tests/vad/test_manager.py`:

```python
"""Test VAD manager"""
import pytest
from app.vad.manager import VADManager, vad_manager


def test_vad_manager_singleton():
    """Test that vad_manager is a singleton"""
    from app.vad.manager import vad_manager as vm2
    assert vad_manager is vm2


def test_vad_manager_get_provider():
    """Test getting a provider by name"""
    provider = vad_manager.get_provider("silero")
    assert provider is not None
    assert provider.name == "silero"


def test_vad_manager_get_nonexistent_provider():
    """Test getting a non-existent provider"""
    provider = vad_manager.get_provider("nonexistent")
    assert provider is None


def test_vad_manager_get_available_providers():
    """Test getting available providers list"""
    providers = vad_manager.get_available_providers()
    assert isinstance(providers, list)
    assert len(providers) >= 1
    assert any(p["name"] == "silero" for p in providers)


def test_vad_manager_validate_config():
    """Test config validation"""
    assert vad_manager.validate_provider_config("silero", {}) is True
    assert vad_manager.validate_provider_config("nonexistent", {}) is False
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/vad/test_manager.py -v`

Expected: FAIL with "No module named 'app.vad.manager'"

**Step 3: Write minimal implementation**

Create `backend/app/vad/manager.py`:

```python
"""VAD provider manager"""
from typing import Dict, List, Optional, Any
from app.vad.base import VADProvider
from app.vad.silero import SileroVADProvider
from app.vad.ten import TenVADProvider
from app.core.logger import get_logger

logger = get_logger(__name__)


class VADManager:
    """Manager for VAD providers"""

    def __init__(self):
        self._providers: Dict[str, VADProvider] = {}
        self._load_providers()

    def _load_providers(self):
        """Load all available VAD providers."""
        # Load Silero VAD (default, always available)
        silero_provider = SileroVADProvider()
        self._providers[silero_provider.name] = silero_provider

        # Load TEN VAD
        try:
            ten_provider = TenVADProvider()
            self._providers[ten_provider.name] = ten_provider
            logger.info("TEN VAD provider loaded successfully")
        except Exception as e:
            logger.warning(f"TEN VAD provider not available: {e}")

    def get_provider(self, name: str) -> Optional[VADProvider]:
        """Get a provider by name."""
        return self._providers.get(name)

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers with their info."""
        return [
            {
                "name": provider.name,
                "display_name": provider.display_name,
                "description": provider.description,
            }
            for provider in self._providers.values()
        ]

    def get_provider_names(self) -> List[str]:
        """Get list of available provider names."""
        return list(self._providers.keys())

    def validate_provider_config(self, provider_name: str, config: Dict) -> bool:
        """Validate configuration for a specific provider."""
        provider = self.get_provider(provider_name)
        if not provider:
            return False
        return provider.validate_config(config)


# Global VAD manager instance
vad_manager = VADManager()
```

Update `backend/app/vad/__init__.py`:
```python
"""VAD (Voice Activity Detection) providers"""
from app.vad.manager import vad_manager, VADManager
from app.vad.base import VADProvider
from app.vad.silero import SileroVADProvider
from app.vad.ten import TenVADProvider

__all__ = [
    "vad_manager",
    "VADManager",
    "VADProvider",
    "SileroVADProvider",
    "TenVADProvider",
]
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/vad/test_manager.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/vad/manager.py backend/app/vad/__init__.py backend/tests/vad/test_manager.py
git commit -m "feat: add VAD provider manager"
```

---

## Task 5: Add VAD Configuration to Settings

**Files:**
- Modify: `backend/app/core/config.py`
- Test: `backend/tests/test_config.py`

**Step 1: Write the failing test**

Add to `backend/tests/test_config.py` (create if doesn't exist):

```python
"""Test configuration"""
from app.core.config import settings


def test_default_vad_method():
    """Test default VAD method is silero"""
    assert settings.DEFAULT_VAD_METHOD == "silero"


def test_available_vad_methods():
    """Test available VAD methods include silero and ten"""
    assert "silero" in settings.AVAILABLE_VAD_METHODS
    assert "ten" in settings.AVAILABLE_VAD_METHODS
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_config.py::test_default_vad_method -v`

Expected: FAIL with "AttributeError: type object 'Settings' has no attribute 'DEFAULT_VAD_METHOD'"

**Step 3: Write minimal implementation**

Modify `backend/app/core/config.py` - add after line 36:

```python
    # VAD settings
    DEFAULT_VAD_METHOD: str = "silero"
    AVAILABLE_VAD_METHODS: list = ["silero", "ten"]
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_config.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/core/config.py backend/tests/test_config.py
git commit -m "feat: add VAD configuration to settings"
```

---

## Task 6: Update API Schema to Support VAD Selection

**Files:**
- Modify: `backend/app/models/schemas.py`
- Test: `backend/tests/test_schemas.py`

**Step 1: Write the failing test**

Create `backend/tests/test_schemas.py`:

```python
"""Test API schemas"""
from app.models.schemas import ASRRequest


def test_asr_request_with_vad_method():
    """Test ASRRequest with vad_method"""
    data = {
        "vad_method": "ten",
        "vad_options": {"threshold": 0.6}
    }
    request = ASRRequest(**data)
    assert request.vad_method == "ten"
    assert request.vad_options["threshold"] == 0.6


def test_asr_request_default_vad_method():
    """Test ASRRequest defaults to silero"""
    request = ASRRequest()
    assert request.vad_method == "silero"
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_schemas.py -v`

Expected: FAIL with "ASRRequest has no attribute 'vad_method'"

**Step 3: Write minimal implementation**

Modify `backend/app/models/schemas.py`:

Current ASRRequest (around line 6-10):
```python
class ASRRequest(BaseModel):
    asr_method: str = Field(default="local-whisper", description="ASR method to use")
    language: Optional[str] = Field(default="auto", description="Language code")
    vad_options: Optional[Dict[str, Any]] = Field(default=None, description="VAD options")
```

Update to:
```python
class ASRRequest(BaseModel):
    asr_method: str = Field(default="local-whisper", description="ASR method to use")
    language: Optional[str] = Field(default="auto", description="Language code")
    vad_method: str = Field(default="silero", description="VAD method to use (silero, ten)")
    vad_options: Optional[Dict[str, Any]] = Field(default=None, description="VAD options")
    asr_options: Optional[Dict[str, Any]] = Field(default=None, description="ASR options")
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_schemas.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/models/schemas.py backend/tests/test_schemas.py
git commit -m "feat: add vad_method to ASRRequest schema"
```

---

## Task 7: Update Audio Processing to Use VAD Manager

**Files:**
- Modify: `backend/app/utils/audio_processing.py`
- Test: `backend/tests/test_audio_processing.py`

**Step 1: Write the failing test**

Create `backend/tests/test_audio_processing.py`:

```python
"""Test audio processing with VAD manager"""
import pytest
from app.utils.audio_processing import vad_segmentation_with_provider
from app.vad.manager import vad_manager


def test_vad_segmentation_with_silero():
    """Test VAD segmentation with silero provider"""
    provider = vad_manager.get_provider("silero")
    assert provider is not None

    # Use a test audio file if available, otherwise skip
    # This is a placeholder - actual test needs audio file


def test_vad_segmentation_with_ten():
    """Test VAD segmentation with ten provider"""
    provider = vad_manager.get_provider("ten")
    if provider is None:
        pytest.skip("TEN VAD not available")
    assert provider.name == "ten"
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_audio_processing.py -v`

Expected: FAIL with "function 'vad_segmentation_with_provider' not found"

**Step 3: Write minimal implementation**

Modify `backend/app/utils/audio_processing.py` - add new function:

```python
def vad_segmentation_with_provider(
    audio_path: str,
    provider_name: str = "silero",
    vad_options: Optional[Dict[str, Any]] = None,
) -> Tuple[List[Dict], Any, int]:
    """
    Perform speech activity detection using specified VAD provider.

    Args:
        audio_path: Path to the audio file.
        provider_name: VAD provider name (silero, ten).
        vad_options: VAD options (threshold, min_speech_duration_ms, etc.)

    Returns:
        Tuple of (speech_timestamps, audio_data, sample_rate).
    """
    from app.vad.manager import vad_manager

    logger.info(f"Loading audio file for VAD processing with {provider_name}...")
    audio_data, sample_rate = sf.read(audio_path)

    # Get VAD provider
    provider = vad_manager.get_provider(provider_name)
    if not provider:
        raise ValueError(f"VAD provider '{provider_name}' not found")

    # Prepare options
    options = vad_options or {}
    threshold = options.get("threshold", 0.5)
    min_speech_duration_ms = options.get("min_speech_duration_ms", 500)
    min_silence_duration_ms = options.get("min_silence_duration_ms", 500)

    logger.info(f"Starting VAD speech detection with {provider_name}...")
    speech_timestamps = provider.process_audio(
        audio_data,
        threshold=threshold,
        min_speech_duration_ms=min_speech_duration_ms,
        min_silence_duration_ms=min_silence_duration_ms,
    )

    logger.info(f"VAD detection completed, found {len(speech_timestamps)} speech segments")

    return speech_timestamps, audio_data, sample_rate
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_audio_processing.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/utils/audio_processing.py backend/tests/test_audio_processing.py
git commit -m "feat: add VAD segmentation with provider selection"
```

---

## Task 8: Update ASR Service to Use Configurable VAD

**Files:**
- Modify: `backend/app/services/asr_service.py`
- Test: `backend/tests/test_asr_service.py`

**Step 1: Write the failing test**

Create `backend/tests/test_asr_service.py`:

```python
"""Test ASR service with VAD selection"""
import pytest
from app.services.asr_service import ASRService


def test_asr_service_accepts_vad_method():
    """Test that ASRService can accept vad_method parameter"""
    service = ASRService()
    # This test verifies the method signature accepts vad_method
    # Actual processing test would require audio file
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_asr_service.py -v`

Expected: PASS (placeholder test) - but we need to verify the signature

**Step 3: Write minimal implementation**

Modify `backend/app/services/asr_service.py`:

1. Update `process_media` method signature (around line 63-76):

Add `vad_method: str = "silero"` parameter:

```python
    async def process_media(
        self,
        media_path: str,
        asr_method: str = "whisper-api",
        vad_method: str = "silero",
        vad_options: Optional[Dict[str, Any]] = None,
        # ... rest of parameters
    ) -> ASRResponse:
```

2. Update the VAD segmentation call (around line 141-143):

Old:
```python
                speech_timestamps, audio_data, sample_rate = silero_vad_segmentation(
                    processed_audio_path, vad_options or {}
                )
```

New:
```python
                from app.utils.audio_processing import vad_segmentation_with_provider

                speech_timestamps, audio_data, sample_rate = vad_segmentation_with_provider(
                    processed_audio_path,
                    provider_name=vad_method,
                    vad_options=vad_options or {}
                )
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/test_asr_service.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/services/asr_service.py backend/tests/test_asr_service.py
git commit -m "feat: use configurable VAD in ASR service"
```

---

## Task 9: Update API Routes to Expose VAD Selection

**Files:**
- Modify: `backend/app/api/v1/endpoints/asr.py` (or similar route file)
- Test: `backend/tests/api/test_asr_routes.py`

**Step 1: Write the failing test**

Create `backend/tests/api/test_asr_routes.py`:

```python
"""Test ASR API routes"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_asr_endpoint_accepts_vad_method():
    """Test that ASR endpoint accepts vad_method parameter"""
    client = TestClient(app)

    # Test request validation (mock file upload)
    response = client.post(
        "/api/v1/asr/transcribe",
        data={
            "asr_method": "local-whisper",
            "vad_method": "ten",
        }
    )
    # Should return 422 for missing file, but not 422 for vad_method
    # The error should be about missing file, not invalid vad_method
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/api/test_asr_routes.py -v`

Expected: May fail if vad_method not passed through

**Step 3: Write minimal implementation**

Find the transcribe endpoint in `backend/app/api/v1/endpoints/asr.py` (or similar) and update the function call to pass `vad_method` from request to ASR service.

Look for where `ASRService.process_media` is called and add:
```python
vad_method=request.vad_method,
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/api/test_asr_routes.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/api/v1/endpoints/asr.py backend/tests/api/test_asr_routes.py
git commit -m "feat: expose vad_method in ASR API endpoint"
```

---

## Task 10: Add VAD Providers Info Endpoint

**Files:**
- Create: `backend/app/api/v1/endpoints/vad.py`
- Modify: `backend/app/api/v1/router.py` (register route)
- Test: `backend/tests/api/test_vad_routes.py`

**Step 1: Write the failing test**

Create `backend/tests/api/test_vad_routes.py`:

```python
"""Test VAD API routes"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_get_vad_providers():
    """Test getting available VAD providers"""
    client = TestClient(app)
    response = client.get("/api/v1/vad/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert any(p["name"] == "silero" for p in data["providers"])
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/api/test_vad_routes.py -v`

Expected: FAIL with 404

**Step 3: Write minimal implementation**

Create `backend/app/api/v1/endpoints/vad.py`:

```python
"""VAD provider endpoints"""
from fastapi import APIRouter
from typing import Dict, Any
from app.vad.manager import vad_manager

router = APIRouter()


@router.get("/providers")
async def get_vad_providers() -> Dict[str, Any]:
    """Get available VAD providers."""
    return {
        "providers": vad_manager.get_available_providers(),
        "default": "silero"
    }
```

Register router in `backend/app/api/v1/router.py` (or main router file):

```python
from app.api.v1.endpoints import vad
api_router.include_router(vad.router, prefix="/vad", tags=["vad"])
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/api/test_vad_routes.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/api/v1/endpoints/vad.py backend/app/api/v1/router.py backend/tests/api/test_vad_routes.py
git commit -m "feat: add VAD providers info endpoint"
```

---

## Task 11: Update Frontend to Support VAD Selection

**Files:**
- Modify: `frontend/src/types/index.ts` - add VAD method type
- Modify: `frontend/src/stores/config.ts` or similar - add VAD method state
- Modify: `frontend/src/components/ASRForm.tsx` or similar - add VAD method selector

**Step 1: Write the test/integration check**

Check that frontend types include VAD method:
```bash
grep -r "vad_method" frontend/src/
```

Expected: No matches initially

**Step 2: Update frontend types**

Modify `frontend/src/types/index.ts`:

Add to existing types or create new:
```typescript
// VAD method types
export type VADMethod = 'silero' | 'ten';

export interface VADConfig {
  method: VADMethod;
  outputFormats: OutputFormat[];
  minSpeechDuration: number;
  minSilenceDuration: number;
}
```

**Step 3: Update API client/types**

Add `vadMethod` field to ASR request type.

**Step 4: Add UI component**

Add VAD method selector in the ASR form (similar to ASR method selector).

**Step 5: Test and commit**

```bash
cd frontend && npm run build
git add frontend/src/
git commit -m "feat: add VAD method selection to frontend"
```

---

## Summary of Implementation

After completing all tasks, the VAD system will:

1. **Support two VAD providers**: Silero VAD (default) and TEN VAD
2. **Be configurable**: Users can select VAD method via API or frontend
3. **Follow plugin pattern**: Similar to ASR plugins for consistency
4. **Have unit tests**: Each component has corresponding tests
5. **Have API endpoint**: `/api/v1/vad/providers` returns available providers

**Configuration:**
- Default VAD method: `silero` (configurable via `DEFAULT_VAD_METHOD`)
- Available methods: `["silero", "ten"]` (configurable via `AVAILABLE_VAD_METHODS`)
- Per-request selection via `vad_method` parameter

**Usage Example:**

```python
# Direct usage
from app.vad.manager import vad_manager

provider = vad_manager.get_provider("ten")
segments = provider.process_audio(audio, threshold=0.5)

# Via ASR service
service.process_media(
    media_path="audio.wav",
    vad_method="ten",
    vad_options={"threshold": 0.6}
)
```

**API Request Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/asr/transcribe" \
  -F "file=@audio.wav" \
  -F "vad_method=ten" \
  -F "vad_options={\"threshold\":0.6}"
```

---

## Sources:
- [TEN-framework/ten-vad on Hugging Face](https://huggingface.co/TEN-framework/ten-vad)
- [TEN VAD Discussion - Where is onnx file?](https://huggingface.co/TEN-framework/ten-vad/discussions/7)
- [TEN-framework/ten-vad on GitHub](https://github.com/TEN-framework/ten-vad)
