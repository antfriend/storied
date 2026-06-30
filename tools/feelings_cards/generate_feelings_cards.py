#!/usr/bin/env python3
"""Generate print-and-play Feeling cards from a Feelings TTDB.

Reuses the Robot Combat Trading Cards print geometry *exactly* (US Letter @ 300 DPI,
770x1074 cards, 3x3 grid, 1/8" gutters) but renders an affective card face built from
the TTDB record: name, the umwelt eyeball compass showing the card's position on the
affective field, tagline, body, stats (valence / category / object / intensity), and
the typed edges that drive the game's combo system.

Pipeline:  TTDB -> per-card SVG -> PNG (Inkscape, cairosvg fallback)
           -> 3x3 page PNGs + tiled back page -> duplex PDF (Pillow).

Usage:
    python generate_feelings_cards.py --ttdb ../../reference/feelings_ttdb.md
"""
from __future__ import annotations

import argparse
import math
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

# --- Print geometry: identical to Robot-Combat-Trading-Cards (do not change) -------
PAGE_WIDTH = 2550          # US Letter @ 300 dpi
PAGE_HEIGHT = 3300
CARD_WIDTH = 770
CARD_HEIGHT = 1074
CARD_SPACING = 38          # 1/8"
LEFT_SIDE_OF_PAGE = 82
TOP_OF_PAGE = 3
PAGE_CORNER = 40
CARD_CORNER = 45

# --- Palette ----------------------------------------------------------------------
CREAM = "rgb(245, 243, 238)"
INK = "rgb(40, 40, 46)"
DARK_BAND = "rgb(52, 52, 60)"
DARK_BAND_2 = "rgb(72, 72, 82)"
POS_COLOR = "rgb(34, 139, 96)"     # positive valence  (north / NE-NW)
NEG_COLOR = "rgb(168, 46, 58)"     # negative valence  (south / SE-SW)
EYE_RED = "rgb(196, 60, 60)"       # the umwelt iris (matches eyeball.js --eyeball-red)

# Per-type theming for the non-feeling Pulse card types (manifest color coding).
GOLD = "rgb(176, 137, 43)"         # Story Track border / header
GOLD_DK = "rgb(140, 104, 28)"
BLUE = "rgb(38, 66, 120)"          # Character (deep blue)
BLUE_DK = "rgb(26, 46, 86)"
SLATE = "rgb(86, 92, 102)"         # Part (slate gray)
SLATE_DK = "rgb(60, 64, 72)"

CATEGORY_TINT = {
    "Feeling": "rgb(70, 120, 170)",
    "Emotion": "rgb(196, 118, 40)",
    "Disposition": "rgb(120, 92, 168)",
    "Intent": "rgb(40, 150, 138)",
}

# --- Decks --------------------------------------------------------------------------
# A deck selects (and orders) which TTDB cards print. `cards: None` = the whole field.
# Pulse pulls only what games/Pulse.md uses: the 6 Hero's-Arc beats, the near-neighbor
# hand cards, and the 5 character dispositions — in play order.
DECKS: dict[str, dict] = {
    "feelings": {"name": "Feelings", "cards": None},
    "pulse": {
        "name": "Pulse",
        # Final "boxed game" lands here; instructions PDF is rendered from this rules file.
        "box": "../../games/pulse",
        "instructions": "../../games/pulse/Pulse.md",
        "accent": (34, 139, 96),
        # The full 57-card print-and-play set (5 card types with copies) is built by
        # build_pulse_jobs() from the PULSE_* tables below — see games/pulse/Pulse-Print-and-Play.md.
        "composition": "pulse",
    },
    "metamorphosis": {
        "name": "Metamorphosis",
        "box": "../../games/metamorphosis",
        "instructions": "../../games/Metamorphosis.md",
        "accent": (120, 92, 168),  # disposition purple — all six larva are dispositions
        "cards": [
            # Larva (character) dispositions, in Metamorphosis.md §3.1 order
            "Curiosity",     # The Seeker
            "Suspicion",     # The Warden
            "Compassion",    # The Healer
            "Generosity",    # The Giver
            "Equanimity",    # The Hermit
            "Indifference",  # The Trickster
        ],
    },
}

# Edge types that are part of the affective "combo" system (worth printing).
# umwelt-anchoring edges (feels/emotes/is_*_of) and reverse links are dropped.
EDGE_LABELS = {
    "resonates_with": "resonates with",
    "can_deepen_into": "deepens into",
    "intensifies_into": "intensifies into",
    "can_intensify_into": "intensifies into",
    "can_become": "becomes",
    "opens_toward": "opens toward",
    "enables": "enables",
}


# --- Slug ---------------------------------------------------------------------------
def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.strip())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9]+", "_", ascii_text).strip("_")
    return slug or "item"


def xesc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# --- TTDB parsing -------------------------------------------------------------------
COORD_RE = re.compile(r"@LAT(-?\d+)LON(-?\d+)")


