"""Generate a playable, validator-clean HOI4 mod skeleton.

Usage:
    python tools/new_mod.py "My Cool Mod" [--dir <parent>] [--version 0.1.0]

Creates `<parent>/my_cool_mod/` plus the `.mod` descriptor next to it:
descriptor pair, folder tree, BOM'd localisation, an event file with its
add_namespace declared. The result passes tools/validate.py out of the box.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

EVENT_TEMPLATE = """add_namespace = {name}

# {name}.1 — sample event; delete or adapt freely
country_event = {{
\tid = {name}.1
\ttitle = {name}.1.t
\tdesc = {name}.1.d
\tpicture = GFX_report_event_generic_sign_treaty1

\tis_triggered_only = yes

\toption = {{
\t\tname = {name}.1.a
\t}}
}}
"""

LOC_TEMPLATE = """l_english:
 {name}.1.t:0 "{title} Event"
 {name}.1.d:0 "A brand-new event from the {title} mod."
 {name}.1.a:0 "Understood"
"""

DESCRIPTOR_TEMPLATE = """version="{version}"
tags={{
\t"Events"
}}
name="{title}"
supported_version="1.19.*"
path="mod/{name}"
"""

INNER_DESCRIPTOR_TEMPLATE = """version="{version}"
tags={{
\t"Events"
}}
name="{title}"
supported_version="1.19.*"
"""


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    if not slug or slug[0].isdigit():
        slug = f"mod_{slug}"
    return slug


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a HOI4 mod skeleton")
    parser.add_argument("title", help='mod title, e.g. "My Cool Mod"')
    parser.add_argument("--dir", type=Path, default=Path("."), help="parent directory")
    parser.add_argument("--version", default="0.1.0")
    args = parser.parse_args(argv)

    name = _slugify(args.title)
    mod_dir = args.dir / name
    if mod_dir.exists():
        print(f"error: {mod_dir} already exists — refusing to overwrite", file=sys.stderr)
        return 2

    (mod_dir / "events").mkdir(parents=True)
    for d in ["common/national_focus", "common/decisions/categories",
              "localisation/english", "history/countries", "interface", "gfx"]:
        (mod_dir / d).mkdir(parents=True, exist_ok=True)

    (mod_dir / "descriptor.mod").write_text(
        INNER_DESCRIPTOR_TEMPLATE.format(version=args.version, title=args.title),
        encoding="utf-8",
    )
    (args.dir / f"{name}.mod").write_text(
        DESCRIPTOR_TEMPLATE.format(version=args.version, title=args.title, name=name),
        encoding="utf-8",
    )
    (mod_dir / "events" / f"{name}_events.txt").write_text(
        EVENT_TEMPLATE.format(name=name), encoding="utf-8"
    )
    loc = mod_dir / "localisation" / "english" / f"{name}_l_english.yml"
    loc.write_bytes(b"\xef\xbb\xbf" + LOC_TEMPLATE.format(name=name, title=args.title).encode("utf-8"))

    print(f"created: {mod_dir}")
    print(f"descriptor: {args.dir / (name + '.mod')}")
    print("next: enable it in the launcher, then run scripts/validate.py on it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
