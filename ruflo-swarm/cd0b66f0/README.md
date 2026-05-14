# ruflo-swarm

Codex-safe swarm coordination, status tracking, and work partitioning.

## Install

```
/plugin marketplace add ruvnet/ruflo
/plugin install ruflo-swarm@ruflo
```

## What's Included

- **Swarm records**: Ruflo records topology, agent state, and coordination metadata.
- **Topologies**: hierarchical, mesh, hierarchical-mesh, ring, star, adaptive.
- **Bounded status checks**: Use MCP or CLI status/health checks from Codex.
- **Work partitioning guidance**: Use Codex subagents only when the user explicitly asks for delegation or parallel work.
- **Hive-Mind Consensus**: Byzantine, Raft, Gossip, CRDT, and Quorum strategies in Ruflo state.
- **Anti-Drift**: hierarchical topology with specialized strategy for tight coordination.

## Requires

- `ruflo-core` plugin (provides MCP server)

## Compatibility

- **CLI:** pinned to `@claude-flow/cli` v3.6 major+minor.
- **Codex execution model:** Ruflo coordinates; Codex writes code, runs commands, and owns final integration.
- **Verification:** `bash plugins/ruflo-swarm/scripts/smoke.sh` is the legacy structural contract.

## MCP surface (12 tools)

| Family | Count | Tools |
|--------|------:|-------|
| `swarm_*` | 4 | `swarm_init`, `swarm_status`, `swarm_shutdown`, `swarm_health` |
| `agent_*` | 8 | `agent_spawn`, `agent_execute`, `agent_terminate`, `agent_status`, `agent_list`, `agent_pool`, `agent_health`, `agent_update` |

Sources: `v3/@claude-flow/cli/src/mcp-tools/swarm-tools.ts:71, 145, 208, 270` and `agent-tools.ts:182, 287, 319, 356, 395, 451, 573, 651`.

## Codex coordination model

Ruflo swarm tools create coordination records. They do not execute code by themselves.

| Codex action | Use |
|-------------|-----|
| Local Codex work | Immediate implementation, verification, and integration |
| `spawn_agent` | Only after the user explicitly asks for subagents or parallel delegation |
| `send_input` | Coordinate with an existing authorized Codex subagent |
| Ruflo memory/task tools | Store progress, state, and reusable patterns |
| Bounded shell status checks | Inspect `swarm status` or `swarm health` without indefinite streaming |

## Anti-drift defaults

For coding swarms, use defaults that prevent agent drift:

| Setting | Value | Rationale |
|---------|-------|-----------|
| `topology` | `hierarchical` | Coordinator catches divergence |
| `maxAgents` | 6-8 | Smaller team = less drift |
| `strategy` | `specialized` | Clear roles, no overlap |
| `consensus` | `raft` | Leader maintains authoritative state |
| `memory` | `hybrid` | SQLite + AgentDB for both fast + durable |

For 10+ agent teams, use `hierarchical-mesh` (queen + peer communication).

## Namespace coordination

This plugin owns the `swarm-state` AgentDB namespace. Reserved namespaces (`pattern`, `claude-memories`, `default`) MUST NOT be shadowed.

`swarm-state` indexes active swarms, agent assignments, and topology snapshots. Accessed via `memory_*` namespace-routed tools.

## Verification

```bash
bash plugins/ruflo-swarm/scripts/smoke.sh
# Expected: "11 passed, 0 failed"
```

## Architecture Decisions

- [`ADR-0001` -- ruflo-swarm plugin contract](./docs/adrs/0001-swarm-contract.md)

## Related Plugins

- `ruflo-agentdb` -- namespace convention owner
- `ruflo-autopilot` -- bounded prediction and learning for next-action selection
- `ruflo-intelligence` -- routing and recommendation intelligence