#!/usr/bin/env python3
"""Generate a 3D-printable organizer box + lid for the game *Pulse*.

A single-color, rounded-corner tray that stands the five card types up in
their own little stacks (Story / Character / Part / Feeling / Reference) and
gives every token a pocket (Pulse / Drift / Swing / Baton / Story Marker).
A telescoping lid drops over the top and carries the game's identity in
**raised relief**: the word PULSE over a heartbeat waveform (the same motif
engraved on the Pulse token).

Everything is designed for FDM without supports: chunky walls, generous
finger-scoops, big bold lettering, no fragile overhangs. Units are mm.

    cd games/pulse/box && python make_box.py

Outputs: pulse-box.3mf (base + lid in one file), plus pulse-box-base.stl,
pulse-box-lid.stl, and a top-view layout diagram (box-layout.png).

Needs: numpy trimesh shapely manifold3d matplotlib lxml
"""
import math
import numpy as np
import trimesh
from trimesh.creation import extrude_polygon, cylinder
from shapely.geometry import box as sbox, LineString
from shapely.ops import unary_union

# ---------------------------------------------------------------------------
# Parameters (mm)
# ---------------------------------------------------------------------------
T_WALL   = 2.6     # outer wall thickness
T_FLOOR  = 2.4     # tray floor thickness
T_DIV    = 2.4     # internal divider thickness
R_CORNER = 8.0     # rounded outer corner radius
R_POCKET = 2.0     # rounded pocket corner radius
H_INT    = 66.0    # interior height (63 mm card stands, +3 clearance)
LY       = 92.0    # interior length  (88 mm card lies along its long edge, +4)
CLEAR    = 0.5     # lid-to-base slide clearance (per side)

# Card compartments: cards stand on their long (88 mm) edge, 63 mm tall,
# stacked along X.  Width sized for a comfortable un-/lightly-sleeved fit.
CARD_SPECS = [
    ("Story",   9.0),   # 6 cards
    ("Char",    9.0),   # 5 cards
    ("Part",   11.0),   # 8 cards
    ("Feeling",34.0),   # 32 cards  (the big draw deck)
    ("Ref",    10.0),   # 6 cards
]

H_BASE = T_FLOOR + H_INT


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def rrect(x0, y0, x1, y1, r):
    """Axis-aligned rounded rectangle as a shapely polygon."""
    r = min(r, (x1 - x0) / 2 - 1e-3, (y1 - y0) / 2 - 1e-3)
    return sbox(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, join_style=1, quad_segs=16)


def prism(poly, z0, z1):
    """Extrude a shapely polygon between two z heights."""
    m = extrude_polygon(poly.buffer(0), height=z1 - z0)
    m.apply_translation((0, 0, z0))
    return m


def extrude_geom(geom, h, z0=0.0):
    """Extrude a shapely Polygon or MultiPolygon (with holes) to a mesh."""
    polys = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    parts = []
    for p in polys:
        if p.is_empty or p.area < 1e-6:
            continue
        m = extrude_polygon(p, height=h)
        m.apply_translation((0, 0, z0))
        parts.append(m)
    return trimesh.util.concatenate(parts) if parts else None


def scoop(xc, y_edge, x_len, r):
    """A horizontal half-cylinder cutter that notches a wall top for fingers.

    Axis runs along X (the notch width); the round profile bites down from the
    rim at z = H_BASE so only the upper part of the wall is removed.
    """
    c = cylinder(radius=r, height=x_len, sections=48)
    c.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    c.apply_translation((xc, y_edge, H_BASE))
    return c


