"""Main CLI application for lazy-asr"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, List

import typer
import structlog
from rich.console import Console

from app.core.config import settings
from app.core.logger import get_logger
from app.services.asr_service import ASRService
from app.cli.progress import ConsoleProgressReporter

# Create CLI app
app = typer.Typer(
    name="lazy-asr",
    help="Lazy ASR - Automatic Speech Recognition command-line tool",
    no_args_is_help=True,
)

console = Console()
logger = get_logger(__name__)


@app.command()
def transcribe(
    file: str = typer.Argument(..., help="Path to media file (audio or video)"),
    *,
    asr_method: str = typer.Option(
        settings.DEFAULT_ASR_METHOD,
        "--method", "-m",
        help="ASR method to use"
    ),
    vad_method: str = typer.Option(
        settings.DEFAULT_VAD_METHOD,
        "--vad",
        help="VAD method to use (silero, ten)"
    ),
    language: str = typer.Option(
        "auto",
        "--language", "-l",
        help="Language code (e.g., en, zh) or 'auto' for detection"
    ),
    output_formats: str = typer.Option(
        "srt",
        "--formats", "-f",
        help="Output formats (comma-separated): srt, vtt, lrc, txt"
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory (default: same as source file)"
    ),
    api_url: Optional[str] = typer.Option(
        None,
        "--api-url",
        help="Custom API URL for ASR service"
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        help="API key for ASR service"
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        help="Model name for ASR service"
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed progress information"
    ),
):
    """
    Transcribe a media file to subtitles.

    Examples:

        # Transcribe with default settings
        lazy-asr transcribe video.mp4

        # Use specific ASR method and output multiple formats
        lazy-asr transcribe video.mp4 --method local-whisper --formats srt,vtt,lrc

        # Specify language and output directory
        lazy-asr transcribe audio.wav --language en --output ./subtitles

        # Use custom API endpoint
        lazy-asr transcribe video.mp4 --api-url https://api.example.com/asr
    """
    # Validate file exists
    file_path = Path(file).expanduser().resolve()
    if not file_path.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    if not file_path.is_file():
        console.print(f"[red]Error:[/red] Not a file: {file}")
        raise typer.Exit(1)

    # Parse output formats
    formats_list = [f.strip() for f in output_formats.split(",")]

    # Setup output mode
    output_mode = "source" if output_dir is None else "task"

    # Run transcription
    result = asyncio.run(_run_transcription(
        file_path=str(file_path),
        asr_method=asr_method,
        vad_method=vad_method,
        language=language,
        output_formats=formats_list,
        output_mode=output_mode,
        output_dir=output_dir,
        api_url=api_url,
        api_key=api_key,
        model=model,
        verbose=verbose,
    ))

    # Handle output
    if json_output:
        import json
        console.print_json(json.dumps(result.model_dump(mode='json'), indent=2))
    else:
        _print_human_readable_result(result, console)

    # Exit with appropriate code
    if not result.success:
        raise typer.Exit(1)


async def _run_transcription(
    file_path: str,
    asr_method: str,
    vad_method: str,
    language: str,
    output_formats: List[str],
    output_mode: str,
    output_dir: Optional[str],
    api_url: Optional[str],
    api_key: Optional[str],
    model: Optional[str],
    verbose: bool,
):
    """Run the transcription process"""
    # Initialize reporter
    reporter = ConsoleProgressReporter(console)

    reporter.print_info(f"[cyan]Processing:[/cyan] {file_path}")
    reporter.print_info(f"[cyan]ASR Method:[/cyan] {asr_method}")
    reporter.print_info(f"[cyan]VAD Method:[/cyan] {vad_method}")

    if verbose:
        reporter.start_progress(description="Transcribing...")

    # Create progress callback
    async def progress_callback(progress_data: dict):
        if verbose:
            await reporter(progress_data)

    # Initialize service
    service = ASRService()

    # Temporarily override output directory if specified
    original_output_dir = service.output_dir
    if output_dir:
        service.output_dir = output_dir

    try:
        result = await service.process_media(
            media_path=file_path,
            asr_method=asr_method,
            vad_method=vad_method,
            language=language,
            output_formats=output_formats,
            output_mode=output_mode,
            asr_api_url=api_url,
            asr_api_key=api_key,
            asr_model=model,
            progress_callback=progress_callback if verbose else None,
        )
        return result
    finally:
        if verbose:
            reporter.stop_progress()
        if output_dir:
            service.output_dir = original_output_dir


def _print_human_readable_result(result, console: Console):
    """Print transcription result in human-readable format"""
    if result.success:
        console.print()  # Blank line

        # Show output files
        if result.output_files:
            console.print("[bold green]Generated files:[/bold green]")
            for fmt, path in result.output_files.items():
                console.print(f"  [cyan]{fmt.upper()}:[/cyan] {path}")

        # Show statistics
        if result.stats:
            console.print()
            console.print("[bold]Statistics:[/bold]")
            for key, value in result.stats.items():
                key_formatted = key.replace("_", " ").title()
                console.print(f"  [cyan]{key_formatted}:[/cyan] {value}")

        console.print()
        reporter = ConsoleProgressReporter(console)
        reporter.print_success(result.message)
    else:
        console.print()
        reporter = ConsoleProgressReporter(console)
        reporter.print_error(result.message)


@app.command()
def scan(
    path: str = typer.Argument(..., help="Path to directory to scan"),
    *,
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive",
        "-r/-nr",
        help="Scan directories recursively"
    ),
    max_files: int = typer.Option(
        100,
        "--max-files",
        help="Maximum number of files to process"
    ),
    skip_existing: bool = typer.Option(
        True,
        "--skip-existing/--process-all",
        help="Skip files that already have subtitle files"
    ),
    asr_method: str = typer.Option(
        settings.DEFAULT_ASR_METHOD,
        "--method", "-m",
        help="ASR method to use"
    ),
    vad_method: str = typer.Option(
        settings.DEFAULT_VAD_METHOD,
        "--vad",
        help="VAD method to use"
    ),
    formats: str = typer.Option(
        "srt",
        "--formats", "-f",
        help="Output formats (comma-separated)"
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON"
    ),
):
    """
    Scan a directory for media files and transcribe them.

    Examples:

        # Scan current directory recursively
        lazy-asr scan .

        # Scan without recursion
        lazy-asr scan /path/to/videos --no-recursive

        # Process up to 50 files
        lazy-asr scan /media --max-files 50
    """
    from app.services.scan_service import ScanService

    scan_path = Path(path).expanduser().resolve()
    if not scan_path.exists():
        console.print(f"[red]Error:[/red] Path not found: {path}")
        raise typer.Exit(1)

    if not scan_path.is_dir():
        console.print(f"[red]Error:[/red] Not a directory: {path}")
        raise typer.Exit(1)

    formats_list = [f.strip() for f in formats.split(",")]

    # Run scan synchronously for CLI
    result = asyncio.run(_run_scan(
        scan_path=str(scan_path),
        recursive=recursive,
        max_files=max_files,
        skip_existing=skip_existing,
        asr_method=asr_method,
        vad_method=vad_method,
        output_formats=formats_list,
    ))

    if json_output:
        import json
        console.print_json(json.dumps(result, indent=2, default=str))
    else:
        _print_scan_result(result, console)


async def _run_scan(
    scan_path: str,
    recursive: bool,
    max_files: int,
    skip_existing: bool,
    asr_method: str,
    vad_method: str,
    output_formats: List[str],
) -> dict:
    """Run the scan process"""
    from app.models.schemas import ScanRequest
    from app.services.scan_service import ScanService

    console.print(f"[cyan]Scanning:[/cyan] {scan_path}")
    console.print(f"[cyan]Recursive:[/cyan] {recursive}")
    console.print(f"[cyan]Max Files:[/cyan] {max_files}")
    console.print()

    scan_service = ScanService()

    # Create scan request
    scan_request = ScanRequest(
        path=scan_path,
        recursive=recursive,
        max_files=max_files,
        asr_method=asr_method,
        vad_method=vad_method,
        output_formats=output_formats,
    )

    # Perform scan directly (synchronously for CLI)
    scan_id = await scan_service.scan_path(scan_request)

    # Wait for scan to complete
    import time
    while True:
        status = scan_service.get_scan_status(scan_id)
        if not status:
            console.print("[red]Error:[/red] Scan lost")
            return {"error": "Scan lost"}

        if status.status in ["completed", "failed"]:
            break

        # Print progress
        console.print(
            f"Progress: {status.progress}% - {status.message}",
            end="\r",
        )
        time.sleep(0.5)

    console.print()  # New line after progress

    # Get result
    result = scan_service.get_scan_result(scan_id)
    if result:
        return {
            "scan_id": result.scan_id,
            "status": result.status,
            "total_files": result.total_files,
            "processed_files": result.processed_files,
            "failed_files": result.failed_files,
            "success_rate": result.success_rate,
            "duration_seconds": result.duration_seconds,
        }

    return status.model_dump()


def _print_scan_result(result: dict, console: Console):
    """Print scan result in human-readable format"""
    console.print()
    console.print("[bold]Scan Results:[/bold]")
    console.print(f"  [cyan]Status:[/cyan] {result.get('status', 'unknown')}")
    console.print(f"  [cyan]Total Files:[/cyan] {result.get('total_files', 0)}")
    console.print(f"  [cyan]Processed:[/cyan] {result.get('processed_files', 0)}")
    console.print(f"  [cyan]Failed:[/cyan] {result.get('failed_files', 0)}")
    console.print(f"  [cyan]Duration:[/cyan] {result.get('duration_seconds', 0):.1f}s")
    console.print()


@app.command()
def plugins():
    """List available ASR plugins and VAD providers"""
    from plugins.manager import plugin_manager

    console.print("[bold]Available ASR Plugins:[/bold]")
    plugins_list = plugin_manager.get_available_plugins()

    for plugin in plugins_list:
        console.print(f"  [green]✓[/green] [cyan]{plugin['name']}[/cyan]")
        if plugin.get("description"):
            console.print(f"      {plugin['description']}")

    console.print()
    console.print(f"[bold]Default ASR Method:[/bold] {settings.DEFAULT_ASR_METHOD}")

    console.print()
    console.print("[bold]Available VAD Providers:[/bold]")
    for vad_method in settings.AVAILABLE_VAD_METHODS:
        is_default = " (default)" if vad_method == settings.DEFAULT_VAD_METHOD else ""
        console.print(f"  [cyan]{vad_method}[/cyan]{is_default}")


@app.command()
def version():
    """Show version information"""
    console.print("[bold]lazy-asr[/bold] - Automatic Speech Recognition Tool")
    console.print(f"Version: {settings.PROJECT_NAME}")
    console.print(f"Default ASR: {settings.DEFAULT_ASR_METHOD}")
    console.print(f"Default VAD: {settings.DEFAULT_VAD_METHOD}")


def main():
    """Main entry point for CLI"""
    app()


if __name__ == "__main__":
    main()
