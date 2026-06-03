#!/usr/bin/env python3
"""
Audit and clean appfilter.xml against actual icon assets and Lawnicons.

Pass 1: Remove entries pointing to drawables with no icon PNG.
Pass 2: Add new activity mappings from Lawnicons for packages we have icons for.
Pass 3: Deduplicate component entries.

Usage:
    python3 scripts/audit_appfilter.py [--lawnicons-url URL] [--dry-run]

Reads:  app/src/main/res/xml/appfilter.xml, icons/appstract-dark/
Writes: app/src/main/res/xml/appfilter.xml (cleaned)
        app/src/main/res/xml/appfilter_wishlist.xml (removed entries)
"""

import argparse
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
APPFILTER = REPO_ROOT / "app" / "src" / "main" / "res" / "xml" / "appfilter.xml"
ICONS_DIR = REPO_ROOT / "icons" / "appstract-dark"
WISHLIST = APPFILTER.parent / "appfilter_wishlist.xml"
LAWNICONS_URL = (
    "https://raw.githubusercontent.com/LawnchairLauncher/lawnicons"
    "/develop/app/assets/appfilter.xml"
)

COMPONENT_RE = re.compile(
    r'component="ComponentInfo\{([^/]+)/([^}]+)\}"'
)
DRAWABLE_RE = re.compile(r'drawable="([^"]+)"')


def load_actual_icons():
    return {p.stem for p in ICONS_DIR.glob("*.png")}


def parse_entry(line):
    """Extract (package, activity, drawable) from an appfilter line, or None."""
    cm = COMPONENT_RE.search(line)
    dm = DRAWABLE_RE.search(line)
    if cm and dm:
        return cm.group(1), cm.group(2), dm.group(1)
    return None


def fetch_lawnicons(url):
    print(f"Fetching Lawnicons appfilter from {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "appstract-audit/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode("utf-8")
    print(f"  {len(data)} bytes, {data.count(chr(10))} lines")
    return data.splitlines()


def build_lawnicons_index(lines):
    """package -> set of (activity,)"""
    index = defaultdict(set)
    for line in lines:
        parsed = parse_entry(line)
        if parsed:
            pkg, act, _ = parsed
            index[pkg].add(act)
    return index


def run(dry_run=False, lawnicons_url=LAWNICONS_URL):
    icons = load_actual_icons()
    print(f"Actual icon PNGs: {len(icons)}")

    lines = APPFILTER.read_text().splitlines(keepends=True)
    if not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    # --- Pass 1 & 3: filter broken refs and dedup ---
    kept = []
    wishlist = []
    seen_components = set()
    pkg_to_drawable = defaultdict(str)

    # First pass: figure out which drawable each package maps to
    # (only for packages with real icons)
    for line in lines:
        parsed = parse_entry(line)
        if parsed:
            pkg, act, drw = parsed
            if drw in icons:
                pkg_to_drawable[pkg] = drw

    stats = {"broken": 0, "duped": 0, "kept": 0, "added": 0}

    for line in lines:
        parsed = parse_entry(line)
        if parsed is None:
            # Comment, header, scale, blank line — keep as-is
            kept.append(line)
            continue

        pkg, act, drw = parsed
        component_key = f"{pkg}/{act}"

        if drw not in icons:
            wishlist.append(line)
            stats["broken"] += 1
            continue

        if component_key in seen_components:
            stats["duped"] += 1
            continue

        seen_components.add(component_key)
        kept.append(line)
        stats["kept"] += 1

    # --- Pass 2: add new activities from Lawnicons ---
    lawnicons_lines = fetch_lawnicons(lawnicons_url)
    lawnicons_index = build_lawnicons_index(lawnicons_lines)

    new_entries = []
    for pkg, drw in sorted(pkg_to_drawable.items()):
        if pkg not in lawnicons_index:
            continue
        for act in sorted(lawnicons_index[pkg]):
            component_key = f"{pkg}/{act}"
            if component_key not in seen_components:
                entry = (
                    f'\t<item component="ComponentInfo{{{pkg}/{act}}}"'
                    f' drawable="{drw}"/>\n'
                )
                new_entries.append(entry)
                seen_components.add(component_key)
                stats["added"] += 1

    # Insert new entries before closing </resources>
    closing_idx = None
    for i in range(len(kept) - 1, -1, -1):
        if "</resources>" in kept[i]:
            closing_idx = i
            break

    if closing_idx is not None and new_entries:
        block = ["\n\t<!-- New activity mappings from Lawnicons -->\n"] + new_entries
        kept = kept[:closing_idx] + block + ["\n"] + kept[closing_idx:]

    # --- Report ---
    print(f"\nResults:")
    print(f"  Kept:    {stats['kept']} existing entries")
    print(f"  Removed: {stats['broken']} broken (drawable missing)")
    print(f"  Removed: {stats['duped']} duplicates")
    print(f"  Added:   {stats['added']} new from Lawnicons")
    print(f"  Wishlist: {len(wishlist)} removed this run (merged into existing backlog)")

    if dry_run:
        print("\n(dry run — no files written)")
        return

    APPFILTER.write_text("".join(kept))
    print(f"\nWrote {APPFILTER}")

    # Merge this run's removals into the existing wishlist instead of
    # overwriting it, so the accumulated backlog survives runs that remove
    # nothing. Drop entries whose icon now exists (the wish was fulfilled),
    # and dedup by component.
    merged = []
    seen_wishes = set()
    existing = WISHLIST.read_text().splitlines(keepends=True) if WISHLIST.exists() else []
    for line in existing + wishlist:
        parsed = parse_entry(line)
        if parsed is None:
            continue
        pkg, act, drw = parsed
        if drw in icons:
            continue  # icon now exists — no longer a wish
        key = f"{pkg}/{act}"
        if key in seen_wishes:
            continue
        seen_wishes.add(key)
        merged.append(line)

    wishlist_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<!-- Entries removed during audit: drawable PNGs don't exist yet.\n"
        "     Design these icons to re-enable the mappings. -->\n"
        "<resources>\n"
    )
    wishlist_content += "".join(merged)
    wishlist_content += "</resources>\n"
    WISHLIST.write_text(wishlist_content)
    print(f"Wrote {WISHLIST} ({len(merged)} entries, {len(wishlist)} new this run)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--lawnicons-url", default=LAWNICONS_URL)
    args = parser.parse_args()
    run(dry_run=args.dry_run, lawnicons_url=args.lawnicons_url)