# ---------------------------------------------------------------------------
# Compartment layout  -> list of pockets {name, x0,x1,y0,y1}
# ---------------------------------------------------------------------------
def build_layout():
    pockets = []

    # --- card zone: full-length stacks side by side along X ---
    x = 0.0
    for name, w in CARD_SPECS:
        pockets.append(dict(name=name, kind="card", x0=x, x1=x + w, y0=0.0, y1=LY))
        x += w + T_DIV
    card_end = x - T_DIV

    # --- token zone: two columns after a divider ---
    tx0 = card_end + T_DIV
    colA_w, colB_w = 27.0, 24.0
    Ax0, Ax1 = tx0, tx0 + colA_w
    Bx0, Bx1 = Ax1 + T_DIV, Ax1 + T_DIV + colB_w
    WX = Bx1  # interior width falls out of the layout

    # column A (27 wide): Drift cubes / Pulse discs / Swing stars, split along Y
    availA = LY - 2 * T_DIV
    dh, ph, sh = 30.0, 25.0, availA - 30.0 - 25.0   # swing takes the remainder
    y = 0.0
    for name, h in (("Drift", dh), ("Pulse", ph), ("Swing", sh)):
        pockets.append(dict(name=name, kind="token", x0=Ax0, x1=Ax1, y0=y, y1=y + h))
        y += h + T_DIV

    # column B (24 wide): long Baton channel + Story Marker pocket
    bat_h = 65.0
    pockets.append(dict(name="Baton",  kind="token", x0=Bx0, x1=Bx1, y0=0.0,          y1=bat_h))
    pockets.append(dict(name="Marker", kind="token", x0=Bx0, x1=Bx1, y0=bat_h + T_DIV, y1=LY))

    return pockets, WX


# ---------------------------------------------------------------------------
# Base tray
# ---------------------------------------------------------------------------
def make_base(pockets, WX):
    outer = rrect(-T_WALL, -T_WALL, WX + T_WALL, LY + T_WALL, R_CORNER)
    body = prism(outer, 0.0, H_BASE)

    # carve every pocket, leaving walls + dividers + floor
    cavities, cutters = [], []
    for p in pockets:
        cav = rrect(p["x0"], p["y0"], p["x1"], p["y1"], R_POCKET)
        cavities.append(prism(cav, T_FLOOR, H_BASE + 1.0))

        # finger scoops on both Y-edges of each pocket
        xc = (p["x0"] + p["x1"]) / 2
        xlen = (p["x1"] - p["x0"]) * 0.62
        r = min(11.0, (p["y1"] - p["y0"]) / 2 - 1.0)
        if r > 3.0:
            cutters.append(scoop(xc, p["y0"], xlen, r))
            cutters.append(scoop(xc, p["y1"], xlen, r))

    body = trimesh.boolean.difference([body] + cavities)
    body = trimesh.boolean.difference([body] + cutters)
    return body


# ---------------------------------------------------------------------------
# Lid  (telescoping cap with raised-relief branding)
# ---------------------------------------------------------------------------
def letters_to_geom(text, font_size, weight="bold"):
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fp = FontProperties(family="DejaVu Sans", weight=weight)
    tp = TextPath((0, 0), text, size=font_size, prop=fp)
    loops = [np.asarray(poly) for poly in tp.to_polygons() if len(poly) >= 3]
    # even-odd fill via symmetric difference => letter holes (P,U,R,S,E) resolve
    geom = None
    for lp in loops:
        poly = sbox(0, 0, 1, 1)  # placeholder to get a Polygon type
        from shapely.geometry import Polygon
        poly = Polygon(lp).buffer(0)
        geom = poly if geom is None else geom.symmetric_difference(poly)
    # centre on origin
    minx, miny, maxx, maxy = geom.bounds
    from shapely.affinity import translate
    geom = translate(geom, -(minx + maxx) / 2, -(miny + maxy) / 2)
    return geom


def heartbeat_line(width, amp):
    """A stylised ECG/heartbeat polyline, centred on origin, buffered to a
    printable ribbon.  Echoes the Pulse token's engraved pulse-line."""
    # normalised control points across [-0.5,0.5] in x, [-1,1]-ish in y
    pts = [(-0.50, 0.0), (-0.30, 0.0), (-0.22, 0.15), (-0.14, -0.10),
           (-0.06, 0.0), (0.00, 0.0), (0.04, 0.28), (0.10, -1.00),
           (0.16, 0.60), (0.22, 0.0), (0.30, 0.0), (0.34, 0.12),
           (0.40, -0.10), (0.46, 0.0), (0.50, 0.0)]
    line = LineString([(x * width, y * amp) for x, y in pts])
    return line.buffer(1.7, cap_style=1, join_style=1)


