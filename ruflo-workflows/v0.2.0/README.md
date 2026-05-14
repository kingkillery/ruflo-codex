# ruflo-workflows

Workflow automation with templates, orchestration, and full state-machine lifecycle management.

## Install

```
/plugin marketplace add ruvnet/ruflo
/plugin install ruflo-workflows@ruflo
```

## Features

- **Workflow creation**: Define multi-step processes with conditions and parallel execution
- **Templates**: Reusable workflow patterns for common operations
- **Lifecycle management**: Execute, pause, resume, cancel running workflows
- **Approval gates**: Manual pause points for human review

## Commands

- `/workflow` -- List workflows, check status, view templates

## Skills

- `workflow-create` -- Create reusable workflow templates
- `workflow-run` -- Execute and manage running workflows

## Compatibility

- **CLI:** pinned to `@claude-flow/cli` v3.6 major+minor.
- **Verification:** `bash plugins/ruflo-workflows/scripts/smoke.sh` is the contract.

## MCP surface (10 tools)

All defined at `v3/@claude-flow/cli/src/mcp-tools/workflow-tools.ts`:

| Tool | Purpose |
|------|---------|
| `workflow_create` | Create a new workflow definition |
| `workflow_run` | Run a workflow with inputs |
| `workflow_execute` | Execute a one-shot workflow without persistence |
| `workflow_status` | Inspect a running workflow |
| `workflow_list` | List workflows |
| `workflow_pause` | Pause a running workflow |
| `workflow_resume` | Resume a paused workflow |
| `workflow_cancel` | Cancel a workflow |
| `workflow_delete` | Delete a workflow definition |
| `workflow_template` | Manage workflow templates |

## Lifecycle state machine

```
created â”€â”€runâ”€â”€â†’ running â”€â”€pauseâ”€â”€â†’ paused â”€â”€resumeâ”€â”€â†’ running
                    â”‚                  â”‚
                    â”‚                  â””â”€â”€cancelâ”€â”€â†’ cancelled
                    â”‚
                    â”œâ”€â”€completeâ”€â”€â†’ completed
                    â””â”€â”€cancelâ”€â”€â”€â”€â†’ cancelled
```

| State | Allowed transitions |
|-------|--------------------|
| `created` | `running` (via `workflow_run`), `cancelled` (via `workflow_cancel`) |
| `running` | `paused` (via `workflow_pause`), `completed` (auto), `cancelled` (via `workflow_cancel`) |
| `paused` | `running` (via `workflow_resume`), `cancelled` (via `workflow_cancel`) |
| `completed` | terminal |
| `cancelled` | terminal |

`workflow_execute` is the **stateless** path â€” fire-and-forget, no persisted state machine.

## Namespace coordination

This plugin owns the `workflows-state` AgentDB namespace (kebab-case, follows the convention from ruflo-agentdb namespace convention (original ruflo repo)). Reserved namespaces (`pattern`, `claude-memories`, `default`) MUST NOT be shadowed.

`workflows-state` indexes workflow definitions, current state, run history, and template metadata. Accessed via `memory_*` (namespace-routed).

## Verification

```bash
bash plugins/ruflo-workflows/scripts/smoke.sh
# Expected: "11 passed, 0 failed"
```

## Architecture Decisions

- [`ADR-0001` â€” ruflo-workflows plugin contract (10-tool MCP surface, lifecycle state machine, smoke as contract)](./docs/adrs/0001-workflows-contract.md)

## Related Plugins

- `ruflo-agentdb` â€” namespace convention owner
- `ruflo-loop-workers` â€” sibling automation surface (loops are recurring; workflows are stateful pipelines)
- `ruflo-sparc` â€” SPARC phase transitions can be modeled as workflows
