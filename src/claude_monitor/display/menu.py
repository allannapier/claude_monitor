"""Interactive menu and entry page for Claude Monitor."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
from rich.columns import Columns


class InteractiveMenu:
    """Interactive menu system for Claude Monitor."""

    # Skyscanner blue color
    SKYSCANNER_BLUE = "#0770E3"

    LOGO = """
   ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗
  ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝
  ██║     ██║     ███████║██║   ██║██║  ██║█████╗
  ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝
  ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗
   ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝

  ███╗   ███╗ ██████╗ ███╗   ██╗██╗████████╗ ██████╗ ██████╗
  ████╗ ████║██╔═══██╗████╗  ██║██║╚══██╔══╝██╔═══██╗██╔══██╗
  ██╔████╔██║██║   ██║██╔██╗ ██║██║   ██║   ██║   ██║██████╔╝
  ██║╚██╔╝██║██║   ██║██║╚██╗██║██║   ██║   ██║   ██║██╔══██╗
  ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║██║   ██║   ╚██████╔╝██║  ██║
  ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
    """

    def __init__(self, console: Console = None):
        """
        Initialize interactive menu.

        Args:
            console: Rich Console instance
        """
        self.console = console or Console()

    def display_logo(self):
        """Display the Claude Monitor logo in Skyscanner blue."""
        logo_text = Text(self.LOGO, style=f"bold {self.SKYSCANNER_BLUE}")
        subtitle = Text("Usage Tracking for Claude Code", style=f"italic {self.SKYSCANNER_BLUE}")

        self.console.print(Panel(
            logo_text,
            subtitle=subtitle,
            border_style=self.SKYSCANNER_BLUE,
            padding=(1, 2)
        ))
        self.console.print()

    def create_menu_table(self) -> Table:
        """Create the main menu options table."""
        table = Table(
            show_header=False,
            border_style=self.SKYSCANNER_BLUE,
            padding=(0, 2),
            show_edge=False
        )

        table.add_column("Option", style=f"bold {self.SKYSCANNER_BLUE}", width=6)
        table.add_column("Command", style="cyan", width=20)
        table.add_column("Description", style="white")

        # Menu options
        table.add_row("[1]", "Full Dashboard", "Complete overview with all metrics")
        table.add_row("[2]", "Claude Code Features", "Sub-agents, skills, tools, configuration")
        table.add_row("", "", "")
        table.add_row("[Q]", "Quit", "Exit Claude Monitor")

        return table

    def create_timeframe_table(self) -> Table:
        """Create the timeframe selection table."""
        table = Table(
            show_header=False,
            border_style=self.SKYSCANNER_BLUE,
            padding=(0, 2),
            show_edge=False
        )

        table.add_column("Option", style=f"bold {self.SKYSCANNER_BLUE}", width=6)
        table.add_column("Timeframe", style="cyan")

        table.add_row("[T]", "Today")
        table.add_row("[W]", "Last 7 days")
        table.add_row("[M]", "Last 30 days")
        table.add_row("[R]", "Current quarter")
        table.add_row("[Y]", "Last year")
        table.add_row("[A]", "All time (default)")

        return table

    def show_welcome(self):
        """Display welcome screen with menu options."""
        self.display_logo()

        # Create two-column layout for menu and timeframe
        menu_panel = Panel(
            self.create_menu_table(),
            title="[bold]Select View[/bold]",
            border_style=self.SKYSCANNER_BLUE,
            padding=(1, 2)
        )

        timeframe_panel = Panel(
            self.create_timeframe_table(),
            title="[bold]Time Range[/bold]",
            border_style=self.SKYSCANNER_BLUE,
            padding=(1, 2)
        )

        self.console.print(Columns([menu_panel, timeframe_panel], equal=True, expand=True))
        self.console.print()

    def get_user_choice(self) -> tuple[str, str]:
        """
        Get user's menu choice and timeframe.

        Returns:
            Tuple of (view_choice, timeframe_choice)
        """
        self.show_welcome()

        # Get view choice
        view = Prompt.ask(
            "[bold cyan]Select view[/bold cyan]",
            choices=["1", "2", "q", "Q"],
            default="1",
            show_choices=False
        ).upper()

        if view == "Q":
            return "quit", ""

        # Get timeframe choice
        timeframe = Prompt.ask(
            "[bold cyan]Select timeframe[/bold cyan]",
            choices=["t", "T", "w", "W", "m", "M", "r", "R", "y", "Y", "a", "A"],
            default="a",
            show_choices=False
        ).upper()

        self.console.clear()
        return view, timeframe

    @staticmethod
    def map_choices(view: str, timeframe: str) -> dict:
        """
        Map user choices to CLI options.

        Args:
            view: View choice (1-2)
            timeframe: Timeframe choice (T, W, M, Y, A)

        Returns:
            Dict with 'focus' and 'time_preset' keys
        """
        view_map = {
            "1": None,  # Full dashboard
            "2": "features"
        }

        timeframe_map = {
            "T": "today",
            "W": "week",
            "M": "month",
            "R": "quarter",
            "Y": "year",
            "A": "all"
        }

        return {
            "focus": view_map.get(view),
            "time_preset": timeframe_map.get(timeframe, "all")
        }
