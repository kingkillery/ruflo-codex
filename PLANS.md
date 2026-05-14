# Ruflo-Codex Remaining Plans & Open Issues

> Generated after review-fixes commit (`8918ffe`).

## Open Issues

### 1. Mixed Version Directory Conventions ✅ RESOLVED
- **Problem**: Original 4 core plugins use commit-hash dirs (`cd0b66f0/`); Tier 1 plugins use semantic version dirs (`v0.2.0/`).
- **Resolution**: Standardized on semantic versions. Renamed `cd0b66f0/` → `v0.2.0/` for all 4 core plugins. Updated `marketplace.json` and `.agents/plugins/marketplace.json`.
- **Commit**: `0d8af09`

### 2. Tier 2 Plugin Port (Medium Effort) ✅ COMPLETED
Plugins ported as a bloc — all are documentation-only MCP surfaces with no Claude-specific primitives:
- `ruflo-agentdb` v0.3.0 — AgentDB memory bridge (15 `agentdb_*` MCP tools)
- `ruflo-ruvector` v0.2.1 — Vector search utilities via `ruvector@0.2.25`
- `ruflo-intelligence` v0.3.0 — SONA neural patterns, 3-tier model routing
- `ruflo-knowledge-graph` v0.2.0 — Entity extraction, pathfinder traversal

**Commit**: `9a235d5`
**Validation**: `scripts/validate-registry.py` passes (0 errors, 0 warnings).

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

1. ~~**Decide on version directory convention** — done.~~
2. ~~**Port Tier 2 plugins** — done.~~
3. ~~**Add CI validation** — GitHub Action added (`scripts/validate-registry.py` + `.github/workflows/validate.yml`).~~
4. ~~**Codex install test** — dry-run install test passes for all 18 plugins (`scripts/test-codex-install.py`). Live Codex API test deferred to avoid token costs.~~
5. **Push latest changes to GitHub** — ensure `kingkillery/ruflo-codex` is up to date.
6. **Tier 3 decision** — evaluate whether excluded plugins (rag-memory, cost-tracker, loop-workers, aide) warrant redesign or can remain excluded.
