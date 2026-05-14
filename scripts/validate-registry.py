#!/usr/bin/env python3
"""
Ruflo-Codex registry validator.

Validates:
1. All plugin.json files parse as JSON and have required fields.
2. marketplace.json parses and references existing plugin directories.
3. Every marketplace plugin has both .codex-plugin/plugin.json and .claude-plugin/plugin.json.
4. Every plugin has a scripts/smoke.sh file.
5. No smoke.sh references excluded (unported) Tier-3 plugins as hard dependencies.
6. No README presents excluded plugins as installable.
"""

import glob
import json
import os
import re
import sys

EXCLUDED_PLUGINS = {
    "ruflo-rag-memory",
    "ruflo-cost-tracker",
    "ruflo-loop-workers",
    "ruflo-aide",
    "ruflo-daa",
    "ruflo-ddd",
    "ruflo-goals",
    "ruflo-iot-cognitum",
    "ruflo-market-data",
    "ruflo-neural-trader",
    "ruflo-observability",
    "ruflo-plugin-creator",
    "ruflo-ruvllm",
    "ruflo-rvf",
}

REQUIRED_PLUGIN_FIELDS = {"name", "version", "description", "author", "license", "keywords"}
REQUIRED_CODEX_FIELDS = {"name", "version", "description", "interface"}

errors = []
warnings = []


def error(msg: str):
    errors.append(msg)
    print(f"ERROR: {msg}")


def warn(msg: str):
    warnings.append(msg)
    print(f"WARN: {msg}")


def check_json_file(path: str, required_fields: set | None = None):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        error(f"{path}: invalid JSON - {e}")
        return None
    except FileNotFoundError:
        error(f"{path}: file not found")
        return None

    if required_fields:
        missing = required_fields - set(data.keys())
        if missing:
            error(f"{path}: missing required fields {missing}")

    return data


def main():
    # 1. Validate all plugin.json files
    codex_manifests = glob.glob("**/.codex-plugin/plugin.json", recursive=True)
    claude_manifests = glob.glob("**/.claude-plugin/plugin.json", recursive=True)

    print(f"Found {len(codex_manifests)} .codex-plugin/plugin.json files")
    print(f"Found {len(claude_manifests)} .claude-plugin/plugin.json files")

    for path in codex_manifests:
        check_json_file(path, REQUIRED_CODEX_FIELDS)

    for path in claude_manifests:
        check_json_file(path, REQUIRED_PLUGIN_FIELDS)

    # 2. Validate marketplace.json
    mp = check_json_file("marketplace.json", {"name", "plugins"})
    if mp is None:
        sys.exit(1)

    plugins = mp.get("plugins", [])
    print(f"marketplace.json lists {len(plugins)} plugins")

    seen_names = set()
    for entry in plugins:
        name = entry.get("name")
        if name in seen_names:
            error(f"marketplace.json: duplicate plugin entry '{name}'")
        seen_names.add(name)

        path = entry.get("source", {}).get("path")
        if not path:
            error(f"marketplace.json: '{name}' missing source.path")
            continue

        if not os.path.isdir(path):
            error(f"marketplace.json: '{name}' path '{path}' does not exist")
            continue

        # 3. Check dual manifests exist
        codex_json = os.path.join(path, ".codex-plugin", "plugin.json")
        claude_json = os.path.join(path, ".claude-plugin", "plugin.json")
        if not os.path.isfile(codex_json):
            error(f"'{name}': missing {codex_json}")
        if not os.path.isfile(claude_json):
            error(f"'{name}': missing {claude_json}")

        # 4. Check smoke.sh exists
        smoke = os.path.join(path, "scripts", "smoke.sh")
        if not os.path.isfile(smoke):
            warn(f"'{name}': missing {smoke}")
        else:
            # 5. Check smoke.sh doesn't reference excluded plugins as hard deps
            with open(smoke, encoding="utf-8") as f:
                content = f.read()
            for excluded in EXCLUDED_PLUGINS:
                if re.search(rf"\bgrep\b.*{re.escape(excluded)}\b", content):
                    error(f"'{name}' smoke.sh: hard dependency check on excluded plugin '{excluded}'")

    # 6. Check READMEs don't present excluded plugins as installable
    readme_paths = glob.glob("**/README.md", recursive=True)
    for readme in readme_paths:
        with open(readme, encoding="utf-8") as f:
            text = f.read()
        for excluded in EXCLUDED_PLUGINS:
            if re.search(rf"\bplugin install\b.*{re.escape(excluded)}\b", text):
                error(f"{readme}: references excluded plugin '{excluded}' as installable")

    print("\n" + "=" * 60)
    print(f"Validation complete: {len(errors)} errors, {len(warnings)} warnings")
    if errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
