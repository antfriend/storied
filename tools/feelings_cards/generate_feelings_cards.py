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
        "instructions": "../../games/Pulse.md",
        "accent": (34, 139, 96),
        "cards": [
            # Story Track — the Hero's Arc, in beat order (Pulse.md §2.1)
            "Serenity", "Unease", "Fear", "Grief", "Hope", "Joy",
            # Hand near-neighbors (Pulse.md §2.4)
            "Contentment", "Melancholy", "Frustration", "Excitement",
            # Character dispositions as classes (Pulse.md §2.2)
            "Curiosity", "Suspicion", "Compassion", "Equanimity", "Indifference",
        ],
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

    if deck["cards"] is not None:
        by_title = {r["title"]: r for r in cards}
        ordered = []
        for title in deck["cards"]:
            if title in by_title:
                ordered.append(by_title[title])
            else:
                print(f"  ! '{title}' not found in TTDB — skipped")
        if not ordered:
            raise ValueError(f"No matching cards for deck '{args.deck}'.")
        cards = ordered

    slug = slugify(deck_label)
    out_base = (base / args.out_dir).resolve()
    cards_dir = out_base / "cards" / slug
    pages_dir = out_base / "pages" / slug
    pdf_dir = out_base / "output" / slug
    for d in (cards_dir, pages_dir):
        d.mkdir(parents=True, exist_ok=True)

    print(f"Deck '{deck_label}': {len(cards)} cards from {ttdb_path.name}")

    # 1. individual card PNGs
    card_pngs: list[Path] = []
    for rec in cards:
        cslug = slugify(rec["title"])
        svg_p = cards_dir / f"{cslug}.svg"
        png_p = cards_dir / f"{cslug}.png"
        svg_p.write_text(card_front_svg(rec, coord2name, db_name), encoding="utf-8")
        svg_to_png(svg_p, png_p)
        card_pngs.append(png_p)
        if not args.keep_svgs:
            svg_p.unlink(missing_ok=True)
        print(f"  card: {rec['title']}")

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