def parse_records(ttdb_text: str) -> list[dict]:
    """Split a TTDB into records keyed by their @LAT..LON.. header line."""
    records: list[dict] = []
    current: dict | None = None
    for raw in ttdb_text.splitlines():
        line = raw.rstrip("\r\n")
        stripped = line.strip()
        if stripped.startswith("@LAT"):
            if current:
                records.append(current)
            m = COORD_RE.search(stripped)
            relates_m = re.search(r"relates:([^|]+)", stripped)
            edges = []
            if relates_m:
                for tok in relates_m.group(1).split(","):
                    tok = tok.strip()
                    if ">@" in tok:
                        etype, target = tok.split(">@", 1)
                        edges.append((etype.strip(), "@" + target.strip()))
            current = {
                "id": stripped.split()[0],
                "lat": int(m.group(1)) if m else 0,
                "lon": int(m.group(2)) if m else 0,
                "edges": edges,
                "title": None,
                "tagline": None,
                "body": [],
                "fields": {},
                "ew": {},
            }
            continue
        if current is None:
            continue

        if stripped.startswith("## "):
            current["title"] = stripped[3:].strip()
            continue
        if current["title"] and current["tagline"] is None and re.fullmatch(r"\*.+\*", stripped):
            current["tagline"] = stripped.strip("*").strip()
            continue
        field_m = re.match(r"-\s*\*?\*?([A-Za-z][A-Za-z \-]*?)\*?\*?:\s*(.+)", stripped)
        if field_m and stripped.startswith("-"):
            key = field_m.group(1).strip()
            val = field_m.group(2).strip().strip("*").strip()
            current["fields"][key] = val
            continue
        ew_m = re.match(r"(conf|rev|sal|touched):\s*(-?\d+)", stripped)
        if ew_m:
            current["ew"][ew_m.group(1)] = int(ew_m.group(2))
            continue
        if stripped in ("[ew]", "[/ew]") or stripped.startswith("#"):
            continue
        if stripped and not stripped.startswith("-") and not stripped.startswith("```"):
            current["body"].append(stripped)

    if current:
        records.append(current)
    return records


def is_card(rec: dict) -> bool:
    """A record is a Feeling card iff it carries a Category field."""
    return rec["fields"].get("Category") in {"Feeling", "Emotion", "Disposition", "Intent"}


def intensity_levels(text: str) -> list[int]:
    return [int(n) for n in re.findall(r"L(\d)", text or "")]


def object_of(rec: dict) -> str:
    obj = rec["fields"].get("Object")
    if obj:
        return obj
    if rec["lon"] > 0:
        return "Other-directed"
    if rec["lon"] < 0:
        return "Self-directed"
    return "Centered"


