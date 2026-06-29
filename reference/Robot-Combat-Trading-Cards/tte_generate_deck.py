#!/usr/bin/env python3
import argparse
import unicodedata
import re
import subprocess
from pathlib import Path

from pypdf import PdfReader, PdfWriter

# Page size: U.S. Letter at 300 dpi
PAGE_WIDTH = 2550
PAGE_HEIGHT = 3300

# Card layout: 3x3 grid with 1/8" (38 px) spacing
CARD_SPACING = 38
CARD_WIDTH = 770
LEFT_SIDE_OF_PAGE = 82
CARD_HEIGHT = 1074
CORNER_SIZE = 40


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.strip())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9]+", "_", ascii_text)
    slug = slug.strip("_")
    return slug or "item"


def assemble_pngs_to_pdf_with_alternating_backs(front_pngs, back_png, output_pdf: Path) -> None:
    """Assemble page PNGs into a PDF with alternating card back pages."""
    import img2pdf

    front_pdfs = []
    for front_png in front_pngs:
        front_pdf = front_png.with_suffix(".pdf")
        with open(front_pdf, "wb") as f:
            f.write(img2pdf.convert(str(front_png)))
        front_pdfs.append(front_pdf)

    back_pdf = back_png.with_suffix(".pdf")
    with open(back_pdf, "wb") as f:
        f.write(img2pdf.convert(str(back_png)))

    writer = PdfWriter()
    for front_pdf in front_pdfs:
        writer.append(PdfReader(str(front_pdf)))
        writer.append(PdfReader(str(back_pdf)))

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with open(output_pdf, "wb") as f:
        writer.write(f)

    print(f"Generated PDF with alternating card backs: {output_pdf}")

    for pdf in front_pdfs + [back_pdf]:
        pdf.unlink(missing_ok=True)


def create_front_page_svg(card_pngs: list[Path]) -> str:
    """Create a full-page SVG embedding individual card PNGs in a 3x3 grid."""
    svg = f"""<svg width="{PAGE_WIDTH}" height="{PAGE_HEIGHT}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{PAGE_WIDTH}" height="{PAGE_HEIGHT}" fill="black" rx="{CORNER_SIZE}" ry="{CORNER_SIZE}" />
"""
    cards_per_row = 3
    for i, card_png in enumerate(card_pngs):
        row = i // cards_per_row
        col = i % cards_per_row
        x = col * (CARD_WIDTH + CARD_SPACING) + LEFT_SIDE_OF_PAGE
        y = row * (CARD_HEIGHT + CARD_SPACING) + 3
        href = card_png.resolve().as_uri()
        svg += f'    <image href="{href}" x="{x}" y="{y}" width="{CARD_WIDTH}" height="{CARD_HEIGHT}" />\n'
    svg += "</svg>"
    return svg


def create_back_page_svg(back_png: Path) -> str:
    """Create a full-page SVG tiling the individual back card PNG in a 3x3 grid."""
    href = back_png.resolve().as_uri()
    svg = f"""<svg width="{PAGE_WIDTH}" height="{PAGE_HEIGHT}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{PAGE_WIDTH}" height="{PAGE_HEIGHT}" fill="black" rx="{CORNER_SIZE}" ry="{CORNER_SIZE}" />
"""
    for row in range(3):
        for col in range(3):
            x = col * (CARD_WIDTH + CARD_SPACING) + LEFT_SIDE_OF_PAGE
            y = row * (CARD_HEIGHT + CARD_SPACING) + 3
            svg += f'    <image href="{href}" x="{x}" y="{y}" width="{CARD_WIDTH}" height="{CARD_HEIGHT}" />\n'
    svg += "</svg>"
    return svg


def svg_to_png(svg_file: Path, png_file: Path) -> None:
    subprocess.run(
        ["inkscape", str(svg_file), "--export-filename", str(png_file)],
        check=True,
    )
    print(f"Converted {svg_file} to {png_file}")


def find_card_pngs(cards_dir: Path, event_slug: str) -> list[Path]:
    """Find individual card PNGs, excluding event-level page files."""
    return sorted(
        p for p in cards_dir.glob("*.png")
        if not p.name.startswith(f"{event_slug}_")
    )


