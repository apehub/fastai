"""Command-line interface for quickai."""

import argparse
from pathlib import Path

from quickai.quickai import QuickAI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    bot = QuickAI(workspace=Path(args.workspace).resolve())
    bot.start()
    return 0
