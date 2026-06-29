#!/usr/bin/env python3
import argparse
import unicodedata
import re
import subprocess
import os
from pathlib import Path

# Page size: U.S. Letter at 300 dpi (unused here, kept for consistency)
PAGE_WIDTH = 2550
PAGE_HEIGHT = 3300

CARD_WIDTH = 770
CARD_HEIGHT = 1074

GREY_COLOR = "rgb(210, 210, 210)"
DARKER_GREY_COLOR = "rgb(95, 95, 95)"
BACKGROUND_IMG_SIZE = 90
NAME_FONT_SIZE = 84
CORNER_SIZE = 40


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.strip())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9]+", "_", ascii_text)
    slug = slug.strip("_")
    return slug or "item"


def normalize_event_name(name: str) -> str:
    cleaned = name.replace("(Event)", "").strip()
    return re.sub(r"\s+", " ", cleaned)


def parse_ttdb_sections(ttdb_text: str):
    sections = []
    current = None
    for raw_line in ttdb_text.splitlines():
        line = raw_line.rstrip("\r\n")
        stripped = line.lstrip()
        if stripped.startswith("@LAT"):
            if current:
                sections.append(current)
            header_line = stripped.strip()
            current = {
                "record_id": header_line.split()[0],
                "header": header_line,
                "title": None,
                "lines": [line],
                "relates": [],
            }

            relates_match = re.search(r"relates:([^|]+)", header_line)
            relates_raw = relates_match.group(1).strip() if relates_match else ""
            relates = []
            if relates_raw:
                for token in relates_raw.split(","):
                    token = token.strip()
                    if not token:
                        continue
                    if ">@" in token:
                        edge_type, target = token.split(">@", 1)
                        relates.append((edge_type.strip(), f"@{target.strip()}"))
                    elif ">" in token:
                        edge_type, target = token.split(">", 1)
                        relates.append((edge_type.strip(), target.strip()))
            current["relates"] = relates
            continue

        if current is None:
            continue

        current["lines"].append(line)
        if current["title"] is None:
            if stripped.startswith("## "):
                current["title"] = stripped.replace("## ", "", 1).strip()

    if current:
        sections.append(current)

    return sections


def parse_event_block(section):
    event = {"name": None, "url": None}
    if section.get("title"):
        event_title = section["title"].replace("(Event)", "").strip()
        event["name"] = event_title
    for line in section.get("lines", []):
        if line.strip().startswith("- URL:"):
            event["url"] = line.split(":", 1)[1].strip()
    return event


