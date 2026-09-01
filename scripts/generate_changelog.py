#!/usr/bin/env python3
"""Generate changelog.md and release notes from changelog.yaml.

Usage:
    generate_changelog.py [--changelog changelog.yaml] [--md changelog.md]
                          [--notes release_notes.md] [--print-version]

changelog.md is regenerated in the Keep a Changelog 1.1.0 format.
release_notes.md contains the body of the latest version entry.
"""

import argparse
import datetime
import sys

import yaml

HEADER = """# geometry changelog

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).
"""

REPOSITORY = "https://github.com/geometry-zsh/geometry"


def render_changes(changes):
    """Render a changes mapping as '### Type' sections, preserving order."""
    parts = []
    for change_type, items in (changes or {}).items():
        if not items:
            continue
        section = f"### {change_type.capitalize()}\n"
        section += "\n".join(f"- {item}" for item in items)
        parts.append(section)
    return "\n\n".join(parts)


def render_version(entry):
    """Render the body of a version entry (notes + change sections)."""
    parts = []
    notes = (entry.get("notes") or "").strip()
    if notes:
        parts.append(notes)
    changes = render_changes(entry.get("changes"))
    if changes:
        parts.append(changes)
    return "\n\n".join(parts)


def render_changelog(data):
    lines = [HEADER.rstrip("\n")]

    versions = data.get("versions") or []
    released = [entry for entry in versions if not entry.get("unreleased")]

    for entry in versions:
        if entry.get("unreleased"):
            lines.append("## [Unreleased]")
        else:
            date = entry["date"]
            if isinstance(date, (datetime.date, datetime.datetime)):
                date = date.isoformat()[:10]
            lines.append(f"## [{entry['version']}] - {date}")
        body = render_version(entry)
        if body:
            lines.append(body)

    output = "\n\n".join(lines)

    if released:
        latest = released[0]["version"]
        links = [f"[unreleased]: {REPOSITORY}/compare/v{latest}...HEAD"]
        if len(released) > 1:
            previous = released[1]["version"]
            links.append(
                f"[{latest}]: {REPOSITORY}/compare/v{previous}...v{latest}"
            )
        output += "\n\n" + "\n".join(links)

    return output + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--changelog", default="changelog.yaml")
    parser.add_argument("--md", default="changelog.md")
    parser.add_argument("--notes", default="release_notes.md")
    parser.add_argument("--print-version", action="store_true")
    args = parser.parse_args()

    with open(args.changelog) as f:
        data = yaml.safe_load(f)

    versions = data.get("versions") or []
    released = [entry for entry in versions if not entry.get("unreleased")]
    if not released:
        sys.exit("No released versions found in changelog.yaml")
    latest = released[0]

    with open(args.md, "w") as f:
        f.write(render_changelog(data))

    with open(args.notes, "w") as f:
        f.write(render_version(latest) + "\n")

    if args.print_version:
        print(latest["version"])


if __name__ == "__main__":
    main()
