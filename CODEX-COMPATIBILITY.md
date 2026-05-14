# Ruflo Codex Compatibility

This Codex marketplace cache is intentionally a curated Ruflo subset, not a full port of the Claude Flow native `.claude` content tree.

## Decision

Do not bulk-port the full `.claude` content tree from the original ruflo repository into Codex skills by default.

The Claude tree contains a large Claude Code-native surface: many agents, slash commands, hook prompts, and workflow assumptions that rely on Claude-only primitives. Importing it wholesale would create noisy or misleading Codex instructions unless each item is reviewed and translated.

## Current Codex Scope

The Codex cache exposes 14 plugins:

**Core (4)**
- `ruflo-core`: MCP server configuration, hooks, core discovery/init/doctor skills, and generalist guidance.
- `ruflo-swarm`: Codex-safe swarm coordination patterns.
- `ruflo-autopilot`: bounded autopilot prediction, progress, and learning guidance.
- `ruflo-federation`: federation status, init, and audit workflows.

**Tier 1 — high-value, low Claude-coupling (10)**
- `ruflo-browser`: Playwright automation (navigate, click, screenshot, scrape).
- `ruflo-testgen`: TDD workflow, test gap detection, coverage routing.
- `ruflo-security-audit`: CVE scanning, dependency checks, static analysis.
- `ruflo-aidefence`: PII detection, prompt-injection defense, sanitization.
- `ruflo-docs`: Doc generation, drift detection, API docs.
- `ruflo-adr`: Architecture decision records, code-to-ADR linking.
- `ruflo-jujutsu`: Diff risk scoring, PR review, git workflow.
- `ruflo-sparc`: SPARC methodology (Spec-Pseudocode-Architecture-Refinement-Completion).
- `ruflo-migrations`: Database schema migrations, up/down pairs, dry-run.
- `ruflo-workflows`: Repeatable multi-step processes, parallel execution.

Ruflo coordinates state and memory. Codex remains responsible for writing code, running commands, editing files, and deciding when to use Codex subagents.

## Porting Rule

Port additional Claude Flow content only when there is a concrete Codex use case.

For each candidate skill, command, or agent:

1. Remove or translate Claude-only primitives.
2. Prefer MCP tools and Codex-native shell/subagent workflows.
3. Keep the write scope narrow and validated.
4. Add tests or at least JSON/frontmatter parsing checks when applicable.
5. Document any remaining platform limitation instead of pretending feature parity.

## Known Non-Goals

- No automatic persistent wakeup loop inside Codex.
- No wholesale slash-command import.
- No blind import of all Claude agents.
- No prompt-hook parity where Codex does not expose the same hook behavior.