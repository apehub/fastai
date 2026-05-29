"""Base orchestration for a single agent-backed call flow.

A flow turns typed inputs into a typed, structured output by: building a
prompt, invoking an ``AgentRuntime``, and parsing the agent's response. FastAI
flows (recon, init analysis, drift detection, ...) subclass ``AgentFlow``;
the runtime supplies the intelligence, the flow owns the orchestration.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

from fastai.agents.runtimes import AgentInvokeOptions, AgentResult, AgentRuntime

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class AgentFlow(ABC, Generic[TInput, TOutput]):
    """Template for a prompt-build / invoke / parse call flow."""

    def __init__(
        self,
        runtime: AgentRuntime,
        *,
        workspace: Path | None = None,
        timeout: float = 600.0,
    ) -> None:
        self.runtime = runtime
        self.workspace = workspace
        self.timeout = timeout

    @abstractmethod
    def build_prompt(self, inputs: TInput) -> str:
        """Render the prompt sent to the agent runtime."""

    @abstractmethod
    def parse(self, result: AgentResult, inputs: TInput) -> TOutput:
        """Turn the runtime result into the structured flow output."""

    def run(self, inputs: TInput) -> TOutput:
        """Execute the full flow: build prompt, invoke runtime, parse result."""

        prompt = self.build_prompt(inputs)
        result = self.runtime.invoke(
            prompt,
            options=AgentInvokeOptions(workspace=self.workspace, timeout=self.timeout),
        )
        return self.parse(result, inputs)
