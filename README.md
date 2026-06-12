# Coding Agent

A small Python coding agent scaffold that uses the OpenAI Responses API plus a local tool layer to inspect files, edit files, and run shell commands inside the project workspace.

## What it does

- accepts a coding task from the CLI
- gives the model a constrained local toolkit
- loops on tool calls until the agent produces a final answer
- keeps file access inside the current workspace root

## Requirements

- Python 3.11+
- `uv`
- `OPENAI_API_KEY` available in your shell environment or a local `.env` file

## Setup

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

Optional `.env` file in the project root:

```bash
OPENAI_API_KEY=your_key_here
```

## Usage

Run a one-off task:

```bash
coding-agent "Create a Python function that validates email addresses."
```

Start an interactive session:

```bash
coding-agent
```

You can also choose a model explicitly:

```bash
coding-agent --model gpt-5.4 "Inspect this repo and suggest the first improvement."
```

## Notes

- The agent only reads and writes files under the workspace root.
- Shell commands run with a timeout and return stdout and stderr to the model.
- This is a starter project meant to be extended with stronger guardrails, richer diff editing, streaming, approval flows, and test hooks.
