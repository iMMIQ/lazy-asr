"""Console-based progress reporting for CLI operations"""

from typing import Dict, Any, Optional
from rich.console import Console
from rich.progress import Progress, TaskID, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
from rich.panel import Panel
from rich.text import Text


class ConsoleProgressReporter:
    """Progress reporter for CLI operations using Rich for beautiful terminal output"""

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the console progress reporter

        Args:
            console: Optional Rich console instance (creates new one if not provided)
        """
        self.console = console or Console()
        self.progress: Optional[Progress] = None
        self.task_id: Optional[TaskID] = None
        self.current_stage = ""
        self._messages = []

    async def __call__(self, progress_data: Dict[str, Any]):
        """
        Async callback for progress updates

        Args:
            progress_data: Progress data dictionary with keys:
                - stage: Current processing stage
                - progress: Progress percentage (0-100)
                - message: Human-readable message
        """
        stage = progress_data.get("stage", "")
        progress = progress_data.get("progress", 0)
        message = progress_data.get("message", "")

        if stage != self.current_stage:
            self.current_stage = stage
            self._print_stage_message(stage, message)
        elif message:
            self._print_progress(progress, message)

    def _print_stage_message(self, stage: str, message: str):
        """Print a stage change message"""
        stage_text = Text()
        stage_text.append(f"[{stage.upper()}] ", style="bold cyan")
        stage_text.append(message, style="white")
        self.console.print(stage_text)

    def _print_progress(self, progress: float, message: str):
        """Print progress update"""
        if self.progress and self.task_id:
            self.progress.update(self.task_id, completed=progress, description=message)

    def start_progress(self, total: int = 100, description: str = "Processing..."):
        """Start a progress bar"""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console,
        )
        self.progress.start()
        self.task_id = self.progress.add_task(description, total=total)

    def stop_progress(self):
        """Stop the progress bar"""
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.task_id = None

    def print_success(self, message: str):
        """Print a success message"""
        self.console.print(Panel(message, title="[bold green]Success[/bold green]", border_style="green"))

    def print_error(self, message: str):
        """Print an error message"""
        self.console.print(Panel(message, title="[bold red]Error[/bold red]", border_style="red"))

    def print_info(self, message: str):
        """Print an info message"""
        self.console.print(message)

    def print_warning(self, message: str):
        """Print a warning message"""
        self.console.print(f"[yellow]Warning:[/yellow] {message}")

    def print_stats(self, stats: Dict[str, Any]):
        """Print processing statistics"""
        stats_text = Text()
        for key, value in stats.items():
            key_formatted = key.replace("_", " ").title()
            stats_text.append(f"{key_formatted}: ", style="bold cyan")
            stats_text.append(f"{value}\n")

        self.console.print(Panel(stats_text, title="[bold]Statistics[/bold]", border_style="blue"))
