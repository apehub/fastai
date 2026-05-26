"""
main entry point for the fastai application
"""

from pathlib import Path


class FastAI:
    """FastAI class"""

    def __init__(self, workspace: str | Path):
        """Initialize the FastAI class"""
        self.workspace = workspace

    def start(self):
        """Start the FastAI application"""
        print(f"Starting FastAI in workspace: {self.workspace}")