def find_back_png(cards_dir: Path, event_slug: str) -> Path:
    """Find the individual back card PNG."""
    back_png = cards_dir / f"{event_slug}_back.png"
    if not back_png.exists():
        raise FileNotFoundError(
            f"Back card PNG not found: {back_png}\n"
            f"Run tte_generate_cards.py first to generate individual cards."
        )
    return back_png


def generate_deck_pdf(
    cards_dir: Path,
    event_slug: str,
    event_name: str,
    output_dir: Path,
    keep_svgs: bool,
    keep_pngs: bool,
) -> Path:
    card_pngs = find_card_pngs(cards_dir, event_slug)
    if not card_pngs:
        raise ValueError(f"No individual card PNGs found in {cards_dir}")

    back_png = find_back_png(cards_dir, event_slug)

    print(f"Found {len(card_pngs)} card(s) in {cards_dir}")

    svg_dir = cards_dir / "svgs"
    svg_dir.mkdir(parents=True, exist_ok=True)

    max_cards_per_page = 9  # 3x3
    page_pngs = []
    page_num = 1

    for start in range(0, len(card_pngs), max_cards_per_page):
        page_cards = card_pngs[start : start + max_cards_per_page]
        svg_file = svg_dir / f"{event_slug}_robot_page_{page_num}.svg"
        png_file = cards_dir / f"{event_slug}_robot_page_{page_num}.png"

        svg_file.write_text(create_front_page_svg(page_cards), encoding="utf-8")
        print(f"Generated SVG for page {page_num}: {svg_file}")
        svg_to_png(svg_file, png_file)
        page_pngs.append(png_file)
        page_num += 1

    back_page_svg = svg_dir / f"{event_slug}_card_back_page.svg"
    back_page_png = cards_dir / f"{event_slug}_card_back_page.png"
    back_page_svg.write_text(create_back_page_svg(back_png), encoding="utf-8")
    print(f"Generated SVG for card back page: {back_page_svg}")
    svg_to_png(back_page_svg, back_page_png)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_pdf = output_dir / f"{event_slug}_deck.pdf"
    assemble_pngs_to_pdf_with_alternating_backs(page_pngs, back_page_png, output_pdf)
    print(f"Final PDF: {output_pdf}")

    if not keep_svgs:
        for svg_path in svg_dir.glob("*.svg"):
            svg_path.unlink(missing_ok=True)
        try:
            svg_dir.rmdir()
        except OSError:
            pass

    if not keep_pngs:
        for png in page_pngs + [back_page_png]:
            png.unlink(missing_ok=True)

    return output_pdf


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assemble individual card PNGs from the cards folder into a deck PDF."
    )
    parser.add_argument(
        "--event-name",
        required=True,
        help="Event name (used to derive folder and output file names).",
    )
    parser.add_argument(
        "--cards-dir",
        default=None,
        help="Directory containing individual card PNGs (default: cards/<event_slug>).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for generated PDFs (default: output/<event_slug>).",
    )
    parser.add_argument(
        "--keep-svgs",
        action="store_true",
        help="Keep intermediate SVG page files.",
    )
    parser.add_argument(
        "--cleanup-pngs",
        action="store_true",
        help="Remove page PNGs after PDF assembly.",
    )

    args = parser.parse_args()
    event_name = args.event_name
    event_slug = slugify(event_name)

    base_dir = Path(__file__).resolve().parent
    cards_dir = Path(args.cards_dir) if args.cards_dir else base_dir / "cards" / event_slug
    output_dir = Path(args.output_dir) if args.output_dir else base_dir / "output" / event_slug

    if not cards_dir.exists():
        raise FileNotFoundError(f"Cards directory not found: {cards_dir}")

    print(f"Event: {event_name}")
    print(f"Cards dir: {cards_dir}")
    print(f"Output dir: {output_dir}")

    generate_deck_pdf(
        cards_dir=cards_dir,
        event_slug=event_slug,
        event_name=event_name,
        output_dir=output_dir,
        keep_svgs=args.keep_svgs,
        keep_pngs=not args.cleanup_pngs,
    )


if __name__ == "__main__":
    main()