# --- SVG helpers --------------------------------------------------------------------
def wrap(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def fit_tagline(text: str, width: int = 620, max_font: int = 28, min_font: int = 22,
                max_lines: int = 3) -> tuple[list[str], int]:
    """Largest italic font (down to min_font) whose wrap fits within max_lines."""
    for f in range(max_font, min_font - 1, -1):
        cpl = max(10, int(width / (0.50 * f)))
        lines = wrap(text, cpl)
        if len(lines) <= max_lines:
            return lines, f
    cpl = max(10, int(width / (0.50 * min_font)))
    return wrap(text, cpl)[:max_lines], min_font


def fit_body(text: str, top: int = 632, bottom: int = 838, width: int = 690,
             max_font: int = 25, min_font: int = 17) -> tuple[list[str], int, float]:
    """Largest body font whose full wrap fits the box [top, bottom]; truncate only as a last resort."""
    for f in range(max_font, min_font - 1, -1):
        cpl = max(10, int(width / (0.52 * f)))
        lh = round(f * 1.22, 1)
        max_lines = int((bottom - top) / lh) + 1
        lines = wrap(text, cpl)
        if len(lines) <= max_lines:
            return lines, f, lh
    f = min_font
    cpl = max(10, int(width / (0.52 * f)))
    lh = round(f * 1.22, 1)
    max_lines = int((bottom - top) / lh) + 1
    return wrap(text, cpl)[:max_lines], f, lh


def tspans(lines: list[str], x: float, y: float, line_h: float, **attrs) -> str:
    attr = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    out = [f'<text x="{x}" y="{y}" {attr}>']
    for i, ln in enumerate(lines):
        dy = 0 if i == 0 else line_h
        out.append(f'<tspan x="{x}" dy="{dy}">{xesc(ln)}</tspan>')
    out.append("</text>")
    return "".join(out)


def eyeball_compass(rec: dict, cx: float, cy: float, R: float, valence_color: str) -> str:
    """The umwelt eyeball at origin, looking toward this card's node on the field."""
    scale = R / 48.0  # field extent ~ +/-48 in lat/lon for the affective nodes
    nx = cx + rec["lon"] * scale
    ny = cy - rec["lat"] * scale  # north = up
    # eye looks toward the node
    dx, dy = nx - cx, ny - cy
    dist = math.hypot(dx, dy) or 1.0
    ux, uy = dx / dist, dy / dist
    re_, ri, rp = 30, 13, 6
    off = 11  # iris+pupil shift together toward the node (concentric, like eyeball.js)
    ex, ey = cx + ux * off, cy + uy * off
    levels = intensity_levels(rec["fields"].get("Intensity", ""))
    node_r = 7 + (max(levels) if levels else 1) * 2.0

    return f"""
    <circle cx="{cx}" cy="{cy}" r="{R}" fill="rgb(250,249,246)" stroke="rgb(210,208,202)" stroke-width="2"/>
    <line x1="{cx-R}" y1="{cy}" x2="{cx+R}" y2="{cy}" stroke="rgb(214,212,206)" stroke-width="2"/>
    <line x1="{cx}" y1="{cy-R}" x2="{cx}" y2="{cy+R}" stroke="rgb(214,212,206)" stroke-width="2"/>
    <text x="{cx}" y="{cy-R+26}" font-size="22" fill="{POS_COLOR}" text-anchor="middle" font-family="Arial">N +</text>
    <text x="{cx}" y="{cy+R-10}" font-size="22" fill="{NEG_COLOR}" text-anchor="middle" font-family="Arial">S −</text>
    <text x="{cx+R-22}" y="{cy-6}" font-size="20" fill="rgb(120,118,112)" text-anchor="middle" font-family="Arial">other</text>
    <text x="{cx-R+22}" y="{cy-6}" font-size="20" fill="rgb(120,118,112)" text-anchor="middle" font-family="Arial">self</text>
    <line x1="{cx}" y1="{cy}" x2="{nx}" y2="{ny}" stroke="{valence_color}" stroke-width="4" stroke-dasharray="6 6" opacity="0.8"/>
    <circle cx="{cx}" cy="{cy}" r="{re_}" fill="white" stroke="black" stroke-width="3"/>
    <circle cx="{ex}" cy="{ey}" r="{ri}" fill="{EYE_RED}" stroke="black" stroke-width="1"/>
    <circle cx="{ex}" cy="{ey}" r="{rp}" fill="black"/>
    <circle cx="{cx-9}" cy="{cy-11}" r="4" fill="white" fill-opacity="0.85"/>
    <circle cx="{nx}" cy="{ny}" r="{node_r}" fill="{valence_color}" stroke="white" stroke-width="3"/>
    """


def card_front_svg(rec: dict, coord2name: dict[str, str], db_name: str) -> str:
    name = rec["title"]
    valence = rec["fields"].get("Valence", "")
    category = rec["fields"].get("Category", "")
    intensity = rec["fields"].get("Intensity", "")
    obj = object_of(rec)
    vcolor = POS_COLOR if valence.lower().startswith("pos") else NEG_COLOR
    cat_color = CATEGORY_TINT.get(category, DARK_BAND)

    name_size = 64 if len(name) <= 14 else 50

    # intensity pips
    levels = intensity_levels(intensity)
    lvl = max(levels) if levels else 0
    pips = ""
    for i in range(4):
        fill = "white" if i < lvl else "none"
        pips += (
            f'<circle cx="{612 + i*30}" cy="105" r="9" fill="{fill}" '
            f'stroke="white" stroke-width="2"/>'
        )

    # combo edges
    edge_lines = []
    for etype, target in rec["edges"]:
        if etype in EDGE_LABELS and target in coord2name:
            edge_lines.append(f'{EDGE_LABELS[etype]} → {coord2name[target]}')
    edge_lines = edge_lines[:3]
    edges_block = ""
    if edge_lines:
        edges_block = tspans(
            edge_lines, 60, 988, 30,
            font_size="24", fill="white", font_family="Arial",
        )

    tagline_lines, tag_f = fit_tagline(rec["tagline"] or "")
    tag_lh = round(tag_f * 1.28, 1)
    tag_start = 552 - (len(tagline_lines) - 1) * tag_lh / 2
    body_lines, body_f, body_lh = fit_body(" ".join(rec["body"]))

    return f"""<svg width="{CARD_WIDTH}" height="{CARD_HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <rect x="5" y="5" width="{CARD_WIDTH-10}" height="{CARD_HEIGHT-10}" fill="{CREAM}" rx="{CARD_CORNER}" ry="{CARD_CORNER}"/>

  <!-- header band (valence) -->
  <rect x="30" y="30" width="{CARD_WIDTH-60}" height="150" fill="{vcolor}" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>
  <rect x="48" y="50" width="190" height="40" fill="white" rx="20" ry="20"/>
  <text x="143" y="78" font-size="24" fill="{cat_color}" text-anchor="middle" font-family="Arial" font-weight="bold">{xesc(category)}</text>
  {pips}
  <text x="{CARD_WIDTH/2}" y="158" font-size="{name_size}" fill="rgba(0,0,0,0.25)" text-anchor="middle" font-family="Arial" font-weight="bold">{xesc(name)}</text>
  <text x="{CARD_WIDTH/2 - 2}" y="156" font-size="{name_size}" fill="white" text-anchor="middle" font-family="Arial" font-weight="bold">{xesc(name)}</text>

  <!-- affective-field compass with the umwelt eyeball -->
  {eyeball_compass(rec, CARD_WIDTH/2, 360, 145, vcolor)}

  <!-- tagline -->
  {tspans(tagline_lines, CARD_WIDTH/2, tag_start, tag_lh, font_size=str(tag_f), fill=INK, text_anchor="middle", font_family="Arial", font_style="italic")}

  <!-- body -->
  {tspans(body_lines, 40, 632, body_lh, font_size=str(body_f), fill=INK, font_family="Arial")}

  <!-- stats band -->
  <rect x="30" y="850" width="{CARD_WIDTH-60}" height="92" fill="{DARK_BAND}" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>
  <text x="{CARD_WIDTH/2}" y="892" font-size="27" fill="white" text-anchor="middle" font-family="Arial" font-weight="bold">{xesc(valence)} &#183; {xesc(category)} &#183; {xesc(obj)}</text>
  <text x="{CARD_WIDTH/2}" y="924" font-size="22" fill="rgb(200,200,205)" text-anchor="middle" font-family="Arial">Intensity: {xesc(intensity)}</text>

  <!-- combo edges band -->
  <rect x="30" y="952" width="{CARD_WIDTH-60}" height="78" fill="{DARK_BAND_2}" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>
  {edges_block}

  <text x="{CARD_WIDTH/2}" y="1056" font-size="17" fill="rgb(150,148,142)" text-anchor="middle" font-family="Arial">{xesc(rec['id'])} &#183; {xesc(db_name)}</text>

  <rect x="5" y="5" width="{CARD_WIDTH-10}" height="{CARD_HEIGHT-10}" fill="none" stroke="black" stroke-width="8" rx="{CARD_CORNER}" ry="{CARD_CORNER}"/>
</svg>
"""


def card_back_svg(db_name: str, deck_label: str = "Feelings") -> str:
    cx, cy = CARD_WIDTH / 2, CARD_HEIGHT / 2 - 40
    return f"""<svg width="{CARD_WIDTH}" height="{CARD_HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <rect x="5" y="5" width="{CARD_WIDTH-10}" height="{CARD_HEIGHT-10}" fill="{DARK_BAND}" rx="{CARD_CORNER}" ry="{CARD_CORNER}"/>
  <text x="{cx}" y="180" font-size="56" fill="white" text-anchor="middle" font-family="Arial" font-weight="bold">TOOT TOOT</text>
  <text x="{cx}" y="240" font-size="44" fill="rgb(200,200,205)" text-anchor="middle" font-family="Arial">{xesc(deck_label.upper())}</text>

  <circle cx="{cx}" cy="{cy}" r="150" fill="rgb(70,70,80)" stroke="rgb(110,110,122)" stroke-width="3"/>
  <line x1="{cx-150}" y1="{cy}" x2="{cx+150}" y2="{cy}" stroke="rgb(96,96,108)" stroke-width="2"/>
  <line x1="{cx}" y1="{cy-150}" x2="{cx}" y2="{cy+150}" stroke="rgb(96,96,108)" stroke-width="2"/>
  <text x="{cx+96}" y="{cy-96}" font-size="26" fill="{POS_COLOR}" text-anchor="middle" font-family="Arial">NE</text>
  <text x="{cx-96}" y="{cy-96}" font-size="26" fill="{POS_COLOR}" text-anchor="middle" font-family="Arial">NW</text>
  <text x="{cx+96}" y="{cy+108}" font-size="26" fill="{NEG_COLOR}" text-anchor="middle" font-family="Arial">SE</text>
  <text x="{cx-96}" y="{cy+108}" font-size="26" fill="{NEG_COLOR}" text-anchor="middle" font-family="Arial">SW</text>
  <circle cx="{cx}" cy="{cy}" r="46" fill="white" stroke="black" stroke-width="4"/>
  <circle cx="{cx}" cy="{cy}" r="20" fill="{EYE_RED}" stroke="black" stroke-width="2"/>
  <circle cx="{cx}" cy="{cy}" r="10" fill="black"/>
  <circle cx="{cx-10}" cy="{cy-10}" r="6" fill="white" fill-opacity="0.85"/>

  <text x="{cx}" y="{CARD_HEIGHT-130}" font-size="24" fill="rgb(190,190,196)" text-anchor="middle" font-family="Arial">lat = valence &#183; lon = object &#183; distance = intensity</text>
  <text x="{cx}" y="{CARD_HEIGHT-90}" font-size="20" fill="rgb(150,150,158)" text-anchor="middle" font-family="Arial">{xesc(db_name)}</text>
  <rect x="5" y="5" width="{CARD_WIDTH-10}" height="{CARD_HEIGHT-10}" fill="none" stroke="black" stroke-width="8" rx="{CARD_CORNER}" ry="{CARD_CORNER}"/>
</svg>
"""


def page_svg(card_pngs: list[Path]) -> str:
    svg = [
        f'<svg width="{PAGE_WIDTH}" height="{PAGE_HEIGHT}" xmlns="http://www.w3.org/2000/svg">',
        f'<rect x="0" y="0" width="{PAGE_WIDTH}" height="{PAGE_HEIGHT}" fill="black" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>',
    ]
    for i, png in enumerate(card_pngs):
        row, col = divmod(i, 3)
        x = col * (CARD_WIDTH + CARD_SPACING) + LEFT_SIDE_OF_PAGE
        y = row * (CARD_HEIGHT + CARD_SPACING) + TOP_OF_PAGE
        svg.append(f'<image href="{png.resolve().as_uri()}" x="{x}" y="{y}" width="{CARD_WIDTH}" height="{CARD_HEIGHT}"/>')
    svg.append("</svg>")
    return "\n".join(svg)


def back_page_svg(back_png: Path) -> str:
    href = back_png.resolve().as_uri()
    svg = [
        f'<svg width="{PAGE_WIDTH}" height="{PAGE_HEIGHT}" xmlns="http://www.w3.org/2000/svg">',
        f'<rect x="0" y="0" width="{PAGE_WIDTH}" height="{PAGE_HEIGHT}" fill="black" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>',
    ]
    for row in range(3):
        for col in range(3):
            x = col * (CARD_WIDTH + CARD_SPACING) + LEFT_SIDE_OF_PAGE
            y = row * (CARD_HEIGHT + CARD_SPACING) + TOP_OF_PAGE
            svg.append(f'<image href="{href}" x="{x}" y="{y}" width="{CARD_WIDTH}" height="{CARD_HEIGHT}"/>')
    svg.append("</svg>")
    return "\n".join(svg)


# --- Rendering ----------------------------------------------------------------------
def svg_to_png(svg_file: Path, png_file: Path) -> None:
    inkscape = shutil.which("inkscape")
    if inkscape:
        subprocess.run(
            [inkscape, str(svg_file), "--export-type=png", "--export-filename", str(png_file)],
            check=True, capture_output=True,
        )
        return
    import cairosvg  # fallback
    cairosvg.svg2png(url=str(svg_file), write_to=str(png_file))


def assemble_pdf(front_pages: list[Path], back_page: Path, out_pdf: Path) -> None:
    from PIL import Image
    pages: list[Image.Image] = []
    for fp in front_pages:
        pages.append(Image.open(fp).convert("RGB"))
        pages.append(Image.open(back_page).convert("RGB"))
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(out_pdf, "PDF", resolution=300.0, save_all=True, append_images=pages[1:])


def write_box_readme(box_dir: Path, deck_label: str, deck_pdf: Path,
                     rules_pdf: Path | None, n_cards: int, n_pages: int) -> None:
    """Write a box-insert README describing the boxed game's contents and how to print it."""
    rules_line = f"- **{rules_pdf.name}** — the full rules booklet.\n" if rules_pdf else ""
    readme = f"""# {deck_label} — boxed game

Print-and-play artifacts for **{deck_label}**, generated from the Feelings TTDB and the
game's rules. Regenerate with:

```bash
cd tools/feelings_cards && python generate_feelings_cards.py --deck {slugify(deck_label).lower()}
```

## Contents
- **{deck_pdf.name}** — the card deck: {n_cards} cards across {n_pages} front page(s),
  each followed by a matching card back for **duplex** printing.
{rules_line}- **README.md** — this file.

## Printing the deck
- Print **{deck_pdf.name}** at **100% / actual size** (no "fit to page") on US Letter.
- Use **double-sided (duplex)**, flip on the **long edge**, on white cardstock.
- Cards are **2.5" × 3.5"** (poker size) with 1/8" gutters — cut on the gutters; sleeve if you like.

## You also need (not printed)
A pulse source (phone metronome or a human click track) and small tokens for
Pulse / Drift / Swing and a Baton marker — any beads, cubes, or coins work.
See the rules booklet for counts.

*Generated by `tools/feelings_cards/generate_feelings_cards.py`.*
"""
    (box_dir / "README.md").write_text(readme, encoding="utf-8")


# --- Pulse deck composition (the full print-and-play set) ---------------------------
# These tables mirror games/pulse/Pulse-Print-and-Play.md exactly. Feeling cards stay
# TTDB-driven (rendered by card_front_svg); the other four types are synthesized here.

# Story Track ×6 — Hero's Arc beats: (beat, name, lat, lon, valence, tagline, edge, stage, win)
PULSE_STORY = [
    (1, "Serenity", 10, -10, "pos", "A mild, quiet ease.", "deepens → Unease", "ordinary world", False),
    (2, "Unease", -10, -10, "neg", "Something not quite right.", "resonates → Fear", "the call", False),
    (3, "Fear", -30, 20, "neg", "Danger crystallizes and hijacks attention.", "intensifies → Grief", "the ordeal", False),
    (4, "Grief", -30, -30, "neg", "What was loved is irreversibly gone.", "blooms → Hope", "the dark night", False),
    (5, "Hope", 20, 20, "pos", "A possibility opens in the wreckage.", "blooms → Joy", "the turn", False),
    (6, "Joy", 30, 30, "pos", "The self reconstituted and enlarged.", "reach here = WIN", "the return", True),
]

# Character ×5 — dispositions as classes: (name, disposition, lat, lon, reaches, strains, quote)
PULSE_CHARS = [
    ("THE SEEKER", "Curiosity", 10, 40, "Unease, Hope", "Grief", "A forward lean toward the unknown."),
    ("THE WARDEN", "Suspicion", -20, -30, "Fear, Grief", "Joy", "Reading the world for hidden threat."),
    ("THE HEALER", "Compassion", 30, 40, "Hope, Joy", "Fear", "Moved to care for another's suffering."),
    ("THE HERMIT", "Equanimity", 30, -20, "Serenity, Grief", "Hope", "Holds joy and sorrow without overturning."),
    ("THE TRICKSTER", "Indifference", -10, -40, "Fear, Unease", "Joy, Hope", "The world does not call to it."),
]

# Part ×8 — beat_mask, two copies each: (name, mask, line1, line2, copies)
PULSE_PARTS = [
    ("HI-HAT", [1, 2, 3, 4], "Timekeeper — every beat.", "The band's spine.", 2),
    ("BACKBEAT", [2, 4], "The groove. Holds the bar", "during a Baton handoff.", 2),
    ("LEAD", [1], "Sounds the story advance.", "Clean downbeat = Marker++", 2),
    ("RIM", [3], "Offbeat accent. Covers", "the middle of the bar.", 2),
]

# Feeling ×32 — TTDB titles with copy counts (6 exact @4, 4 neighbors @2)
PULSE_FEELINGS = [
    ("Serenity", 4), ("Unease", 4), ("Fear", 4), ("Grief", 4), ("Hope", 4), ("Joy", 4),
    ("Contentment", 2), ("Melancholy", 2), ("Frustration", 2), ("Excitement", 2),
]

# Reference ×6 — identical quick-reference card (condensed from Pulse.md §9)
PULSE_REFERENCE = 6
PULSE_REFERENCE_LINES = [
    "A BAR = 4 metronome beats.",
    "YOUR BEAT = your Part's beat_mask.",
    "",
    "ON YOUR BEAT, with the click:",
    " play a Feeling that REACHES /",
    " EDGES the required emotion.",
    "  Reaches -> clean, +Swing token",
    "  Strains -> +1 Drift",
    "  miss/late/illegal -> -1 Pulse,",
    "                       +1 Drift",
    "  two on same beat   -> -1 Pulse",
    "",
    "CONDUCTOR (Baton): calls next",
    " emotion on beat 4; must Reach.",
    " Bust/strain -> hand baton to one",
    " who Reaches; era +1. Backbeat",
    " holds; new conductor counts in.",
    "",
    "DRIFT hits 3 -> Resync: skip a",
    " bar, clear Drift, re-count.",
    "SWING token: push/lay-back on",
    " purpose -> clean + draw a card.",
    "",
    "WIN story: reach JOY, >=1 Pulse.",
    "LOSE: Pulse hits 0.",
    "WIN set: 3 stories, 60->80->100.",
]


def _compass_rec(lat: int, lon: int, intensity: str = "L3") -> dict:
    """Minimal record so eyeball_compass can plot a node by lat/lon."""
    return {"lat": lat, "lon": lon, "fields": {"Intensity": intensity}}


def num_badge(label: str, cx: float, cy: float, r: float, fill: str, tcolor: str,
              stroke: str = "white") -> str:
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
        f'<text x="{cx}" y="{cy + r*0.36:.1f}" font-size="{r*1.1:.0f}" fill="{tcolor}" '
        f'text-anchor="middle" font-family="Arial" font-weight="bold">{label}</text>'
    )


