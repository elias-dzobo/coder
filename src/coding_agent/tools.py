from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Any, Callable


ToolHandler = Callable[..., dict[str, Any]]


@dataclass(slots=True)
class LocalTools:
    workspace_root: Path
    command_timeout_seconds: int = 20

    def definitions(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "name": "list_files",
                "description": "List files and directories under a workspace-relative path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path under the workspace root.",
                            "default": ".",
                        }
                    },
                    "required": [],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "read_file",
                "description": "Read a text file from the workspace, optionally by line range.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Relative file path."},
                        "start_line": {
                            "type": "integer",
                            "description": "1-based starting line number.",
                            "default": 1,
                        },
                        "end_line": {
                            "type": "integer",
                            "description": "1-based ending line number, inclusive.",
                            "default": 200,
                        },
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "write_file",
                "description": "Write a full text file under the workspace root, creating parent directories as needed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Relative file path."},
                        "content": {"type": "string", "description": "Full file contents."},
                    },
                    "required": ["path", "content"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "run_command",
                "description": "Run a shell command inside the workspace root and capture output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command to execute."}
                    },
                    "required": ["command"],
                    "additionalProperties": False,
                },
            },
        ]

    def handlers(self) -> dict[str, ToolHandler]:
        return {
            "list_files": self.list_files,
            "read_file": self.read_file,
            "write_file": self.write_file,
            "run_command": self.run_command,
        }

    def list_files(self, path: str = ".") -> dict[str, Any]:
        target = self._resolve(path)
        entries = sorted(target.iterdir(), key=lambda item: (item.is_file(), item.name.lower()))
        return {
            "path": str(target.relative_to(self.workspace_root)),
            "entries": [
                {
                    "name": entry.name,
                    "path": str(entry.relative_to(self.workspace_root)),
                    "type": "file" if entry.is_file() else "directory",
                }
                for entry in entries
            ],
        }

    def read_file(self, path: str, start_line: int = 1, end_line: int = 200) -> dict[str, Any]:
        target = self._resolve(path)
        lines = target.read_text(encoding="utf-8").splitlines()
        start = max(start_line, 1)
        end = max(end_line, start)
        selection = lines[start - 1 : end]
        return {
            "path": str(target.relative_to(self.workspace_root)),
            "start_line": start,
            "end_line": start + len(selection) - 1,
            "content": "\n".join(selection),
        }

    def write_file(self, path: str, content: str) -> dict[str, Any]:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {
            "path": str(target.relative_to(self.workspace_root)),
            "bytes_written": len(content.encode("utf-8")),
        }

    def run_command(self, command: str) -> dict[str, Any]:
        completed = subprocess.run(
            command,
            cwd=self.workspace_root,
            shell=True,
            text=True,
            capture_output=True,
            timeout=self.command_timeout_seconds,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    def execute(self, name: str, arguments: str) -> str:
        handler = self.handlers().get(name)
        if handler is None:
            raise ValueError(f"Unknown tool: {name}")

        parsed = json.loads(arguments or "{}")
        result = handler(**parsed)
        return json.dumps(result)

    def _resolve(self, path: str) -> Path:
        candidate = (self.workspace_root / path).resolve()
        try:
            candidate.relative_to(self.workspace_root)
        except ValueError as exc:
            raise ValueError("Path must stay inside the workspace root.") from exc
        return candidate
