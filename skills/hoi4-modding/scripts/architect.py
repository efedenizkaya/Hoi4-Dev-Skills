"""Mod Architect core: project memory + consistency checker.

Tracks a HOI4 mod's scenario in one JSON file — countries, characters,
chronological timeline entries, content registry (focuses/events/
decisions/ideas) and country relations — then audits it for
contradictions: timeline entries before a participant's birth, one-way
alliances, undefined participants and content dependencies.

The project file is the architect's own data (JSON); mod game files are
never modified by this tool.

Usage:
    python tools/architect.py init --name "My Mod" --project <file.json>
    python tools/architect.py add-country TAG --project <f> [--name N]
                                     [--ideology I] [--government G]
    python tools/architect.py add-character TOKEN --project <f>
                                     [--name N] [--country TAG]
                                     [--born DATE] [--died DATE]
                                     [--roles a,b]
    python tools/architect.py add-timeline --project <f> --date DATE
                                     --title T [--participants A,B]
    python tools/architect.py add-content KIND ID --project <f>
                                     [--summary S] [--depends A,B]
    python tools/architect.py add-relation TAG --project <f>
                                     [--allies A,B] [--enemies A,B]
                                     [--wars A,B]
    python tools/architect.py check --project <f> [--json] [--out R.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCHEMA_VERSION = 1


def _load(project: Path) -> dict:
    if not project.is_file():
        print(f"error: project file {project} not found — run init first",
              file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(project.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: {project} is not valid JSON ({exc}) — restore it or "
              "delete it and re-run init", file=sys.stderr)
        sys.exit(2)


def _save(project: Path, data: dict) -> None:
    project.write_text(json.dumps(data, indent=1, ensure_ascii=False),
                       encoding="utf-8")


def _date(s: str) -> tuple[int, int, int]:
    try:
        y, m, d = (int(x) for x in s.split("."))
    except ValueError:
        raise ValueError(f"invalid date '{s}' — expected YYYY.M.D, e.g. 1936.1.1")
    if not (1 <= m <= 12 and 1 <= d <= 31):
        raise ValueError(f"invalid date '{s}' — month/day out of range")
    return y, m, d


def _validated_date(s: str, field: str) -> bool:
    """Validate a user-supplied date; on failure print a friendly error
    and return False (caller exits with 2)."""
    try:
        _date(s)
    except ValueError as exc:
        print(f"error: --{field}: {exc}", file=sys.stderr)
        return False
    return True


def cmd_init(args) -> int:
    project = Path(args.project)
    if project.exists():
        print(f"error: {project} already exists", file=sys.stderr)
        return 2
    if not _validated_date(args.timeline_start, "timeline-start"):
        return 2
    data = {
        "schema_version": SCHEMA_VERSION,
        "name": args.name,
        "timeline_start": args.timeline_start or "1936.1.1",
        "scenario_notes": [],
        "countries": [],
        "characters": [],
        "timeline": [],
        "content": [],
        "relations": [],
    }
    _save(project, data)
    print(f"project created: {project}")
    return 0


def cmd_add_country(args) -> int:
    project = Path(args.project)
    data = _load(project)
    if any(c["tag"] == args.tag for c in data["countries"]):
        print(f"error: country {args.tag} already defined", file=sys.stderr)
        return 2
    data["countries"].append({
        "tag": args.tag,
        "name": args.name or args.tag,
        "ideology": args.ideology or "",
        "government": args.government or "",
        "relations": {"allies": [], "enemies": [], "wars": []},
        "notes": [],
    })
    _save(project, data)
    print(f"country added: {args.tag}")
    return 0


def cmd_add_character(args) -> int:
    project = Path(args.project)
    data = _load(project)
    if any(c["token"] == args.token for c in data["characters"]):
        print(f"error: character {args.token} already defined", file=sys.stderr)
        return 2
    for field in ("born", "died"):
        value = getattr(args, field)
        if value and not _validated_date(value, field):
            return 2
    data["characters"].append({
        "token": args.token,
        "name": args.name or args.token,
        "country": args.country or "",
        "born": args.born or "",
        "died": args.died or "",
        "roles": [r.strip() for r in (args.roles or "").split(",") if r.strip()],
    })
    _save(project, data)
    print(f"character added: {args.token}")
    return 0


def cmd_add_timeline(args) -> int:
    project = Path(args.project)
    data = _load(project)
    if not _validated_date(args.date, "date"):
        return 2
    data["timeline"].append({
        "date": args.date,
        "title": args.title,
        "participants": [p.strip() for p in
                         (args.participants or "").split(",") if p.strip()],
        "notes": args.notes or "",
    })
    _save(project, data)
    print(f"timeline entry added: {args.date} {args.title}")
    return 0


def cmd_add_content(args) -> int:
    project = Path(args.project)
    data = _load(project)
    if any(c["kind"] == args.kind and c["id"] == args.id
           for c in data["content"]):
        print(f"error: content {args.kind}/{args.id} already registered",
              file=sys.stderr)
        return 2
    data["content"].append({
        "kind": args.kind,
        "id": args.id,
        "summary": args.summary or "",
        "depends_on": [d.strip() for d in
                       (args.depends or "").split(",") if d.strip()],
        "files": [],
    })
    _save(project, data)
    print(f"content added: {args.kind}/{args.id}")
    return 0


def cmd_add_relation(args) -> int:
    project = Path(args.project)
    data = _load(project)
    country = next((c for c in data["countries"] if c["tag"] == args.tag), None)
    if country is None:
        print(f"error: country {args.tag} is not defined in the project — "
              "add it first", file=sys.stderr)
        return 2
    rel = country["relations"]
    for key in ("allies", "enemies", "wars"):
        value = getattr(args, key)
        if value:
            rel[key] = [t.strip() for t in value.split(",") if t.strip()]
    _save(project, data)
    print(f"relations updated for {args.tag}")
    return 0


def _check(data: dict) -> list[dict]:
    findings: list[dict] = []

    def finding(rule: str, message: str, **kw) -> None:
        findings.append({"rule": rule, "message": message, **kw})

    tags = {c["tag"] for c in data["countries"]}
    tokens = {c["token"] for c in data["characters"]}

    for entry in data["timeline"]:
        for p in entry["participants"]:
            if p not in tags and p not in tokens:
                finding("undefined-participant",
                        f"{entry['title']}: participant '{p}' is not a "
                        "defined country or character",
                        date=entry["date"])
            char = next((c for c in data["characters"] if c["token"] == p),
                        None)
            if char and char.get("born"):
                if _date(entry["date"]) < _date(char["born"]):
                    finding("event-before-birth",
                            f"{entry['title']}: participant '{p}' is born "
                            f"{char['born']}, after this entry's date "
                            f"{entry['date']}",
                            date=entry["date"])

    for c in data["countries"]:
        rel = c["relations"]
        for key in ("allies", "enemies", "wars"):
            for other in rel[key]:
                if other not in tags:
                    finding("undefined-participant",
                            f"{c['tag']} relation '{key}' references "
                            f"undefined country '{other}'")
        for other in rel["allies"]:
            other_c = next((x for x in data["countries"] if x["tag"] == other),
                           None)
            if other_c and c["tag"] not in other_c["relations"]["allies"]:
                finding("one-way-relation",
                        f"{c['tag']} lists {other} as ally, but {other} "
                        "does not list it back")

    content_ids = {f"{c['kind']}/{c['id']}" for c in data["content"]}
    plain_ids = {c["id"] for c in data["content"]}
    for c in data["content"]:
        for dep in c["depends_on"]:
            if dep not in plain_ids and f"{c['kind']}/{dep}" not in content_ids:
                finding("undefined-dependency",
                        f"{c['kind']}/{c['id']} depends on '{dep}' which is "
                        "not registered")
    return findings


def cmd_check(args) -> int:
    project = Path(args.project)
    data = _load(project)
    try:
        findings = _check(data)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.out:
        Path(args.out).write_text(json.dumps(
            {"project": str(project), "findings": findings}, indent=1),
            encoding="utf-8")
    if args.json:
        print(json.dumps({"findings": findings}, indent=1))
    else:
        for f in findings:
            print(f"[{f['rule']}] {f['message']}")
        print(f"\n{len(findings)} finding(s)")
    return 1 if findings else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mod Architect core")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--name", required=True)
    p_init.add_argument("--project", required=True)
    p_init.add_argument("--timeline-start", default="1936.1.1")

    p_country = sub.add_parser("add-country")
    p_country.add_argument("tag")
    p_country.add_argument("--project", required=True)
    p_country.add_argument("--name")
    p_country.add_argument("--ideology")
    p_country.add_argument("--government")

    p_char = sub.add_parser("add-character")
    p_char.add_argument("token")
    p_char.add_argument("--project", required=True)
    p_char.add_argument("--name")
    p_char.add_argument("--country")
    p_char.add_argument("--born")
    p_char.add_argument("--died")
    p_char.add_argument("--roles")

    p_time = sub.add_parser("add-timeline")
    p_time.add_argument("--project", required=True)
    p_time.add_argument("--date", required=True)
    p_time.add_argument("--title", required=True)
    p_time.add_argument("--participants", default="")
    p_time.add_argument("--notes")

    p_content = sub.add_parser("add-content")
    p_content.add_argument("kind")
    p_content.add_argument("id")
    p_content.add_argument("--project", required=True)
    p_content.add_argument("--summary")
    p_content.add_argument("--depends", default="")

    p_rel = sub.add_parser("add-relation")
    p_rel.add_argument("tag")
    p_rel.add_argument("--project", required=True)
    p_rel.add_argument("--allies")
    p_rel.add_argument("--enemies")
    p_rel.add_argument("--wars")

    p_check = sub.add_parser("check")
    p_check.add_argument("--project", required=True)
    p_check.add_argument("--json", action="store_true")
    p_check.add_argument("--out", type=Path, default=None)

    args = parser.parse_args(argv)
    handlers = {
        "init": cmd_init, "add-country": cmd_add_country,
        "add-character": cmd_add_character, "add-timeline": cmd_add_timeline,
        "add-content": cmd_add_content, "add-relation": cmd_add_relation,
        "check": cmd_check,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