def _card_open(border_color: str) -> str:
    return (
        f'<svg width="{CARD_WIDTH}" height="{CARD_HEIGHT}" xmlns="http://www.w3.org/2000/svg">\n'
        f'  <rect x="5" y="5" width="{CARD_WIDTH-10}" height="{CARD_HEIGHT-10}" '
        f'fill="{CREAM}" rx="{CARD_CORNER}" ry="{CARD_CORNER}"/>'
    )


def _card_close(border_color: str) -> str:
    return (
        f'  <rect x="5" y="5" width="{CARD_WIDTH-10}" height="{CARD_HEIGHT-10}" fill="none" '
        f'stroke="{border_color}" stroke-width="10" rx="{CARD_CORNER}" ry="{CARD_CORNER}"/>\n</svg>\n'
    )


def story_front_svg(spec, db_name: str) -> str:
    beat, name, lat, lon, val, tagline, edge, stage, win = spec
    vcolor = POS_COLOR if val == "pos" else NEG_COLOR
    name_size = 64 if len(name) <= 14 else 50
    if win:
        band = (
            f'<rect x="30" y="952" width="{CARD_WIDTH-60}" height="78" fill="{GOLD_DK}" '
            f'rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>'
            f'<text x="{CARD_WIDTH/2}" y="1002" font-size="34" fill="white" text-anchor="middle" '
            f'font-family="Arial" font-weight="bold">★ REACH HERE = WIN</text>'
        )
    else:
        band = (
            f'<rect x="30" y="952" width="{CARD_WIDTH-60}" height="78" fill="{DARK_BAND_2}" '
            f'rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>'
            f'<text x="{CARD_WIDTH/2}" y="1000" font-size="26" fill="white" text-anchor="middle" '
            f'font-family="Arial">edge out: {xesc(edge)}</text>'
        )
    tag_lines, tag_f = fit_tagline(tagline)
    tag_lh = round(tag_f * 1.28, 1)
    tag_start = 552 - (len(tag_lines) - 1) * tag_lh / 2
    return f"""{_card_open(GOLD)}
  <rect x="30" y="30" width="{CARD_WIDTH-60}" height="150" fill="{GOLD}" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>
  {num_badge(str(beat), 105, 105, 42, "white", GOLD_DK)}
  <text x="172" y="78" font-size="24" fill="rgba(255,255,255,0.85)" font-family="Arial" font-weight="bold">STORY</text>
  <text x="{CARD_WIDTH/2 + 40}" y="156" font-size="{name_size}" fill="white" text-anchor="middle" font-family="Arial" font-weight="bold">{xesc(name)}</text>
  {eyeball_compass(_compass_rec(lat, lon), CARD_WIDTH/2, 360, 145, vcolor)}
  {tspans(tag_lines, CARD_WIDTH/2, tag_start, tag_lh, font_size=str(tag_f), fill=INK, text_anchor="middle", font_family="Arial", font_style="italic")}
  <text x="{CARD_WIDTH/2}" y="700" font-size="28" fill="{GOLD_DK}" text-anchor="middle" font-family="Arial" font-weight="bold">Hero's Arc: {xesc(stage)}</text>
  <rect x="30" y="850" width="{CARD_WIDTH-60}" height="92" fill="{DARK_BAND}" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>
  <text x="{CARD_WIDTH/2}" y="892" font-size="27" fill="white" text-anchor="middle" font-family="Arial" font-weight="bold">Beat {beat} &#183; @LAT{lat}LON{lon}</text>
  <text x="{CARD_WIDTH/2}" y="924" font-size="22" fill="rgb(200,200,205)" text-anchor="middle" font-family="Arial">valence {'+' if val == 'pos' else '−'}</text>
  {band}
  <text x="{CARD_WIDTH/2}" y="1056" font-size="17" fill="rgb(150,148,142)" text-anchor="middle" font-family="Arial">Story Track &#183; {xesc(db_name)}</text>
{_card_close(GOLD)}"""


