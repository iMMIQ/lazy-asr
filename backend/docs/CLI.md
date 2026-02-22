# CLI Documentation

The `lazy-asr` command-line interface provides direct access to ASR transcription
and path scanning without running the API server.

## Installation

After installing the package, the CLI is available as:

```bash
lazy-asr --help
```

## Commands

### transcribe

Transcribe a single media file to subtitles.

```bash
lazy-asr transcribe FILE [OPTIONS]
```

**Arguments:**
- `FILE`: Path to media file (audio or video)

**Options:**
- `--method, -m`: ASR method to use (default: local-whisper)
- `--vad`: VAD method to use (default: ten)
- `--language, -l`: Language code or 'auto' (default: auto)
- `--formats, -f`: Output formats, comma-separated (default: srt)
- `--output, -o`: Output directory (default: same as source)
- `--api-url`: Custom API URL for ASR service
- `--api-key`: API key for ASR service
- `--model`: Model name for ASR service
- `--json`: Output results as JSON
- `--verbose, -v`: Show detailed progress

**Examples:**

```bash
# Basic transcription
lazy-asr transcribe video.mp4

# Multiple output formats
lazy-asr transcribe video.mp4 --formats srt,vtt,lrc

# Use specific ASR method
lazy-asr transcribe audio.wav --method whisper-api

# Specify language
lazy-asr transcribe video.mp4 --language zh

# Custom output directory
lazy-asr transcribe video.mp4 --output ./subtitles

# Use API with custom endpoint
lazy-asr transcribe video.mp4 --method whisper-api --api-url https://api.example.com

# JSON output
lazy-asr transcribe video.mp4 --json
```

### scan

Scan a directory for media files and transcribe them.

```bash
lazy-asr scan PATH [OPTIONS]
```

**Arguments:**
- `PATH`: Path to directory to scan

**Options:**
- `--recursive, -r`: Scan recursively (default: True)
- `--no-recursive, -nr`: Don't scan recursively
- `--max-files`: Maximum files to process (default: 100)
- `--skip-existing`: Skip files with subtitles (default: True)
- `--process-all`: Process all files, even with existing subtitles
- `--method, -m`: ASR method to use
- `--vad`: VAD method to use
- `--formats, -f`: Output formats
- `--json`: Output results as JSON

**Examples:**

```bash
# Scan current directory
lazy-asr scan .

# Scan without recursion
lazy-asr scan /videos --no-recursive

# Limit files processed
lazy-asr scan /media --max-files 50
```

### plugins

List available ASR plugins and VAD providers.

```bash
lazy-asr plugins
```

### version

Show version information.

```bash
lazy-asr version
```

## Output Formats

Supported subtitle formats:
- **srt**: SubRip subtitle format
- **vtt**: WebVTT subtitle format
- **lrc**: LRC lyric format
- **txt**: Plain text transcript

## ASR Methods

- **local-whisper**: Local Whisper using faster-whisper (CPU)
- **whisper-api**: Remote Whisper API service
- **qwen-asr**: Alibaba Qwen ASR service

## VAD Methods

- **silero**: Silero VAD model
- **ten**: TEN VAD provider

## Configuration

The CLI uses the same configuration as the API server. You can override
settings via environment variables or create a `.env` file in the working
directory.

**Environment Variables:**
- `LAZY_ASR_DEFAULT_ASR_METHOD`: Default ASR method
- `LAZY_ASR_DEFAULT_VAD_METHOD`: Default VAD method
- `LAZY_ASR_WHISPER_API_URL`: Whisper API URL
- `LAZY_ASR_WHISPER_API_KEY`: Whisper API key
- `LAZY_ASR_LOCAL_WHISPER_MODEL`: Local Whisper model name
- `LAZY_ASR_OUTPUT_DIR`: Default output directory
