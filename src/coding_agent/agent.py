from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from .config import AgentConfig
from .tools import LocalTools


class CodingAgent:
    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.client = OpenAI()
        self.tools = LocalTools(
            workspace_root=config.workspace_root,
            command_timeout_seconds=config.command_timeout_seconds,
        )

    def run(self, task: str) -> str:
        response = self.client.responses.create(
            model=self.config.model,
            instructions=self.config.instructions(),
            input=task,
            tools=self.tools.definitions(),
        )

        turns = 0
        while turns < self.config.max_turns:
            tool_outputs = self._collect_tool_outputs(response)
            if not tool_outputs:
                return getattr(response, "output_text", "").strip() or self._fallback_text(response)

            response = self.client.responses.create(
                model=self.config.model,
                previous_response_id=response.id,
                input=tool_outputs,
                tools=self.tools.definitions(),
            )
            turns += 1

        raise RuntimeError("Agent exceeded the maximum number of tool turns.")

    def _collect_tool_outputs(self, response: Any) -> list[dict[str, str]]:
        outputs: list[dict[str, str]] = []

        for item in getattr(response, "output", []):
            if getattr(item, "type", None) != "function_call":
                continue

            try:
                result = self.tools.execute(item.name, item.arguments)
            except Exception as exc:  # noqa: BLE001
                result = json.dumps({"error": str(exc)})

            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": result,
                }
            )

        return outputs

    def _fallback_text(self, response: Any) -> str:
        parts: list[str] = []
        for item in getattr(response, "output", []):
            if getattr(item, "type", None) != "message":
                continue
            for content in getattr(item, "content", []):
                text = getattr(content, "text", None)
                if text:
                    parts.append(text)
        return "\n".join(parts).strip()
