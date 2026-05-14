# ruflo-autopilot

Bounded Codex autopilot support with learning and prediction.

Ruflo autopilot exposes prediction, progress, history, and learning MCP tools. Codex executes one bounded iteration at a time; persistent unattended loops require an external scheduler or explicit user continuation.

## Install

```
/plugin marketplace add ruvnet/ruflo
/plugin install ruflo-autopilot@ruflo
```

## Features

- **Bounded iteration**: Predict the next action, execute it in Codex, then log progress.
- **Progress tracking**: Monitors swarm tasks, file checklists, and current session plans.
- **Learning**: Discovers success patterns from completed tasks via AgentDB.
- **Prediction**: Predicts optimal next action based on state and learned patterns.
- **Scheduler-neutral**: Long-running loops are handled outside Codex or by user-directed continuation.

## Commands

- `/autopilot` -- Enable, configure, or disable autopilot.
- `/autopilot-status` -- Quick progress summary.

## Skills

- `autopilot-loop` -- Run one Codex-managed autopilot iteration.
- `autopilot-predict` -- Use learned patterns to pick the next bounded Codex action.

## MCP surface (10 tools)

| Tool | Purpose |
|------|---------|
| `autopilot_status` | Current autopilot state + learning stats |
| `autopilot_enable` | Turn autopilot on for the project |
| `autopilot_disable` | Turn autopilot off |
| `autopilot_config` | Read/update configuration |
| `autopilot_reset` | Clear learned patterns and progress (testing) |
| `autopilot_log` | Append a structured log entry |
| `autopilot_progress` | Progress summary across swarm/file/session tasks |
| `autopilot_learn` | Train on a completed task; writes to `autopilot-patterns` |
| `autopilot_history` | Browse past iterations |
| `autopilot_predict` | Predict the optimal next action from learned patterns |

All 10 are wired in `v3/@claude-flow/cli/src/mcp-tools/autopilot-tools.ts`.

## Compatibility

- **CLI:** pinned to `@claude-flow/cli` v3.6 major+minor.
- **MCP surface:** the 10 tools above.
- **Codex execution model:** one bounded iteration per invocation; Codex does not self-wake.
- **Verification:** `bash plugins/ruflo-autopilot/scripts/smoke.sh` is the legacy structural contract.

## Codex iteration model

Use autopilot as a next-action selector:

1. Check status and progress.
2. Predict the next action.
3. Execute the action directly in Codex.
4. Log and learn from the result.
5. Continue only when the remaining work is safe, bounded, and within the user's request.

For periodic or unattended execution, use an external scheduler, CI job, shell wrapper, or a user-requested follow-up session.

## Namespace coordination

This plugin owns the `autopilot-patterns` AgentDB namespace. Reserved namespaces (`pattern`, `claude-memories`, `default`) MUST NOT be shadowed.

`autopilot_learn` writes to this namespace via `agentdb_pattern-store` semantics and feeds the retrieve, judge, distill, and consolidate learning pipeline.

## Verification

```bash
bash plugins/ruflo-autopilot/scripts/smoke.sh
# Expected: "10 passed, 0 failed"
```

## Architecture Decisions

- [`ADR-0001` -- ruflo-autopilot plugin contract](./docs/adrs/0001-autopilot-contract.md)