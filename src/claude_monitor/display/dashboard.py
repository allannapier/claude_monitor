"""Main dashboard for displaying all metrics."""

from rich.console import Console, Group
from rich.columns import Columns
from rich.panel import Panel

from ..analyzers.usage import UsageAnalyzer
from ..analyzers.tokens import TokenAnalyzer
from ..analyzers.integrations import IntegrationAnalyzer
from ..analyzers.features import FeaturesAnalyzer
from ..parsers.files import FileHistoryParser
from .formatter import DisplayFormatter
from .tables import MetricTables
from .cards import SummaryCards


class Dashboard:
    """Main dashboard for displaying Claude Code metrics."""

    # Compact single-line logo for dashboard header
    COMPACT_LOGO = """
 ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗    ███╗   ███╗ ██████╗ ███╗   ██╗██╗████████╗ ██████╗ ██████╗
██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝    ████╗ ████║██╔═══██╗████╗  ██║██║╚══██╔══╝██╔═══██╗██╔══██╗
██║     ██║     ███████║██║   ██║██║  ██║█████╗      ██╔████╔██║██║   ██║██╔██╗ ██║██║   ██║   ██║   ██║██████╔╝
██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝      ██║╚██╔╝██║██║   ██║██║╚██╗██║██║   ██║   ██║   ██║██╔══██╗
╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗    ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║██║   ██║   ╚██████╔╝██║  ██║
 ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝    ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
    """

    def __init__(
        self,
        usage_analyzer: UsageAnalyzer,
        token_analyzer: TokenAnalyzer,
        integration_analyzer: IntegrationAnalyzer,
        features_analyzer: FeaturesAnalyzer,
        file_parser: FileHistoryParser,
        console: Console = None
    ):
        """
        Initialize dashboard.

        Args:
            usage_analyzer: UsageAnalyzer instance
            token_analyzer: TokenAnalyzer instance
            integration_analyzer: IntegrationAnalyzer instance
            features_analyzer: FeaturesAnalyzer instance
            file_parser: FileHistoryParser instance
            console: Optional Rich Console instance
        """
        self.usage_analyzer = usage_analyzer
        self.token_analyzer = token_analyzer
        self.integration_analyzer = integration_analyzer
        self.features_analyzer = features_analyzer
        self.file_parser = file_parser

        self.console = console or Console()
        self.formatter = DisplayFormatter(self.console)
        self.tables = MetricTables(self.formatter)

    def display_full_dashboard(self):
        """Display complete dashboard with all metrics."""
        # Get all data
        usage_summary = self.usage_analyzer.get_summary()
        token_summary = self.token_analyzer.get_summary()
        integration_summary = self.integration_analyzer.get_summary()
        project_breakdown = self.usage_analyzer.get_project_breakdown()
        most_edited = self.file_parser.get_most_edited_files(limit=10)

        # Display compact logo header
        from rich.text import Text
        from rich.panel import Panel

        logo_text = Text(self.COMPACT_LOGO, style=f"bold #0770E3")
        subtitle = Text(f"({usage_summary.time_range_description})", style="#0770E3")

        logo_panel = Panel(
            logo_text,
            subtitle=subtitle,
            border_style="#0770E3",
            padding=(0, 2)
        )
        self.formatter.print_section(logo_panel)

        # Summary Cards Row - Key metrics at a glance
        total_tokens = (token_summary.total_tokens.total_input_tokens +
                       token_summary.total_tokens.output_tokens)

        cards = [
            SummaryCards.create_session_card(
                usage_summary.total_sessions,
                usage_summary.total_commands
            ),
            SummaryCards.create_token_card(total_tokens),
            SummaryCards.create_cost_card(
                token_summary.total_cost,
                token_summary.cache_savings
            ),
            SummaryCards.create_efficiency_card(
                token_summary.cache_efficiency_pct
            )
        ]

        self.console.print(Columns(cards, padding=(0, 2)))
        self.console.print()

        # Row 1: Usage Summary and Token Usage side by side
        usage_panel = Panel(
            Group(
                self.formatter.create_section_header("📊", "USAGE SUMMARY"),
                self.tables.create_usage_table(usage_summary)
            ),
            border_style="cyan",
            padding=(1, 2)
        )

        token_content = Group(
            self.formatter.create_section_header("💰", "TOKEN USAGE & COSTS"),
            self.tables.create_token_table(token_summary),
            self.tables.create_cache_efficiency_display(token_summary)
        )
        token_panel = Panel(
            token_content,
            border_style="cyan",
            padding=(1, 2)
        )

        self.console.print(Columns([usage_panel, token_panel], padding=(0, 2)))
        self.console.print()

        # Row 2: Model Usage and Model Usage by Project side by side
        model_breakdown = self.token_analyzer.get_model_breakdown()
        model_by_project = self.token_analyzer.get_model_by_project_breakdown()

        model_left_panel = None
        model_right_panel = None

        if model_breakdown:
            model_left_panel = Panel(
                Group(
                    self.formatter.create_section_header("🤖", "MODEL USAGE"),
                    self.tables.create_model_usage_table(model_breakdown)
                ),
                border_style="cyan",
                padding=(1, 2)
            )

        if model_by_project:
            model_right_panel = Panel(
                Group(
                    self.formatter.create_section_header("📊", "MODELS BY PROJECT"),
                    self.tables.create_model_by_project_table(model_by_project, limit=10)
                ),
                border_style="cyan",
                padding=(1, 2)
            )

        # Display panels
        if model_left_panel and model_right_panel:
            self.console.print(Columns([model_left_panel, model_right_panel], padding=(0, 2)))
        elif model_left_panel:
            self.console.print(model_left_panel)
        elif model_right_panel:
            self.console.print(model_right_panel)

        self.console.print()

        # Row 3: Top Projects and Token Usage by Project side by side
        project_tokens = self.token_analyzer.get_project_breakdown()

        left_panel = None
        right_panel = None

        if project_breakdown:
            left_panel = Panel(
                Group(
                    self.formatter.create_section_header("📁", "TOP PROJECTS"),
                    self.tables.create_project_table(project_breakdown, limit=10)
                ),
                border_style="cyan",
                padding=(1, 2)
            )

        if project_tokens:
            right_panel = Panel(
                Group(
                    self.formatter.create_section_header("💰", "TOKEN USAGE BY PROJECT"),
                    self.tables.create_project_tokens_table(project_tokens, limit=10)
                ),
                border_style="cyan",
                padding=(1, 2)
            )

        # Display panels
        if left_panel and right_panel:
            self.console.print(Columns([left_panel, right_panel], padding=(0, 2)))
        elif left_panel:
            self.console.print(left_panel)
        elif right_panel:
            self.console.print(right_panel)

        self.console.print()

        # Row 4: Most Edited Files (full width)
        if most_edited:
            files_panel = Panel(
                Group(
                    self.formatter.create_section_header("✏️", "MOST EDITED FILES"),
                    self.tables.create_files_table(most_edited, limit=10)
                ),
                border_style="cyan",
                padding=(1, 2)
            )

            self.console.print(Columns([files_panel], padding=(0, 2)))
            self.console.print()

    def display_usage_only(self):
        """Display only usage metrics."""
        usage_summary = self.usage_analyzer.get_summary()

        title = "Claude Code Usage"
        subtitle = f"({usage_summary.time_range_description})"
        self.formatter.print_section(
            self.formatter.create_title_panel(title, subtitle)
        )

        self.formatter.print_section(
            self.tables.create_usage_table(usage_summary)
        )

        project_breakdown = self.usage_analyzer.get_project_breakdown()
        if project_breakdown:
            self.formatter.print_section(
                self.formatter.create_section_header("📁", "PROJECT BREAKDOWN")
            )
            self.formatter.print_section(
                self.tables.create_project_table(project_breakdown)
            )

    def display_tokens_only(self):
        """Display only token usage and costs."""
        token_summary = self.token_analyzer.get_summary()

        self.formatter.print_section(
            self.formatter.create_title_panel("Token Usage & Costs")
        )

        self.formatter.print_section(
            self.tables.create_token_table(token_summary),
            spacing=False
        )
        self.formatter.print_section(
            self.tables.create_cache_efficiency_display(token_summary)
        )

        # Per-project breakdown
        project_tokens = self.token_analyzer.get_project_breakdown()
        if project_tokens:
            self.formatter.print_section(
                self.formatter.create_section_header("📁", "TOKEN USAGE BY PROJECT")
            )

            for project_path, summary in list(project_tokens.items())[:5]:
                project_name = project_path.split('/')[-1]
                self.console.print(f"\n[cyan]{project_name}[/cyan]")
                self.console.print(
                    f"  Tokens: {TokenAnalyzer.format_token_count(summary.total_tokens.total_input_tokens + summary.total_tokens.output_tokens)} | "
                    f"Cost: ${summary.total_cost:.2f} | "
                    f"Cache: {summary.cache_efficiency_pct:.1f}%"
                )

    def display_integrations_only(self):
        """Display only MCP integration metrics."""
        integration_summary = self.integration_analyzer.get_summary()

        self.formatter.print_section(
            self.formatter.create_title_panel("MCP Integrations")
        )

        self.formatter.print_section(
            self.tables.create_integration_table(integration_summary)
        )

        if integration_summary.has_integrations:
            self.console.print(
                f"\n[white]Total Servers:[/white] {integration_summary.total_servers} | "
                f"[white]Total Tool Calls:[/white] {integration_summary.total_tool_calls} | "
                f"[white]Connections:[/white] {integration_summary.total_connections}"
            )

    def display_files_only(self):
        """Display only file editing metrics."""
        most_edited = self.file_parser.get_most_edited_files(limit=15)
        total_files = self.file_parser.get_total_file_count()
        total_versions = self.file_parser.get_total_versions()

        # Display compact logo header
        from rich.text import Text
        from rich.panel import Panel

        logo_text = Text(self.COMPACT_LOGO, style=f"bold #0770E3")
        subtitle = Text("File Editing Activity", style="#0770E3")

        logo_panel = Panel(
            logo_text,
            subtitle=subtitle,
            border_style="#0770E3",
            padding=(0, 2)
        )
        self.formatter.print_section(logo_panel)

        self.console.print(
            f"[white]Total Files Modified:[/white] {total_files} | "
            f"[white]Total Versions:[/white] {total_versions}\n"
        )

        self.formatter.print_section(
            self.tables.create_files_table(most_edited, limit=15)
        )

    def display_features_only(self):
        """Display Claude Code features (sub-agents, skills, MCPs, configuration)."""
        features_summary = self.features_analyzer.get_summary()

        # Display compact logo header
        from rich.text import Text
        from rich.panel import Panel

        logo_text = Text(self.COMPACT_LOGO, style=f"bold #0770E3")
        subtitle = Text("Claude Code Features", style="#0770E3")

        logo_panel = Panel(
            logo_text,
            subtitle=subtitle,
            border_style="#0770E3",
            padding=(0, 2)
        )
        self.formatter.print_section(logo_panel)

        # Summary stats
        self.console.print(
            f"[white]Sub-Agents Used:[/white] {features_summary.unique_subagents_used} | "
            f"[white]Total Agent Calls:[/white] {features_summary.total_subagent_calls} | "
            f"[white]Installed Skills:[/white] {features_summary.total_skills} | "
            f"[white]MCP Servers:[/white] {features_summary.total_mcp_servers}\n"
        )

        # Row 1: Sub-agents and Tools side by side
        if features_summary.subagent_stats:
            subagent_panel = Panel(
                Group(
                    self.formatter.create_section_header("🤖", "SUB-AGENTS"),
                    self.tables.create_subagent_table(features_summary.subagent_stats, limit=8)
                ),
                border_style="cyan",
                padding=(1, 2)
            )
        else:
            subagent_panel = None

        if features_summary.tool_stats:
            tools_panel = Panel(
                Group(
                    self.formatter.create_section_header("🔧", "TOP TOOLS"),
                    self.tables.create_tools_table(features_summary.tool_stats, limit=8)
                ),
                border_style="cyan",
                padding=(1, 2)
            )
        else:
            tools_panel = None

        if subagent_panel and tools_panel:
            self.console.print(Columns([subagent_panel, tools_panel], padding=(0, 2)))
        elif subagent_panel:
            self.console.print(subagent_panel)
        elif tools_panel:
            self.console.print(tools_panel)

        self.console.print()

        # Row 2: Skills and Configuration side by side
        skills_panel = Panel(
            Group(
                self.formatter.create_section_header("⚡", "INSTALLED SKILLS"),
                self.tables.create_skills_table(features_summary.installed_skills)
            ),
            border_style="cyan",
            padding=(1, 2)
        )

        config_data = {
            'always_thinking_enabled': features_summary.always_thinking_enabled,
            'enabled_plugins': features_summary.enabled_plugins
        }
        config_panel = Panel(
            Group(
                self.formatter.create_section_header("⚙️", "CONFIGURATION"),
                self.tables.create_config_table(config_data)
            ),
            border_style="cyan",
            padding=(1, 2)
        )

        self.console.print(Columns([skills_panel, config_panel], padding=(0, 2)))
        self.console.print()

        # Row 3: MCP Integrations (full width)
        if features_summary.mcp_stats:
            mcp_panel = Panel(
                Group(
                    self.formatter.create_section_header("🔌", "MCP INTEGRATIONS"),
                    self.tables.create_integration_table(
                        type('IntegrationSummary', (), {
                            'has_integrations': bool(features_summary.mcp_stats),
                            'top_servers': list(features_summary.mcp_stats.items())[:10],
                            'total_servers': features_summary.total_mcp_servers,
                            'total_tool_calls': sum(s.tool_call_count for s in features_summary.mcp_stats.values()),
                            'total_connections': sum(s.connection_count for s in features_summary.mcp_stats.values()),
                            'total_errors': 0
                        })()
                    )
                ),
                border_style="cyan",
                padding=(1, 2)
            )
            self.console.print(Columns([mcp_panel], padding=(0, 2)))
            self.console.print()