def character_front_svg(spec, db_name: str) -> str:
    name, disp, lat, lon, reaches, strains, quote = spec
    vcolor = POS_COLOR if lat >= 0 else NEG_COLOR
    name_size = 56 if len(name) <= 14 else 46
    tag_lines, tag_f = fit_tagline(quote)
    tag_lh = round(tag_f * 1.28, 1)
    tag_start = 552 - (len(tag_lines) - 1) * tag_lh / 2
    return f"""{_card_open(BLUE)}
  <rect x="30" y="30" width="{CARD_WIDTH-60}" height="150" fill="{BLUE}" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>
  <rect x="48" y="50" width="240" height="40" fill="white" rx="20" ry="20"/>
  <text x="168" y="78" font-size="24" fill="{BLUE}" text-anchor="middle" font-family="Arial" font-weight="bold">CHARACTER</text>
  <text x="{CARD_WIDTH/2}" y="158" font-size="{name_size}" fill="white" text-anchor="middle" font-family="Arial" font-weight="bold">{xesc(name)}</text>
  {eyeball_compass(_compass_rec(lat, lon), CARD_WIDTH/2, 360, 145, vcolor)}
  {tspans(tag_lines, CARD_WIDTH/2, tag_start, tag_lh, font_size=str(tag_f), fill=INK, text_anchor="middle", font_family="Arial", font_style="italic")}
  <text x="{CARD_WIDTH/2}" y="700" font-size="30" fill="{BLUE_DK}" text-anchor="middle" font-family="Arial" font-weight="bold">Disposition: {xesc(disp.upper())}</text>
  <rect x="30" y="850" width="{CARD_WIDTH-60}" height="92" fill="{DARK_BAND}" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>
  <text x="60" y="892" font-size="26" fill="{POS_COLOR}" font-family="Arial" font-weight="bold">Reaches: <tspan fill="white">{xesc(reaches)}</tspan></text>
  <text x="60" y="926" font-size="20" fill="rgb(200,200,205)" font-family="Arial">play for free (+Swing if clean)</text>
  <rect x="30" y="952" width="{CARD_WIDTH-60}" height="78" fill="{DARK_BAND_2}" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>
  <text x="60" y="994" font-size="26" fill="{NEG_COLOR}" font-family="Arial" font-weight="bold">Strains: <tspan fill="white">{xesc(strains)}</tspan></text>
  <text x="60" y="1020" font-size="18" fill="rgb(180,180,186)" font-family="Arial">costs +1 Drift to play</text>
  <text x="{CARD_WIDTH/2}" y="1056" font-size="17" fill="rgb(150,148,142)" text-anchor="middle" font-family="Arial">@LAT{lat}LON{lon} &#183; {xesc(db_name)}</text>
{_card_close(BLUE)}"""


