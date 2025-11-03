"""Table builders for displaying metrics."""

from rich.table import Table
from rich.text import Text

from ..analyzers.usage import UsageSummary
from ..analyzers.tokens import TokenSummary, TokenAnalyzer
from ..analyzers.integrations import IntegrationSummary
from ..analyzers.features import FeaturesSummary
from ..parsers.files import FileStats
from ..parsers.tools import ToolStats
from .formatter import DisplayFormatter


class MetricTables:
    """Builds rich tables for various metrics."""

    def __init__(self, formatter: DisplayFormatter):
        """
        Initialize metric tables builder.

        Args:
            formatter: DisplayFormatter instance
        """
        self.formatter = formatter

    def create_usage_table(self, summary: UsageSummary) -> Table:
        """
        Create usage summary table.

        Args:
            summary: UsageSummary instance

        Returns:
            Rich Table instance
        """
        table = self.formatter.create_metric_table()
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="white", justify="right", width=16)

        table.add_row("Total Sessions", self.formatter.format_large_number(summary.total_sessions))
        table.add_row("Total Commands", self.formatter.format_large_number(summary.total_commands))
        table.add_row("Total Messages", self.formatter.format_large_number(summary.total_messages))
        table.add_row("Active Projects", str(summary.active_projects))

        if summary.date_range_days is not None:
            table.add_row("Time Range", f"{summary.date_range_days} days")

        if summary.avg_commands_per_day:
            table.add_row("Avg Commands/Day", f"{summary.avg_commands_per_day:.1f}")

        if summary.avg_sessions_per_day:
            table.add_row("Avg Sessions/Day", f"{summary.avg_sessions_per_day:.1f}")

        return table

    def create_token_table(self, summary: TokenSummary) -> Table:
        """
        Create token usage and cost table.

        Args:
            summary: TokenSummary instance

        Returns:
            Rich Table instance
        """
        table = self.formatter.create_metric_table()
        table.add_column("Token Type", style="cyan", width=28)
        table.add_column("Count", style="white", justify="right", width=8)
        table.add_column("Cost", style="white", justify="right", width=8)

        tokens = summary.total_tokens
        costs = summary.cost_breakdown

        # Input tokens
        table.add_row(
            "Input",
            TokenAnalyzer.format_token_count(tokens.input_tokens),
            str(self.formatter.format_cost(costs.input_cost))
        )

        # Output tokens
        table.add_row(
            "Output",
            TokenAnalyzer.format_token_count(tokens.output_tokens),
            str(self.formatter.format_cost(costs.output_cost))
        )

        # Cache write tokens
        table.add_row(
            "Cache Write",
            TokenAnalyzer.format_token_count(tokens.cache_creation_input_tokens),
            str(self.formatter.format_cost(costs.cache_write_cost))
        )

        # Cache read tokens
        table.add_row(
            "Cache Read",
            TokenAnalyzer.format_token_count(tokens.cache_read_input_tokens),
            str(self.formatter.format_cost(costs.cache_read_cost))
        )

        # Separator
        table.add_row("─" * 15, "─" * 10, "─" * 8, style="dim")

        # Total
        total_tokens = tokens.total_input_tokens + tokens.output_tokens
        table.add_row(
            Text("TOTAL", style="bold"),
            TokenAnalyzer.format_token_count(total_tokens),
            str(self.formatter.format_cost(costs.total_cost))
        )

        # Cache savings
        if costs.cache_savings > 0:
            savings_text = Text("Cache Savings", style="green")
            table.add_row(
                savings_text,
                "",
                Text(f"-${costs.cache_savings:.2f}", style="green")
            )

        return table

    def create_cache_efficiency_display(self, summary: TokenSummary) -> Text:
        """
        Create cache efficiency display with progress bar.

        Args:
            summary: TokenSummary instance

        Returns:
            Rich Text instance
        """
        percentage = summary.cache_efficiency_pct
        bar = self.formatter.create_progress_bar(percentage, width=20)

        text = Text("Cache Efficiency: ", style="white")
        text.append(bar + " ")
        text.append(self.formatter.format_percentage(percentage))

        return text

    def create_project_table(self, breakdown: dict, limit: int = 10) -> Table:
        """
        Create top projects table.

        Args:
            breakdown: Project breakdown dict
            limit: Maximum number of projects to show

        Returns:
            Rich Table instance
        """
        table = self.formatter.create_metric_table()
        table.add_column("Project", style="cyan", no_wrap=False, width=28)
        table.add_column("Sessions", justify="right", width=8)
        table.add_column("Commands", justify="right", width=8)

        for i, (project_path, data) in enumerate(breakdown.items()):
            if i >= limit:
                break

            name = data['name']
            sessions = str(data['sessions'])
            commands = str(data['commands'])

            table.add_row(name, sessions, commands)

        return table

    def create_integration_table(self, summary: IntegrationSummary) -> Table:
        """
        Create MCP integrations table.

        Args:
            summary: IntegrationSummary instance

        Returns:
            Rich Table instance
        """
        table = self.formatter.create_metric_table()
        table.add_column("Server", style="cyan", width=56)
        table.add_column("Tool Calls", justify="right", width=12)
        table.add_column("Connections", justify="right", width=12)
        table.add_column("Projects", style="white", no_wrap=False, width=18)

        if not summary.has_integrations:
            table.add_row(Text("No integrations found", style="dim italic"), "", "", "")
            return table

        for server_name, stats in summary.top_servers:
            # Format projects list
            projects_list = sorted(stats.projects)
            if len(projects_list) > 3:
                projects_str = ", ".join(projects_list[:3]) + f" (+{len(projects_list)-3} more)"
            else:
                projects_str = ", ".join(projects_list) if projects_list else "-"

            table.add_row(
                server_name,
                str(stats.tool_call_count),
                str(stats.connection_count),
                projects_str
            )

        return table

    def create_files_table(self, files: list[FileStats], limit: int = 10) -> Table:
        """
        Create most edited files table.

        Args:
            files: List of FileStats
            limit: Maximum number of files to show

        Returns:
            Rich Table instance
        """
        table = self.formatter.create_metric_table()
        table.add_column("File", style="cyan", no_wrap=False, width=78)
        table.add_column("Versions", justify="right", width=10)
        table.add_column("Size", justify="right", width=10)

        for i, file_stat in enumerate(files):
            if i >= limit:
                break

            table.add_row(
                file_stat.file_path,
                str(file_stat.version_count),
                f"{file_stat.size_kb:.1f} KB"
            )

        if not files:
            table.add_row(Text("No file history found", style="dim italic"), "", "")

        return table

    def create_project_tokens_table(self, project_tokens: dict, limit: int = 10) -> Table:
        """
        Create per-project token usage table.

        Args:
            project_tokens: Dict mapping project paths to TokenSummary
            limit: Maximum number of projects to show

        Returns:
            Rich Table instance
        """
        table = self.formatter.create_metric_table()
        table.add_column("Project", style="cyan", no_wrap=False, width=20)
        table.add_column("Tokens", justify="right", width=8)
        table.add_column("Cost", justify="right", width=7)
        table.add_column("Cache", justify="right", width=7)

        for i, (project_path, summary) in enumerate(project_tokens.items()):
            if i >= limit:
                break

            # Shorten project name
            project_name = project_path.split('/')[-1] if '/' in project_path else project_path

            total_tokens = summary.total_tokens.total_input_tokens + summary.total_tokens.output_tokens

            table.add_row(
                project_name,
                TokenAnalyzer.format_token_count(total_tokens),
                f"${summary.total_cost:.2f}",
                f"{summary.cache_efficiency_pct:.1f}%"
            )

        if not project_tokens:
            table.add_row(Text("No project data", style="dim italic"), "", "", "")

        return table

    def create_subagent_table(self, subagent_stats: dict[str, ToolStats], limit: int = 10) -> Table:
        """
        Create sub-agents usage table.

        Args:
            subagent_stats: Dict mapping subagent types to ToolStats
            limit: Maximum number of sub-agents to show

        Returns:
            Rich Table instance
        """
        table = self.formatter.create_metric_table()
        table.add_column("Sub-Agent", style="cyan", width=26)
        table.add_column("Calls", justify="right", width=7)
        table.add_column("Tokens", justify="right", width=7)
        table.add_column("Sessions", justify="right", width=7)

        for i, (agent_type, stats) in enumerate(subagent_stats.items()):
            if i >= limit:
                break

            table.add_row(
                agent_type,
                str(stats.invocation_count),
                TokenAnalyzer.format_token_count(stats.total_tokens),
                str(stats.session_count)
            )

        if not subagent_stats:
            table.add_row(Text("No sub-agents used", style="dim italic"), "", "", "")

        return table

    def create_tools_table(self, tool_stats: dict[str, ToolStats], limit: int = 10) -> Table:
        """
        Create tools usage table.

        Args:
            tool_stats: Dict mapping tool names to ToolStats
            limit: Maximum number of tools to show

        Returns:
            Rich Table instance
        """
        table = self.formatter.create_metric_table()
        table.add_column("Tool", style="cyan", width=30)
        table.add_column("Calls", justify="right", width=8)
        table.add_column("Tokens", justify="right", width=8)

        for i, (tool_name, stats) in enumerate(tool_stats.items()):
            if i >= limit:
                break

            table.add_row(
                tool_name,
                str(stats.invocation_count),
                TokenAnalyzer.format_token_count(stats.total_tokens)
            )

        return table

    def create_skills_table(self, skills: list) -> Table:
        """
        Create installed skills table.

        Args:
            skills: List of SkillInfo instances

        Returns:
            Rich Table instance
        """
        table = self.formatter.create_metric_table()
        table.add_column("Skill", style="cyan", width=26)
        table.add_column("Description", style="white", no_wrap=False, width=21)

        for skill in skills:
            desc = skill.description if skill.description else Text("No description", style="dim italic")
            table.add_row(skill.name, desc)

        if not skills:
            table.add_row(Text("No skills installed", style="dim italic"), "")

        return table

    def create_config_table(self, config_data: dict) -> Table:
        """
        Create configuration table.

        Args:
            config_data: Dict with configuration data

        Returns:
            Rich Table instance
        """
        table = self.formatter.create_metric_table()
        table.add_column("Setting", style="cyan", width=30)
        table.add_column("Value", style="white", no_wrap=False, width=16)

        # Always thinking
        always_thinking = config_data.get('always_thinking_enabled', False)
        thinking_text = Text("Enabled", style="green") if always_thinking else Text("Disabled", style="dim")
        table.add_row("Always Thinking", thinking_text)

        # Enabled plugins
        plugins = config_data.get('enabled_plugins', {})
        if plugins:
            plugin_list = ", ".join([p.split('@')[0] for p, enabled in plugins.items() if enabled])
            table.add_row("Enabled Plugins", plugin_list if plugin_list else Text("None", style="dim"))

        return table

    def create_model_usage_table(self, model_breakdown: dict) -> Table:
        """
        Create model usage breakdown table.

        Args:
            model_breakdown: Dict mapping model names to (TokenUsage, cost) tuples

        Returns:
            Rich Table instance
        """
        table = self.formatter.create_metric_table()
        table.add_column("Model", style="cyan", width=28)
        table.add_column("Tokens", justify="right", width=8)
        table.add_column("Cost", justify="right", width=8)

        for model_name, (tokens, cost) in model_breakdown.items():
            # Simplify model name
            if "claude-" in model_name:
                simple_name = model_name.replace("claude-", "").replace("-20250929", "").replace("-20251001", "").replace("-20250514", "")
                simple_name = simple_name.replace("-", " ").title()
            else:
                simple_name = model_name

            total_tokens = tokens.total_input_tokens + tokens.output_tokens

            table.add_row(
                simple_name,
                TokenAnalyzer.format_token_count(total_tokens),
                f"${cost:.2f}"
            )

        if not model_breakdown:
            table.add_row(Text("No model data", style="dim italic"), "", "")

        return table

    def create_model_by_project_table(self, project_model_breakdown: dict, limit: int = 10) -> Table:
        """
        Create model usage by project table.

        Args:
            project_model_breakdown: Dict mapping projects to model usage
            limit: Maximum number of rows to show

        Returns:
            Rich Table instance
        """
        table = self.formatter.create_metric_table()
        table.add_column("Project", style="cyan", width=30)
        table.add_column("Models Used", style="white", no_wrap=False, width=16)

        row_count = 0
        for project, models in project_model_breakdown.items():
            if row_count >= limit:
                break

            # Simplify project name
            project_name = project.split('/')[-1] if '/' in project else project

            # Format models with their costs
            model_list = []
            for model_name, (tokens, cost) in list(models.items())[:2]:  # Show top 2 models
                # Simplify model name
                if "claude-" in model_name:
                    simple_name = model_name.replace("claude-", "").split("-")[0].title()
                else:
                    simple_name = model_name
                model_list.append(f"{simple_name} (${cost:.0f})")

            if len(models) > 2:
                model_list.append(f"+{len(models)-2} more")

            models_str = ", ".join(model_list)

            table.add_row(project_name, models_str)
            row_count += 1

        if not project_model_breakdown:
            table.add_row(Text("No project data", style="dim italic"), "")

        return table
