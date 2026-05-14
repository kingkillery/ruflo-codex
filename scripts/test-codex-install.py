#!/usr/bin/env python3
"""
Codex install test — validates that the Ruflo marketplace can be consumed by Codex.

This is a dry-run test: it validates manifest structure, plugin paths, and schema
conformance without making any API calls or modifying the user's Codex config.
"""

import glob
import json
import os
import re
import sys

# Based on official OpenAI bundled plugin manifests (browser-use, chrome, latex-tectonic)
REQUIRED_CODEX_FIELDS = {
    "name",
    "version",
    "description",
    "author",
    "license",
    "keywords",
    "skills",
    "interface",
}

REQUIRED_INTERFACE_FIELDS = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "websiteURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
    "defaultPrompt",
    "brandColor",
    "screenshots",
}

VALID_CATEGORIES = {"Coding", "Engineering", "Productivity", "Research"}
VALID_CAPABILITIES = {"Interactive", "Read", "Write"}

errors = []
warnings = []


def error(msg: str):
    errors.append(msg)
    print(f"ERROR: {msg}")


def warn(msg: str):
    warnings.append(msg)
    print(f"WARN: {msg}")


def validate_plugin_manifest(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        error(f"{path}: invalid JSON - {e}")
        return

    missing = REQUIRED_CODEX_FIELDS - set(data.keys())
    if missing:
        error(f"{path}: missing required fields {missing}")

    iface = data.get("interface", {})
    missing_iface = REQUIRED_INTERFACE_FIELDS - set(iface.keys())
    if missing_iface:
        error(f"{path}: interface missing fields {missing_iface}")

    category = iface.get("category")
    if category and category not in VALID_CATEGORIES:
        warn(f"{path}: unusual category '{category}'")

    caps = iface.get("capabilities", [])
    invalid_caps = set(caps) - VALID_CAPABILITIES
    if invalid_caps:
        warn(f"{path}: unusual capabilities {invalid_caps}")

    skills_path = data.get("skills")
    if skills_path:
        abs_skills = os.path.join(os.path.dirname(os.path.dirname(path)), skills_path)
        if not os.path.isdir(abs_skills):
            error(f"{path}: skills path '{skills_path}' does not resolve to a directory")
        else:
            skill_files = glob.glob(os.path.join(abs_skills, "*/SKILL.md"))
            if not skill_files:
                warn(f"{path}: no SKILL.md files found in skills directory")
            else:
                print(f"  -> {len(skill_files)} skill(s) found")


def main():
    print("=" * 60)
    print("Codex Install Test (dry-run)")
    print("=" * 60)

    # 1. Validate marketplace.json
    if not os.path.isfile("marketplace.json"):
        error("marketplace.json not found")
        sys.exit(1)

    try:
        with open("marketplace.json", encoding="utf-8") as f:
            mp = json.load(f)
    except json.JSONDecodeError as e:
        error(f"marketplace.json: invalid JSON - {e}")
        sys.exit(1)

    plugins = mp.get("plugins", [])
    print(f"\nMarketplace '{mp.get('name')}' lists {len(plugins)} plugins\n")

    # 2. Validate each plugin
    for entry in plugins:
        name = entry.get("name", "UNKNOWN")
        path = entry.get("source", {}).get("path")
        print(f"Testing {name} ...")

        if not path:
            error(f"{name}: missing source.path")
            continue

        if not os.path.isdir(path):
            error(f"{name}: path '{path}' does not exist")
            continue

        codex_json = os.path.join(path, ".codex-plugin", "plugin.json")
        if not os.path.isfile(codex_json):
            error(f"{name}: missing {codex_json}")
            continue

        validate_plugin_manifest(codex_json)

    # 3. Summary
    print("\n" + "=" * 60)
    print(f"Install test complete: {len(errors)} errors, {len(warnings)} warnings")
    if errors:
        print("FAIL — plugins would not load correctly in Codex")
        sys.exit(1)
    if warnings:
        print("PASS with warnings — plugins should load but may have minor issues")
    else:
        print("PASS — all plugins are ready for Codex")
    sys.exit(0)


if __name__ == "__main__":
    main()
