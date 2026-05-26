"""
main entry point for the quickai application
"""

from pathlib import Path


class QuickAI:
    """QuickAI class"""

    def __init__(self, workspace: str | Path):
        """Initialize the QuickAI class"""
        self.workspace = workspace

    def start(self):
        """Start the QuickAI application"""
        print(f"Starting QuickAI in workspace: {self.workspace}")