def parse_robot_block(section):
    robot = {"name": None, "weight": None, "team": None, "image_url": None}
    if section.get("title"):
        robot["name"] = section["title"].strip()
    for line in section.get("lines", []):
        stripped = line.strip()
        if stripped.startswith("- Weight class:"):
            robot["weight"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("- Team:"):
            robot["team"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("- Image:"):
            image_value = stripped.split(":", 1)[1].strip()
            image_match = re.search(r"!\[[^\]]*\]\(([^)]+)\)", image_value)
            if image_match:
                robot["image_url"] = image_match.group(1).strip()
            else:
                robot["image_url"] = image_value
    return robot


def extract_event_robot_ids(section) -> list[str]:
    robot_ids = []
    for line in section.get("lines", []):
        match = re.search(r"-\s+(@LAT\S+)", line)
        if match:
            robot_ids.append(match.group(1).strip())
    return robot_ids


def load_event_from_ttdb(ttdb_path: Path, event_name: str):
    ttdb_text = ttdb_path.read_text(encoding="utf-8")
    sections = parse_ttdb_sections(ttdb_text)
    event_section = None
    target_name = normalize_event_name(event_name).lower()
    for section in sections:
        title = section.get("title")
        if not title:
            continue
        normalized = normalize_event_name(title)
        if normalized.lower() == target_name:
            event_section = section
            break
    if not event_section:
        raise ValueError(f"Event not found in TTDB: {event_name}")

    event = parse_event_block(event_section)
    event_id = event_section["record_id"]

    record_map = {section["record_id"]: section for section in sections}
    robots = []
    for section in sections:
        if section["record_id"] == event_id:
            continue
        relates = section.get("relates", [])
        if not any(edge == "competes_in" and target == event_id for edge, target in relates):
            continue
        robot = parse_robot_block(section)
        robot["record_id"] = section["record_id"]
        if all([robot["name"], robot["weight"], robot["team"]]):
            robots.append(robot)

    if not robots:
        fallback_ids = [
            target
            for edge, target in event_section.get("relates", [])
            if edge in {"has_bot", "has_robot"}
        ]
        if not fallback_ids:
            fallback_ids = extract_event_robot_ids(event_section)
        for record_id in fallback_ids:
            section = record_map.get(record_id)
            if not section:
                continue
            robot = parse_robot_block(section)
            robot["record_id"] = section["record_id"]
            if all([robot["name"], robot["weight"], robot["team"]]):
                robots.append(robot)

    if not robots:
        raise ValueError(
            f"No robots linked to event {event_name} via competes_in edges or event has_bot links."
        )

    event_name_final = event.get("name") or event_name
    return event, event_section["record_id"], robots


def name_band(name: str) -> str:
    name_font_size = NAME_FONT_SIZE if len(name) <= 13 else int(NAME_FONT_SIZE * 0.6)
    name_font_y = 116 if len(name) <= 13 else 104

    return f"""
        <rect x="40" y="40" width="{CARD_WIDTH - 80}" height="100" fill="{DARKER_GREY_COLOR}" rx="{CORNER_SIZE}" ry="{CORNER_SIZE}" />

        <text x="{CARD_WIDTH / 2}" y="{name_font_y}" font-size="{name_font_size}" fill="black" text-anchor="middle" font-family="Roboto">{name}</text>
        <text x="{(CARD_WIDTH / 2) + 2}" y="{name_font_y + 2}" font-size="{name_font_size}" fill="white" text-anchor="middle" font-family="Roboto">{name}</text>
    """


def create_card_front_svg(robot, event_name: str) -> str:
    name = robot["name"]
    weight = robot["weight"]
    team = robot["team"]
    image_url = robot.get("image_url") or ""

    return f"""
    <svg width="{CARD_WIDTH}" height="{CARD_HEIGHT}" xmlns="http://www.w3.org/2000/svg">
        <style>
            @font-face {{
                font-family: 'Roboto';
                font-style: normal;
                font-weight: 400;
                src: url('https://fonts.gstatic.com/s/roboto/v29/KFOmCnqEu92Fr1Mu4mxP.ttf') format('truetype');
            }}
            @font-face {{
                font-family: 'Roboto';
                font-style: normal;
                font-weight: 700;
                src: url('https://fonts.gstatic.com/s/roboto/v29/KFOlCnqEu92Fr1MmWUlfBBc9.ttf') format('truetype');
            }}
            text {{
                font-family: 'Roboto', sans-serif;
            }}
        </style>
        <defs>
            <pattern id="imagePattern" patternUnits="userSpaceOnUse" width="{BACKGROUND_IMG_SIZE}" height="{BACKGROUND_IMG_SIZE}">
                <image href="https://ircl-io.github.io/images/IRCL_logo_Transparent2.png" x="0" y="0" width="{BACKGROUND_IMG_SIZE}" height="{BACKGROUND_IMG_SIZE}" />
            </pattern>
        </defs>
        <rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" fill="{GREY_COLOR}" stroke="black" rx="45" ry="45"/>
        <rect x="0" y="0" width="{CARD_WIDTH}" height="{CARD_HEIGHT}" fill="url(#imagePattern)" />
        <image href="{image_url}" x="1" y="80" width="{CARD_WIDTH - 2}" height="{CARD_WIDTH - 2}"/>

        {name_band(name)}

        <rect x="40" y="{CARD_HEIGHT - 120}" width="{CARD_WIDTH - 80}" height="80" fill="{DARKER_GREY_COLOR}" rx="{CORNER_SIZE}" ry="{CORNER_SIZE}" />
        <rect x="40" y="{CARD_HEIGHT - 254}" width="{CARD_WIDTH - 80}" height="120" fill="{DARKER_GREY_COLOR}" rx="{CORNER_SIZE}" ry="{CORNER_SIZE}" />

        <text x="{CARD_WIDTH / 2}" y="{CARD_HEIGHT - 205}" font-size="36" fill="white" text-anchor="middle" font-family="Roboto">{weight}</text>
        <text x="{CARD_WIDTH / 2}" y="{CARD_HEIGHT - 165}" font-size="36" fill="white" text-anchor="middle" font-family="Roboto">by {team}</text>
        <text x="{CARD_WIDTH / 2}" y="{CARD_HEIGHT - 70}" font-size="36" fill="white" text-anchor="middle" font-family="Roboto">{event_name}</text>

        <rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" stroke="black" stroke-width="10" fill="none" rx="45" ry="45" />
    </svg>
    """


def create_card_back_svg() -> str:
    logo_image_url = "https://ircl-io.github.io/images/IRCL/IRCL_logo_Transparent-90.png"

    return f"""
    <svg width="{CARD_WIDTH}" height="{CARD_HEIGHT}" xmlns="http://www.w3.org/2000/svg">
        <style>
            @font-face {{
                font-family: 'Roboto';
                font-style: normal;
                font-weight: 400;
                src: url('https://fonts.gstatic.com/s/roboto/v29/KFOmCnqEu92Fr1Mu4mxP.ttf') format('truetype');
            }}
            @font-face {{
                font-family: 'Roboto';
                font-style: normal;
                font-weight: 700;
                src: url('https://fonts.gstatic.com/s/roboto/v29/KFOlCnqEu92Fr1MmWUlfBBc9.ttf') format('truetype');
            }}
            text {{
                font-family: 'Roboto', sans-serif;
            }}
        </style>
        <rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" fill="{GREY_COLOR}" stroke="black" rx="45" ry="45"/>
        <image href="{logo_image_url}" x="1" y="1" width="{CARD_WIDTH -2}" height="{CARD_HEIGHT-2}" stroke="black"  />
        <text x="60" y="60" font-size="64" font-weight="bold" fill="white" text-anchor="middle" font-family="Roboto" transform="rotate(90, 60, 120)">
            ircl.io
        </text>
        <rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" stroke="black" stroke-width="10" fill="none" rx="45" ry="45" />
    </svg>
    """


def svg_to_png(svg_file: Path, png_file: Path) -> None:
    subprocess.run(
        ["inkscape", str(svg_file), "--export-filename", str(png_file)],
        check=True,
    )


def update_record_lines(lines: list[str], record_id: str, field: str, value: str) -> list[str]:
    updated = []
    in_record = False
    found = False
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("@LAT"):
            if in_record:
                in_record = False
            in_record = stripped.startswith(record_id)
        if in_record and stripped.startswith(f"- {field}:"):
            updated.append(f"- {field}: {value}")
            found = True
            continue
        updated.append(line)
    if not found:
        # Insert after Image field if present, otherwise after the title line.
        new_lines = []
        in_record = False
        inserted = False
        for line in updated:
            stripped = line.lstrip()
            if stripped.startswith("@LAT"):
                if in_record:
                    in_record = False
                in_record = stripped.startswith(record_id)
            new_lines.append(line)
            if in_record and not inserted:
                if stripped.startswith("- Image:"):
                    new_lines.append(f"- {field}: {value}")
                    inserted = True
                elif stripped.startswith("## "):
                    # Insert after the title line if Image is not present in this record.
                    new_lines.append(f"- {field}: {value}")
                    inserted = True
        updated = new_lines
    return updated


def relative_to_base(path: Path, base_dir: Path) -> str:
    try:
        rel = path.resolve().relative_to(base_dir.resolve())
        return rel.as_posix()
    except ValueError:
        return os.path.relpath(path.as_posix(), base_dir.as_posix()).replace("\\", "/")


def format_markdown_image(alt_text: str, rel_path: str) -> str:
    return f"![{alt_text}]({rel_path})"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate single card PNGs from TTDB.")
    parser.add_argument(
        "--ttdb",
        "-t",
        default="cards/IRCL_TTDB.md",
        help="Path to the IRCL TTDB markdown file.",
    )
    parser.add_argument(
        "--event-name",
        required=True,
        help="Event name to render (must match an Event title in the TTDB).",
    )
    parser.add_argument(
        "--robot-name",
        help="Optional robot name to render a single card (matches a Robot title in the TTDB).",
    )
    parser.add_argument(
        "--team-name",
        help="Optional team name to disambiguate robots with the same name.",
    )
    parser.add_argument(
        "--cards-dir",
        default=None,
        help="Directory for generated card PNGs.",
    )
    parser.add_argument(
        "--keep-svgs",
        action="store_true",
        help="Keep intermediate SVGs.",
    )

    args = parser.parse_args()
    ttdb_path = Path(args.ttdb)
    if not ttdb_path.exists():
        raise FileNotFoundError(f"TTDB input not found: {ttdb_path}")

    event, event_id, robots = load_event_from_ttdb(ttdb_path, args.event_name)
    event_name = event.get("name") or args.event_name
    event_slug = slugify(event_name)

    base_dir = Path(__file__).resolve().parent
    cards_dir = Path(args.cards_dir) if args.cards_dir else base_dir / "cards" / event_slug
    cards_dir.mkdir(parents=True, exist_ok=True)

    ttdb_lines = ttdb_path.read_text(encoding="utf-8").splitlines()
    ttdb_dir = ttdb_path.parent.resolve()

    if args.robot_name:
        matches = [robot for robot in robots if robot["name"].lower() == args.robot_name.lower()]
        if args.team_name:
            matches = [
                robot for robot in matches if (robot.get("team") or "").lower() == args.team_name.lower()
            ]
        if not matches:
            team_hint = f" (team: {args.team_name})" if args.team_name else ""
            raise ValueError(f"Robot not found for event {event_name}: {args.robot_name}{team_hint}")
        if len(matches) > 1 and not args.team_name:
            teams = ", ".join(sorted({robot.get("team") or "" for robot in matches if robot.get("team")}))
            raise ValueError(
                f"Multiple robots named '{args.robot_name}' found for event {event_name}. "
                f"Use --team-name to disambiguate. Teams: {teams}"
            )
        robots = matches

    for robot in robots:
        robot_slug = slugify(robot["name"])
        svg_path = cards_dir / f"{robot_slug}.svg"
        png_path = cards_dir / f"{robot_slug}.png"

        svg_path.write_text(create_card_front_svg(robot, event_name), encoding="utf-8")
        svg_to_png(svg_path, png_path)

        rel_path = relative_to_base(png_path, ttdb_dir)
        image_value = format_markdown_image(robot["name"], rel_path)
        ttdb_lines = update_record_lines(ttdb_lines, robot["record_id"], "Card image", image_value)

        if not args.keep_svgs:
            svg_path.unlink(missing_ok=True)

    back_svg = cards_dir / f"{event_slug}_back.svg"
    back_png = cards_dir / f"{event_slug}_back.png"
    back_svg.write_text(create_card_back_svg(), encoding="utf-8")
    svg_to_png(back_svg, back_png)
    if not args.keep_svgs:
        back_svg.unlink(missing_ok=True)

    back_rel_path = relative_to_base(back_png, ttdb_dir)
    back_alt = f"{event_name} Back"
    back_value = format_markdown_image(back_alt, back_rel_path)
    ttdb_lines = update_record_lines(ttdb_lines, event_id, "Back card image", back_value)

    ttdb_path.write_text("\n".join(ttdb_lines) + "\n", encoding="utf-8")
    print(f"Generated {len(robots)} cards + back card in {cards_dir}")


if __name__ == "__main__":
    main()