def part_front_svg(spec, copy_idx: int, db_name: str) -> str:
    name, mask, line1, line2, _copies = spec
    pips = ""
    for i in range(1, 5):
        on = i in mask
        cx = CARD_WIDTH / 2 - 195 + (i - 1) * 130
        pips += num_badge(
            str(i), cx, 380, 52,
            SLATE if on else "rgb(225,223,218)",
            "white" if on else "rgb(150,148,142)",
            stroke=SLATE_DK if on else "rgb(200,198,192)",
        )
    mask_label = " ".join(str(b) for b in range(1, 5) if b in mask)
    return f"""{_card_open(SLATE)}
  <rect x="30" y="30" width="{CARD_WIDTH-60}" height="150" fill="{SLATE}" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>
  <rect x="48" y="50" width="130" height="40" fill="white" rx="20" ry="20"/>
  <text x="113" y="78" font-size="24" fill="{SLATE}" text-anchor="middle" font-family="Arial" font-weight="bold">PART</text>
  <text x="{CARD_WIDTH/2}" y="158" font-size="60" fill="white" text-anchor="middle" font-family="Arial" font-weight="bold">{xesc(name)}</text>
  <text x="{CARD_WIDTH/2}" y="290" font-size="28" fill="{SLATE_DK}" text-anchor="middle" font-family="Arial" font-weight="bold">beat_mask</text>
  {pips}
  <text x="{CARD_WIDTH/2}" y="470" font-size="26" fill="rgb(110,108,104)" text-anchor="middle" font-family="Arial">beats: {mask_label}</text>
  <text x="{CARD_WIDTH/2}" y="640" font-size="30" fill="{INK}" text-anchor="middle" font-family="Arial">{xesc(line1)}</text>
  <text x="{CARD_WIDTH/2}" y="684" font-size="30" fill="{INK}" text-anchor="middle" font-family="Arial">{xesc(line2)}</text>
  <rect x="30" y="850" width="{CARD_WIDTH-60}" height="92" fill="{DARK_BAND}" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>
  <text x="{CARD_WIDTH/2}" y="908" font-size="26" fill="white" text-anchor="middle" font-family="Arial">Deal 1 per player each story</text>
  <text x="{CARD_WIDTH/2}" y="1056" font-size="17" fill="rgb(150,148,142)" text-anchor="middle" font-family="Arial">Part &#183; copy {copy_idx} &#183; {xesc(db_name)}</text>
{_card_close(SLATE)}"""