def make_lid(WX):
    # inner cavity must clear the base's outer rounded rectangle + slide gap
    ix0, iy0 = -T_WALL - CLEAR, -T_WALL - CLEAR
    ix1, iy1 = WX + T_WALL + CLEAR, LY + T_WALL + CLEAR
    inner = rrect(ix0, iy0, ix1, iy1, R_CORNER + CLEAR)
    outer = rrect(ix0 - T_WALL, iy0 - T_WALL, ix1 + T_WALL, iy1 + T_WALL, R_CORNER + CLEAR + T_WALL)

    skirt_h, top_h = 16.0, 2.6
    lid = prism(outer, 0.0, skirt_h + top_h)
    lid = trimesh.boolean.difference([lid, prism(inner, 0.0, skirt_h)])

    top_z = skirt_h + top_h
    cx = (ix0 + ix1) / 2
    cy = (iy0 + iy1) / 2

    reliefs = []

    # PULSE wordmark
    word = letters_to_geom("PULSE", font_size=22)
    from shapely.affinity import translate
    word = translate(word, cx, cy + 12)
    reliefs.append(extrude_geom(word, 1.6, z0=top_z))

    # heartbeat waveform beneath the word
    wave = heartbeat_line(width=WX * 0.82, amp=11.0)
    wave = translate(wave, cx, cy - 12)
    reliefs.append(extrude_geom(wave, 1.6, z0=top_z))

    reliefs = [r for r in reliefs if r is not None]
    return trimesh.boolean.union([lid] + reliefs)


# ---------------------------------------------------------------------------
# Layout diagram (top view)
# ---------------------------------------------------------------------------
def draw_layout(pockets, WX, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle

    counts = {"Story": "×6", "Char": "×5", "Part": "×8", "Feeling": "×32",
              "Ref": "×6", "Drift": "×12", "Pulse": "×7", "Swing": "×3",
              "Baton": "×1", "Marker": "×1"}
    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    ax.add_patch(Rectangle((-T_WALL, -T_WALL), WX + 2 * T_WALL, LY + 2 * T_WALL,
                           fill=False, lw=2))
    for p in pockets:
        w, h = p["x1"] - p["x0"], p["y1"] - p["y0"]
        col = "#d9c14a" if p["kind"] == "card" else "#8fb2c9"
        ax.add_patch(FancyBboxPatch((p["x0"], p["y0"]), w, h,
                     boxstyle="round,pad=0,rounding_size=2",
                     fc=col, ec="#333", lw=1.2, alpha=0.85))
        ax.text(p["x0"] + w / 2, p["y0"] + h / 2,
                f'{p["name"]}\n{counts.get(p["name"],"")}',
                ha="center", va="center", fontsize=8, weight="bold")
    ax.set_xlim(-8, WX + 8)
    ax.set_ylim(-8, LY + 8)
    ax.set_aspect("equal")
    ax.set_title(f"Pulse organizer — interior {WX:.0f} × {LY:.0f} × {H_INT:.0f} mm "
                 f"(cards stand on edge)")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def finalize(name, mesh):
    mesh.merge_vertices()
    if not mesh.is_watertight:
        mesh.fill_holes()
    mesh.fix_normals()
    mesh.export(f"{name}.stl")
    wt = "watertight" if mesh.is_watertight else "NOT watertight"
    print(f"  {name+'.stl':22s} {len(mesh.faces):7d} faces  {wt}")
    return mesh


if __name__ == "__main__":
    pockets, WX = build_layout()
    print(f"Pulse box: interior {WX:.1f} × {LY:.1f} × {H_INT:.1f} mm | "
          f"outer {WX+2*T_WALL:.1f} × {LY+2*T_WALL:.1f} × {H_BASE:.1f} mm")
    print("Building base tray ...")
    base = finalize("pulse-box-base", make_base(pockets, WX))
    print("Building lid ...")
    lid = finalize("pulse-box-lid", make_lid(WX))

    # combined 3mf: base + lid, lid parked beside the base for a clean plate
    scene = trimesh.Scene()
    scene.add_geometry(base, node_name="pulse-box-base")
    lid_placed = lid.copy()
    lid_placed.apply_translation((WX + 30, 0, 0))
    scene.add_geometry(lid_placed, node_name="pulse-box-lid")
    scene.export("pulse-box.3mf")
    print("  pulse-box.3mf          (base + lid)")

    draw_layout(pockets, WX, "box-layout.png")
    print("  box-layout.png         (top-view diagram)")
    print("Done.")
