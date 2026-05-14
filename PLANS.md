# Ruflo-Codex Remaining Plans & Open Issues

> Generated after review-fixes commit (`8918ffe`).

## Open Issues

### 1. Mixed Version Directory Conventions
- **Problem**: Original 4 core plugins use commit-hash dirs (`cd0b66f0/`); Tier 1 plugins use semantic version dirs (`v0.2.0/`).
- **Impact**: Cosmetic inconsistency. Does not affect plugin loading or functionality.
- **Options**:
  1. **Standardize on semantic versions** — rename `cd0b66f0/` → `v0.2.0/` for core plugins (requires updating all `marketplace.json` paths).
  2. **Standardize on commit hashes** — rename `v0.2.0/` → `<hash>/` for Tier 1 plugins (requires re-copying from source).
  3. **Leave as-is** — document the convention difference in `CODEX-COMPATIBILITY.md`.
- **Decision needed**: Pick one and apply.

### 2. Tier 2 Plugin Port (Medium Effort)
Plugins that need namespace/path rework but are mostly self-contained:
- `ruflo-agentdb` — AgentDB memory bridge; references `claude-memories` namespace
- `ruflo-ruvector` — Vector search utilities; depends on agentdb embeddings
- `ruflo-intelligence` — ReasoningBank integration; deep `.claude` coupling
- `ruflo-knowledge-graph` — Graph memory layer; depends on agentdb

**Blocker**: These plugins reference excluded plugins internally. Need to either:
- Port as a bloc (agentdb → ruvector → intelligence → knowledge-graph), or
- Stub out missing dependencies with MCP-only fallbacks.

### 3. Tier 3 Plugin Port (High Effort / Redesign)
Plugins deeply coupled to Claude Code primitives. Likely require redesign rather than direct port:
- `ruflo-rag-memory` — Session `jsonl` parsing, memory bridge hooks
- `ruflo-cost-tracker` — Claude Code-specific token/usage tracking
- `ruflo-loop-workers` — `/loop` primitive, persistent worker pools
- `ruflo-aide` — Deep `CLAUDE.md` integration, session context scraping

**Blocker**: Codex lacks `/loop`, `ScheduleWakeup`, `Monitor` streams, and `Task` tool. These plugins would need to be rebuilt around bounded iteration + external scheduler patterns.

### 4. ADR Historical Records
- Some ADRs (e.g., `ruflo-autopilot/docs/adrs/0001-autopilot-contract.md`) intentionally reference excluded plugins as historical context.
- **Status**: Acceptable — ADRs document decisions, not current state. No action needed unless we want a "Codex port notes" appendix.

## Completed Work (for reference)

| Milestone | Commit | Description |
|-----------|--------|-------------|
| Initial port | `6b989e5` | 4 core plugins (core, swarm, autopilot, federation) + Python hook bridge + `.mcp.json` |
| Tier 1 plugins | `1657f3f` | 10 low-coupling plugins (browser, testgen, security-audit, aidefence, docs, adr, jujutsu, sparc, migrations, workflows) |
| Review fixes | `8918ffe` | Broken cross-refs fixed, smoke tests updated, ScheduleWakeup neutralized |

## Next Steps (prioritized)

1. **Decide on version directory convention** — pick option from Issue #1 and apply.
2. **Port Tier 2 plugins** — start with `ruflo-agentdb` as the dependency root.
3. **Add CI validation** — GitHub Action that validates all `plugin.json` files parse, `smoke.sh` patterns match READMEs, and no new broken cross-refs are introduced.
4. **Codex install test** — actually install the marketplace into a fresh Codex environment and verify plugins load.