def reference_front_svg(db_name: str) -> str:
    body = []
    y0 = 248
    lh = 30
    for i, ln in enumerate(PULSE_REFERENCE_LINES):
        body.append(
            f'<text x="56" y="{y0 + i*lh}" font-size="22" fill="rgb(230,230,234)" '
            f'font-family="Courier New, monospace">{xesc(ln)}</text>'
        )
    return f"""<svg width="{CARD_WIDTH}" height="{CARD_HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <rect x="5" y="5" width="{CARD_WIDTH-10}" height="{CARD_HEIGHT-10}" fill="{DARK_BAND}" rx="{CARD_CORNER}" ry="{CARD_CORNER}"/>
  <rect x="30" y="30" width="{CARD_WIDTH-60}" height="170" fill="rgb(70,70,80)" rx="{PAGE_CORNER}" ry="{PAGE_CORNER}"/>
  <text x="{CARD_WIDTH/2}" y="110" font-size="40" fill="white" text-anchor="middle" font-family="Arial" font-weight="bold">PULSE</text>
  <text x="{CARD_WIDTH/2}" y="160" font-size="28" fill="rgb(200,200,205)" text-anchor="middle" font-family="Arial">QUICK REFERENCE</text>
  {''.join(body)}
  <text x="{CARD_WIDTH/2}" y="1052" font-size="17" fill="rgb(140,140,148)" text-anchor="middle" font-family="Arial">Reference &#183; {xesc(db_name)}</text>
  <rect x="5" y="5" width="{CARD_WIDTH-10}" height="{CARD_HEIGHT-10}" fill="none" stroke="black" stroke-width="8" rx="{CARD_CORNER}" ry="{CARD_CORNER}"/>
</svg>
"""


def build_pulse_jobs(by_title: dict, coord2name: dict, db_name: str) -> list[tuple[str, str]]:
    """Build the full 57-card Pulse set as (slug, front_svg) jobs, in cut-list order."""
    jobs: list[tuple[str, str]] = []
    # 1. Story Track ×6
    for spec in PULSE_STORY:
        jobs.append((f"story_{spec[0]}_{slugify(spec[1])}", story_front_svg(spec, db_name)))
    # 2. Character ×5
    for spec in PULSE_CHARS:
        jobs.append((f"char_{slugify(spec[0])}", character_front_svg(spec, db_name)))
    # 3. Part ×8 (2 copies each)
    for spec in PULSE_PARTS:
        for c in range(1, spec[4] + 1):
            jobs.append((f"part_{slugify(spec[0])}_{c}", part_front_svg(spec, c, db_name)))
    # 4. Feeling ×32 (TTDB-driven, with copies)
    for title, copies in PULSE_FEELINGS:
        rec = by_title.get(title)
        if rec is None:
            print(f"  ! feeling '{title}' not found in TTDB — skipped")
            continue
        svg = card_front_svg(rec, coord2name, db_name)
        for c in range(1, copies + 1):
            jobs.append((f"feeling_{slugify(title)}_{c}", svg))
    # 5. Reference ×6
    ref_svg = reference_front_svg(db_name)
    for c in range(1, PULSE_REFERENCE + 1):
        jobs.append((f"reference_{c}", ref_svg))
    return jobs


