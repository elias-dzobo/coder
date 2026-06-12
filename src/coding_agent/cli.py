from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from .agent import CodingAgent
from .config import AgentConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a local coding agent.")
    parser.add_argument("task", nargs="*", help="Task for the coding agent.")
    parser.add_argument("--model", default=None, help="Model name to use.")
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace root the agent is allowed to access.",
    )
    return parser


def interactive_loop(agent: CodingAgent) -> None:
    print("Interactive coding agent. Type 'exit' to quit.")
    while True:
        try:
            task = input("\n> ").strip()
        except EOFError:
            print()
            return

        if not task or task.lower() in {"exit", "quit"}:
            return

        print()
        print(agent.run(task))


def main() -> None:
    args = build_parser().parse_args()
    workspace_root = Path(args.workspace).resolve()
    load_dotenv(workspace_root / ".env")

    config = AgentConfig(workspace_root=workspace_root)
    if args.model:
        config.model = args.model

    agent = CodingAgent(config)

    if args.task:
        print(agent.run(" ".join(args.task)))
        return

    interactive_loop(agent)


if __name__ == "__main__":
    main()
