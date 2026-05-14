#!/usr/bin/env python3
"""Codex hook bridge for the local Ruflo plugin cache.

The bridge accepts Codex hook JSON on stdin and maps supported Codex events to
Ruflo/claude-flow hook subcommands. It is intentionally best-effort: hook
failures are reported to stderr but never block Codex execution.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}
    return payload if isinstance(payload, dict) else {"value": payload}


def first_string(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def nested(payload: dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for part in path:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def tool_name(payload: dict[str, Any]) -> str:
    value = payload.get("tool")
    tool = value.get("name") if isinstance(value, dict) else value
    return first_string(
        payload.get("tool_name"),
        tool,
        nested(payload, "event", "tool_name"),
        nested(payload, "event", "tool", "name"),
    )


def tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("tool_input") or payload.get("input") or nested(payload, "tool", "input") or nested(payload, "event", "tool_input")
    return value if isinstance(value, dict) else {}


def tool_response(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("tool_response") or payload.get("response") or nested(payload, "tool", "response") or nested(payload, "event", "tool_response")
    return value if isinstance(value, dict) else {}


def command_from(payload: dict[str, Any]) -> str:
    inputs = tool_input(payload)
    return first_string(inputs.get("command"), payload.get("command"), nested(payload, "tool", "command"))


def file_from(payload: dict[str, Any]) -> str:
    inputs = tool_input(payload)
    return first_string(
        inputs.get("file_path"),
        inputs.get("path"),
        inputs.get("target_file"),
        payload.get("file_path"),
        payload.get("path"),
    )


def query_from(payload: dict[str, Any]) -> str:
    inputs = tool_input(payload)
    return first_string(
        inputs.get("pattern"),
        inputs.get("query"),
        inputs.get("glob"),
        inputs.get("path"),
        payload.get("query"),
        payload.get("prompt"),
    )


def task_from(payload: dict[str, Any]) -> str:
    inputs = tool_input(payload)
    response = tool_response(payload)
    return first_string(
        inputs.get("description"),
        inputs.get("task"),
        inputs.get("message"),
        response.get("agent_id"),
        response.get("task_id"),
        payload.get("task_id"),
        payload.get("agent_id"),
    )


def prompt_from(payload: dict[str, Any]) -> str:
    return first_string(payload.get("prompt"), nested(payload, "event", "prompt"), nested(payload, "input", "prompt"), payload.get("raw"))


def session_from(payload: dict[str, Any]) -> str:
    return first_string(payload.get("session_id"), nested(payload, "event", "session_id"), payload.get("conversation_id"), "codex-session")


def message_from(payload: dict[str, Any]) -> str:
    return first_string(payload.get("message"), nested(payload, "event", "message"), payload.get("raw"))


def run_ruflo(args: list[str]) -> int:
    cmd = ["npx", "-y", "@claude-flow/cli@latest", *args]
    try:
        completed = subprocess.run(cmd, text=True, capture_output=True, timeout=20, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"ruflo hook skipped: {exc}", file=sys.stderr)
        return 0
    if completed.stdout.strip():
        print(completed.stdout.strip())
    if completed.returncode != 0 and completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)
    return 0


def is_shell_tool(name: str) -> bool:
    return name in {"shell_command", "bash", "shell", "functions.shell_command"}


def is_search_tool(name: str) -> bool:
    return name in {"read", "grep", "glob", "rg", "functions.shell_command"} or "search" in name or "grep" in name or "glob" in name


def is_subagent_tool(name: str) -> bool:
    return name in {"spawn_agent", "wait_agent", "send_input", "resume_agent", "close_agent", "task"} or "agent" in name


def is_mcp_tool(name: str) -> bool:
    return name.startswith("mcp__") or "mcp" in name or name.startswith("functions.") is False and "__" in name


def handle_pre(payload: dict[str, Any]) -> int:
    name = tool_name(payload).lower()
    command = command_from(payload)
    path = file_from(payload)
    query = query_from(payload)
    task = task_from(payload)

    if command or is_shell_tool(name):
        return run_ruflo(["hooks", "pre-command", "--command", command or name])
    if path and name in {"write", "edit", "multiedit", "apply_patch"}:
        return run_ruflo(["hooks", "pre-edit", "--file", path])
    if task and is_subagent_tool(name):
        return run_ruflo(["hooks", "pre-task", "--description", task[:200]])
    if query and is_search_tool(name):
        return run_ruflo(["hooks", "pre-search", "--query", query])
    if name and is_mcp_tool(name):
        return run_ruflo(["hooks", "mcp-pre", "--tool", name])
    if path:
        return run_ruflo(["hooks", "pre-edit", "--file", path])
    return 0


def handle_post(payload: dict[str, Any]) -> int:
    name = tool_name(payload).lower()
    command = command_from(payload)
    path = file_from(payload)
    query = query_from(payload)
    task = task_from(payload)

    if command or is_shell_tool(name):
        return run_ruflo(["hooks", "post-command", "--command", command or name, "--track-metrics", "true", "--store-results", "true"])
    if path and name in {"write", "edit", "multiedit", "apply_patch"}:
        return run_ruflo(["hooks", "post-edit", "--file", path, "--format", "true", "--update-memory", "true"])
    if task and is_subagent_tool(name):
        return run_ruflo(["hooks", "post-task", "--task-id", task, "--analyze-performance"])
    if query and is_search_tool(name):
        return run_ruflo(["hooks", "post-search", "--query", query, "--cache-results"])
    if name and is_mcp_tool(name):
        return run_ruflo(["hooks", "mcp-post", "--tool", name])
    if path:
        return run_ruflo(["hooks", "post-edit", "--file", path, "--format", "true", "--update-memory", "true"])
    return 0


def handle_user_prompt(payload: dict[str, Any]) -> int:
    prompt = prompt_from(payload)
    if not prompt:
        return 0
    return run_ruflo(["hooks", "route", "--task", prompt, "--include-explanation"])


def handle_session_start(payload: dict[str, Any]) -> int:
    return run_ruflo(["hooks", "session-start", "--session-id", session_from(payload), "--load-context"])


def handle_notification(payload: dict[str, Any]) -> int:
    message = message_from(payload)
    if not message:
        return 0
    return run_ruflo(["hooks", "notify", "--message", message, "--swarm-status"])


def handle_stop() -> int:
    return run_ruflo(["hooks", "session-end", "--generate-summary", "true", "--persist-state", "true", "--export-metrics", "true"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["pre", "post", "stop", "session-start", "user-prompt", "notification"], required=True)
    args = parser.parse_args()
    payload = read_payload()
    if args.phase == "pre":
        return handle_pre(payload)
    if args.phase == "post":
        return handle_post(payload)
    if args.phase == "session-start":
        return handle_session_start(payload)
    if args.phase == "user-prompt":
        return handle_user_prompt(payload)
    if args.phase == "notification":
        return handle_notification(payload)
    return handle_stop()


if __name__ == "__main__":
    raise SystemExit(main())