# --- Main ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Generate Feeling cards from a Feelings TTDB.")
    ap.add_argument("--ttdb", default="../../reference/feelings_ttdb.md", help="Path to the Feelings TTDB markdown.")
    ap.add_argument("--deck", default="feelings", choices=sorted(DECKS),
                    help="Which deck to print (feelings = whole field; pulse = Pulse subset).")
    ap.add_argument("--out-dir", default="build", help="Base output directory.")
    ap.add_argument("--keep-svgs", action="store_true", help="Keep intermediate SVGs.")
    args = ap.parse_args()

    deck = DECKS[args.deck]
    deck_label = deck["name"]

    base = Path(__file__).resolve().parent
    ttdb_path = (base / args.ttdb).resolve() if not Path(args.ttdb).is_absolute() else Path(args.ttdb)
    if not ttdb_path.exists():
        raise FileNotFoundError(f"TTDB not found: {ttdb_path}")

    text = ttdb_path.read_text(encoding="utf-8")
    db_name_m = re.search(r"db_id:\s*(\S+)", text)
    db_name = db_name_m.group(1) if db_name_m else "feelings"

    records = parse_records(text)
    coord2name = {r["id"]: r["title"] for r in records if r["title"]}
    cards = [r for r in records if is_card(r)]
    if not cards:
        raise ValueError("No Feeling cards found (no records with a Category field).")
    by_title = {r["title"]: r for r in cards}

    # Build the render jobs: a list of (unique-slug, front-SVG) pairs.
    jobs: list[tuple[str, str]] = []
    if deck.get("composition") == "pulse":
        jobs = build_pulse_jobs(by_title, coord2name, db_name)
    else:
        if deck["cards"] is not None:
            ordered = []
            for title in deck["cards"]:
                if title in by_title:
                    ordered.append(by_title[title])
                else:
                    print(f"  ! '{title}' not found in TTDB — skipped")
            if not ordered:
                raise ValueError(f"No matching cards for deck '{args.deck}'.")
            cards = ordered
        jobs = [(slugify(r["title"]), card_front_svg(r, coord2name, db_name)) for r in cards]

    slug = slugify(deck_label)
    out_base = (base / args.out_dir).resolve()
    cards_dir = out_base / "cards" / slug
    pages_dir = out_base / "pages" / slug
    pdf_dir = out_base / "output" / slug
    for d in (cards_dir, pages_dir):
        d.mkdir(parents=True, exist_ok=True)

    print(f"Deck '{deck_label}': {len(jobs)} cards from {ttdb_path.name}")

    # 1. individual card PNGs
    card_pngs: list[Path] = []
    for cslug, front_svg in jobs:
        svg_p = cards_dir / f"{cslug}.svg"
        png_p = cards_dir / f"{cslug}.png"
        svg_p.write_text(front_svg, encoding="utf-8")
        svg_to_png(svg_p, png_p)
        card_pngs.append(png_p)
        if not args.keep_svgs:
            svg_p.unlink(missing_ok=True)
        print(f"  card: {cslug}")

    # 2. back card
    back_svg = cards_dir / "_back.svg"
    back_png = cards_dir / "_back.png"
    back_svg.write_text(card_back_svg(db_name, deck_label), encoding="utf-8")
    svg_to_png(back_svg, back_png)
    if not args.keep_svgs:
        back_svg.unlink(missing_ok=True)

    # 3. front pages (3x3)
    front_pages: list[Path] = []
    for i in range(0, len(card_pngs), 9):
        chunk = card_pngs[i:i + 9]
        n = i // 9 + 1
        psvg = pages_dir / f"{slug}_page_{n}.svg"
        ppng = pages_dir / f"{slug}_page_{n}.png"
        psvg.write_text(page_svg(chunk), encoding="utf-8")
        svg_to_png(psvg, ppng)
        front_pages.append(ppng)
        if not args.keep_svgs:
            psvg.unlink(missing_ok=True)

    # 4. back page (tiled)
    bsvg = pages_dir / f"{slug}_back_page.svg"
    bpng = pages_dir / f"{slug}_back_page.png"
    bsvg.write_text(back_page_svg(back_png), encoding="utf-8")
    svg_to_png(bsvg, bpng)
    if not args.keep_svgs:
        bsvg.unlink(missing_ok=True)

    # 5. duplex PDF
    out_pdf = pdf_dir / f"{slug}_deck.pdf"
    assemble_pdf(front_pages, bpng, out_pdf)
    print(f"\nDeck PDF: {out_pdf}")
    print(f"Pages: {len(front_pages)} front + alternating backs ({len(card_pngs)} cards)")

    # 6. boxed game: copy the deck PDF + render rules PDF into the box folder
    if deck.get("box"):
        box_dir = (base / deck["box"]).resolve()
        box_dir.mkdir(parents=True, exist_ok=True)
        deck_final = box_dir / f"{slug}_Deck.pdf"
        shutil.copyfile(out_pdf, deck_final)

        rules_final = None
        if deck.get("instructions"):
            from instructions_pdf import render_markdown_pdf
            rules_src = (base / deck["instructions"]).resolve()
            rules_final = box_dir / f"{slug}_Rules.pdf"
            render_markdown_pdf(rules_src, rules_final, title=deck_label,
                                accent=deck.get("accent", (34, 139, 96)))

        write_box_readme(box_dir, deck_label, deck_final, rules_final, len(card_pngs), len(front_pages))
        print(f"\nBoxed game: {box_dir}")
        print(f"  - {deck_final.name}")
        if rules_final:
            print(f"  - {rules_final.name}")
        print(f"  - README.md")


if __name__ == "__main__":
    main()
