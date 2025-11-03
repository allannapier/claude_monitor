"""Formatter utilities for rich console output."""

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table
from rich.text import Text


class DisplayFormatter:
    """Handles formatting and display of metrics using rich."""

    def __init__(self, console: Console = None):
        """
        Initialize display formatter.

        Args:
            console: Rich Console instance. Creates new one if not provided.
        """
        self.console = console or Console()

    def create_title_panel(self, title: str, subtitle: str = "") -> Panel:
        """
        Create a title panel.

        Args:
            title: Main title text
            subtitle: Optional subtitle text

        Returns:
            Rich Panel instance
        """
        text = Text(title, style="bold cyan")
        if subtitle:
            text.append(f"\n{subtitle}", style="dim")

        return Panel(
            text,
            border_style="cyan",
            padding=(0, 1)
        )

    def create_section_header(self, icon: str, title: str) -> Text:
        """
        Create a section header with icon.

        Args:
            icon: Emoji or symbol
            title: Section title

        Returns:
            Rich Text instance
        """
        text = Text()
        text.append(icon + " ", style="bold")
        text.append(title, style="bold white")
        return text

    def create_metric_table(self, title: str = "", expand: bool = False) -> Table:
        """
        Create a styled table for metrics.

        Args:
            title: Optional table title
            expand: Whether table should expand to fill available space

        Returns:
            Rich Table instance
        """
        table = Table(
            title=title,
            show_header=True,
            header_style="bold cyan",
            border_style="dim",
            padding=(0, 1),
            expand=expand,
            box=None
        )
        return table

    def create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """
        Create a simple ASCII progress bar.

        Args:
            percentage: Percentage value (0-100)
            width: Width of progress bar in characters

        Returns:
            Progress bar string
        """
        filled = int((percentage / 100) * width)
        empty = width - filled
        return "█" * filled + "░" * empty

    def format_percentage(self, percentage: float) -> Text:
        """
        Format a percentage with color coding.

        Args:
            percentage: Percentage value

        Returns:
            Rich Text instance with color
        """
        text = Text(f"{percentage:.1f}%")

        # Color code based on value
        if percentage >= 70:
            text.stylize("green")
        elif percentage >= 40:
            text.stylize("yellow")
        else:
            text.stylize("red")

        return text

    def format_cost(self, cost: float, show_sign: bool = False) -> Text:
        """
        Format a cost value with color.

        Args:
            cost: Cost in dollars
            show_sign: Whether to show + sign for positive values

        Returns:
            Rich Text instance with color
        """
        prefix = "+" if show_sign and cost > 0 else ""
        text = Text(f"{prefix}${cost:.2f}")

        if cost < 0:
            text.stylize("green")
        elif cost > 10:
            text.stylize("red")
        elif cost > 5:
            text.stylize("yellow")
        else:
            text.stylize("white")

        return text

    def format_large_number(self, number: int) -> str:
        """
        Format large numbers with commas.

        Args:
            number: Number to format

        Returns:
            Formatted string
        """
        return f"{number:,}"

    def print_section(self, content, spacing: bool = True):
        """
        Print a section with optional spacing.

        Args:
            content: Content to print (Panel, Table, Text, etc.)
            spacing: Whether to add spacing after
        """
        self.console.print(content)
        if spacing:
            self.console.print()

    def print_separator(self):
        """Print a visual separator line."""
        self.console.print("─" * self.console.width, style="dim")
