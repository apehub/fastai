"""Command-line interface for fastai."""

import argparse
from pathlib import Path

from fastai.fastai import FastAI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    bot = FastAI(workspace=Path(args.workspace).resolve())
    bot.start()
    return 0
