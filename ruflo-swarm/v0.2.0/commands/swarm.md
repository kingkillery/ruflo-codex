---
name: swarm
description: Initialize, monitor, and manage multi-agent swarms
---
$ARGUMENTS

Swarm lifecycle management.

**Init**: `npx @claude-flow/cli@latest swarm init --topology hierarchical --max-agents 8 --strategy specialized`
**Status**: `npx @claude-flow/cli@latest swarm status`
**Health**: `npx @claude-flow/cli@latest swarm health`
**Shutdown**: `npx @claude-flow/cli@latest swarm shutdown`

Parse $ARGUMENTS to determine the subcommand. If no arguments, show swarm status.

After init, use Codex `spawn_agent` only when the user explicitly asks for subagents or parallel delegation. Give each worker a bounded task and disjoint file ownership.
