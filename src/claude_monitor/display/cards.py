"""Summary cards for key metrics."""

from rich.panel import Panel
from rich.text import Text
from rich.align import Align


class SummaryCards:
    """Creates summary cards for key metrics."""

    @staticmethod
    def create_metric_card(title: str, value: str, subtitle: str = "", color: str = "cyan") -> Panel:
        """
        Create a summary metric card.

        Args:
            title: Card title
            value: Main metric value
            subtitle: Optional subtitle/description
            color: Border color

        Returns:
            Rich Panel with metric card
        """
        content = Text()
        content.append(f"{title}\n", style=f"bold {color}")
        content.append(value, style=f"bold white")

        if subtitle:
            content.append(f"\n{subtitle}", style="dim")

        return Panel(
            Align.center(content),
            border_style=color,
            padding=(1, 2)
        )

    @staticmethod
    def create_cost_card(cost: float, savings: float) -> Panel:
        """
        Create a cost summary card with savings.

        Args:
            cost: Total cost
            savings: Cache savings

        Returns:
            Rich Panel with cost card
        """
        content = Text()
        content.append("TOTAL COST\n", style="bold yellow")
        content.append(f"${cost:.2f}", style="bold white")

        if savings > 0:
            content.append(f"\n-${savings:.2f} saved", style="green")

        return Panel(
            Align.center(content),
            border_style="yellow",
            padding=(1, 2)
        )

    @staticmethod
    def create_efficiency_card(percentage: float) -> Panel:
        """
        Create cache efficiency card.

        Args:
            percentage: Efficiency percentage

        Returns:
            Rich Panel with efficiency card
        """
        content = Text()
        content.append("CACHE HIT RATE\n", style="bold green")
        content.append(f"{percentage:.1f}%", style="bold white")

        # Color code based on efficiency
        if percentage >= 80:
            status = "Excellent"
            color = "green"
        elif percentage >= 60:
            status = "Good"
            color = "yellow"
        else:
            status = "Low"
            color = "red"

        content.append(f"\n{status}", style=f"dim {color}")

        return Panel(
            Align.center(content),
            border_style="green",
            padding=(1, 2)
        )

    @staticmethod
    def create_session_card(sessions: int, commands: int) -> Panel:
        """
        Create sessions summary card.

        Args:
            sessions: Number of sessions
            commands: Number of commands

        Returns:
            Rich Panel with session card
        """
        content = Text()
        content.append("SESSIONS\n", style="bold cyan")
        content.append(f"{sessions:,}", style="bold white")
        content.append(f"\n{commands:,} commands", style="dim")

        return Panel(
            Align.center(content),
            border_style="cyan",
            padding=(1, 2)
        )

    @staticmethod
    def create_token_card(total_tokens: int) -> Panel:
        """
        Create token summary card.

        Args:
            total_tokens: Total token count

        Returns:
            Rich Panel with token card
        """
        content = Text()
        content.append("TOTAL TOKENS\n", style="bold magenta")

        # Format tokens
        if total_tokens >= 1_000_000_000:
            formatted = f"{total_tokens / 1_000_000_000:.1f}B"
        elif total_tokens >= 1_000_000:
            formatted = f"{total_tokens / 1_000_000:.1f}M"
        elif total_tokens >= 1_000:
            formatted = f"{total_tokens / 1_000:.1f}K"
        else:
            formatted = str(total_tokens)

        content.append(formatted, style="bold white")

        return Panel(
            Align.center(content),
            border_style="magenta",
            padding=(1, 2)
        )
