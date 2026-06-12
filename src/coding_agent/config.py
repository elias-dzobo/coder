from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(slots=True)
class AgentConfig:
    model: str = os.getenv("CODING_AGENT_MODEL", "gpt-5.4")
    max_turns: int = int(os.getenv("CODING_AGENT_MAX_TURNS", "12"))
    command_timeout_seconds: int = int(os.getenv("CODING_AGENT_COMMAND_TIMEOUT", "20"))
    workspace_root: Path = Path.cwd()

    def instructions(self) -> str:
        return (
            "You are a careful software engineering agent working inside a local project. "
            "Prefer reading relevant files before editing. "
            "Keep changes scoped to the user's request. "
            "Use shell commands when they meaningfully help, but avoid destructive actions. "
            "Only touch files inside the workspace root."
        )
