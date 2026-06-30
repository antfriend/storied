#!/usr/bin/env python3
"""Render a game's Markdown rules into a clean Letter-size instructions PDF.

Markdown -> HTML (python-markdown, tables+fenced code) -> PDF (fpdf2, write_html),
using system Arial as a Unicode font so arrows, em-dashes, +/-, and middots render.
No external binaries required.
"""
from __future__ import annotations

import re
from pathlib import Path

import markdown
from fpdf import FPDF
from fpdf.fonts import FontFace


def _flatten_table_cells(html: str) -> str:
    """fpdf2's write_html rejects inline tags nested in <td>/<th>; keep the text only."""
    def strip(m: re.Match) -> str:
        tag = m.group(1)
        open_tag = re.match(rf"<{tag}[^>]*>", m.group(0)).group(0)
        body = m.group(0)[len(open_tag):-len(f"</{tag}>")]
        body = re.sub(r"</?(strong|em|code|a|b|i)[^>]*>", "", body)
        return open_tag + body + f"</{tag}>"

    return re.sub(r"<(td|th)[^>]*>.*?</\1>", strip, html, flags=re.S)

_F = r"C:\Windows\Fonts"
FONTS = {
    "": rf"{_F}\arial.ttf",
    "B": rf"{_F}\arialbd.ttf",
    "I": rf"{_F}\ariali.ttf",
    "BI": rf"{_F}\arialbi.ttf",
}


class Booklet(FPDF):
    def __init__(self, title: str, accent: tuple[int, int, int]):
        super().__init__(format="Letter")
        self._title = title
        self._accent = accent

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Arial", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"{self._title}  ·  {self.page_no()}", align="C")


def render_markdown_pdf(md_path: Path, pdf_path: Path, title: str,
                        accent: tuple[int, int, int] = (34, 139, 96)) -> Path:
    md_text = Path(md_path).read_text(encoding="utf-8")
    html = markdown.markdown(
        md_text, extensions=["tables", "fenced_code", "sane_lists"]
    )
    html = _flatten_table_cells(html)

    pdf = Booklet(title, accent)
    for style, fp in FONTS.items():
        pdf.add_font("Arial", style, fp)
    pdf.set_margins(16, 16, 16)
    pdf.set_auto_page_break(True, margin=16)
    pdf.add_page()
    pdf.set_font("Arial", size=10.5)
    pdf.set_text_color(28, 28, 32)

    r, g, b = accent
    pdf.write_html(
        html,
        tag_styles={
            "h1": FontFace(color=(r, g, b), size_pt=22, emphasis="BOLD"),
            "h2": FontFace(color=(r, g, b), size_pt=15, emphasis="BOLD"),
            "h3": FontFace(color=(60, 60, 66), size_pt=12, emphasis="BOLD"),
        },
        font_family="Arial",
        table_line_separators=True,
    )
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(pdf_path))
    return pdf_path


if __name__ == "__main__":
    import sys

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".pdf")
    render_markdown_pdf(src, dst, title=src.stem)
    print(f"Wrote {dst}")
