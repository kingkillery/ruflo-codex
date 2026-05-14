---
name: autopilot
description: Enable, configure, or disable autonomous task completion
---
$ARGUMENTS
Manage Ruflo autopilot for bounded autonomous task completion under Codex.

Usage:
- `/autopilot enable` -- Enable autopilot and start the completion loop
- `/autopilot disable` -- Disable autopilot, let agents stop
- `/autopilot config --max-iterations 50 --timeout 30` -- Set limits
- `/autopilot reset` -- Reset iteration counter and restart timer
- `/autopilot learn` -- Discover success patterns from completed tasks
- `/autopilot history KEYWORD` -- Search past completion episodes

Parse $ARGUMENTS to determine the subcommand. If no arguments, show status via `autopilot_status`.

After enabling, use the `autopilot-loop` skill to run one bounded autonomous iteration per Codex turn. For repeated execution, rely on an external scheduler, CI job, or user-requested follow-up session.
