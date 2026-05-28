from __future__ import annotations

from fastai.commands.recon.models import ReconAnalysis, ReconFacts


class OverviewRenderer:
    """Render collected recon data into the system overview document."""

    def render(self, facts: ReconFacts, analysis: ReconAnalysis) -> str:
        """Build the markdown overview output.

        The first version deliberately renders only a small stable subset that
        aligns with the current tests. Future versions can weave richer analysis,
        ecosystem-specific sections and AI-authored summaries into this output.
        """

        lines = [
            "# System Overview",
            "",
            "## Project Summary",
            "",
            f"- Workspace: `{facts.workspace.root}`",
            f"- Total files: {facts.workspace.total_files}",
            f"- Markdown files: {len(facts.documentation.markdown_files)}",
            f"- Python modules: {len(facts.python_modules)}",
            "",
            "## Documentation",
            "",
        ]

        if facts.documentation.markdown_files:
            lines.extend(
                f"- `{path.as_posix()}`"
                for path in facts.documentation.markdown_files
            )
        else:
            lines.append("- No markdown documents found.")

        lines.extend(["", "## Python Modules", ""])
        if facts.python_modules:
            lines.extend(f"- `{path.as_posix()}`" for path in facts.python_modules)
        else:
            lines.append("- No Python modules found.")

        lines.extend(["", "## Analysis", ""])
        lines.append(f"- Framework summary: {analysis.framework_summary or 'Pending future analyzer.'}")
        lines.append(f"- Domain summary: {analysis.domain_summary or 'Pending future analyzer.'}")
        lines.append("")
        return "\n".join(lines)
