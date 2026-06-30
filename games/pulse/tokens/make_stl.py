#!/usr/bin/env python3
"""Generate 3D-printable STL files for the Pulse tokens & accessories.

Builds manifold solids from the 2D SVG prototypes in this folder (metronome
excluded). Units are millimetres. Run:

    cd games/pulse/tokens && python make_stl.py

Outputs: pulse-token.stl, drift-token.stl, swing-token.stl, baton.stl,
story-marker.stl  (+ a combined all-tokens.stl plate for preview).
"""
import math
import numpy as np
import trimesh
from trimesh.creation import extrude_polygon, cylinder
from shapely.geometry import Polygon, Point
from shapely.geometry.polygon import orient
from shapely.affinity import scale as shp_scale

OUT = {}


def solid(poly, height):
    """Clean a shapely polygon (fix winding / self-touch) then extrude."""
    poly = orient(poly.buffer(0), 1.0)
    return extrude_polygon(poly, height=height)


def emboss(base, relief, base_h, relief_h):
    """Union a base solid with a relief sitting on top of it."""
    relief = relief.copy()
    relief.apply_translation((0, 0, base_h))
    u = trimesh.boolean.union([base, relief])
    return u


# ----------------------------------------------------------------------------
# 1. PULSE TOKEN  — 20 mm disc, raised heart relief, recessed pulse-line groove
# ----------------------------------------------------------------------------
def make_pulse():
    R, H = 10.0, 3.0
    disc = cylinder(radius=R, height=H, sections=96)
    disc.apply_translation((0, 0, H / 2))

    # heart as a parametric polygon, scaled to ~13 mm wide
    t = np.linspace(0, 2 * math.pi, 161)[:-1]
    hx = 16 * np.sin(t) ** 3
    hy = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    heart = Polygon(np.column_stack([hx, hy]))
    # normalise to a target width of 13 mm
    minx, miny, maxx, maxy = heart.bounds
    s = 13.0 / (maxx - minx)
    heart = shp_scale(heart, xfact=s, yfact=s, origin=(0, 0))
    heart_solid = solid(heart, 1.4)

    token = emboss(disc, heart_solid, H, 1.4)

    # recessed pulse-line groove cut across the heart face
    pts = [(-6, 0), (-2, 0), (0, 3.5), (2.5, -3.5), (4, 0), (7, 0)]
    line = trimesh.load_path(np.array([(x, y, 0) for x, y in pts]))
    groove = line.copy()
    # build groove as a swept box-ish channel: small cylinders along the path
    cutters = []
    poly = np.array(pts)
    dense = []
    for i in range(len(poly) - 1):
        for f in np.linspace(0, 1, 14):
            dense.append(poly[i] * (1 - f) + poly[i + 1] * f)
    for (x, y) in dense:
        c = cylinder(radius=0.55, height=1.2, sections=12)
        c.apply_translation((x, y, H + 1.4 - 0.4))
        cutters.append(c)
    cut = trimesh.boolean.union(cutters)
    token = trimesh.boolean.difference([token, cut])
    return token


# ----------------------------------------------------------------------------
# 2. DRIFT TOKEN — 12 mm cube, engraved tilde on top
# ----------------------------------------------------------------------------
def make_drift():
    S = 12.0
    cube = trimesh.creation.box(extents=(S, S, S))
    cube.apply_translation((0, 0, S / 2))
    # engrave a tilde groove on the top face
    cutters = []
    for f in np.linspace(0, 1, 40):
        x = (f - 0.5) * 8
        y = 2.2 * math.sin(f * 2 * math.pi)
        c = cylinder(radius=0.6, height=2.0, sections=12)
        c.apply_translation((x, y, S - 0.6))
        cutters.append(c)
    cut = trimesh.util.concatenate(cutters)
    return trimesh.boolean.difference([cube, cut])


# ----------------------------------------------------------------------------
# 3. SWING TOKEN — 22 mm 5-point star, faceted peak, base plate for strength
# ----------------------------------------------------------------------------
def make_swing():
    Rout, Rin = 11.0, 4.6
    pts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        r = Rout if i % 2 == 0 else Rin
        pts.append((r * math.cos(ang), r * math.sin(ang)))
    star = Polygon(pts)
    base = solid(star, 2.2)                             # sturdy flat base
    # raised faceted middle: a smaller star pitched up
    star_small = shp_scale(star, 0.62, 0.62, origin=(0, 0))
    peak = solid(star_small, 1.6)
    return emboss(base, peak, 2.2, 1.6)


# ----------------------------------------------------------------------------
# 4. BATON — 60 mm shaft, tip knob, integrated knurled era dial
# ----------------------------------------------------------------------------
def make_baton():
    parts = []
    shaft = cylinder(radius=4.0, height=52, sections=48)
    shaft.apply_translation((0, 0, 26))
    parts.append(shaft)

    knob = trimesh.creation.icosphere(subdivisions=3, radius=6.0)
    knob.apply_translation((0, 0, 58))
    parts.append(knob)

    body = trimesh.boolean.union(parts)

    # era dial: a knurled wheel through the shaft at z=20
    dial = cylinder(radius=8.0, height=5.0, sections=10)  # 10-sided => 0-9 facets
    dial.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    dial.apply_translation((0, 0, 20))
    body = trimesh.boolean.union([body, dial])

    # grip rings near the base (engraved)
    cutters = []
    for zz in (8, 11, 14):
        ring = cylinder(radius=4.3, height=0.8, sections=48)
        inner = cylinder(radius=3.4, height=1.2, sections=48)
        groove = trimesh.boolean.difference([ring, inner])
        groove.apply_translation((0, 0, zz))
        cutters.append(groove)
    cut = trimesh.util.concatenate(cutters)
    body = trimesh.boolean.difference([body, cut])
    return body


# ----------------------------------------------------------------------------
# 4b. BARE BATON — no integrated dial; a flat seat to glue on a real d10
# ----------------------------------------------------------------------------
def make_baton_bare():
    shaft = cylinder(radius=4.0, height=52, sections=48)
    shaft.apply_translation((0, 0, 26))
    knob = trimesh.creation.icosphere(subdivisions=3, radius=6.0)
    knob.apply_translation((0, 0, 58))
    body = trimesh.boolean.union([shaft, knob])

    # flat circular gluing pad for the d10, facing +Y at mid-shaft
    seat = cylinder(radius=5.0, height=2.0, sections=48)
    seat.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    seat.apply_translation((0, 4.0, 20))   # protrudes from the shaft, flat outer face
    body = trimesh.boolean.union([body, seat])

    # grip rings near the base (engraved) — same as the dialed baton
    cutters = []
    for zz in (8, 11, 14):
        ring = cylinder(radius=4.3, height=0.8, sections=48)
        inner = cylinder(radius=3.4, height=1.2, sections=48)
        groove = trimesh.boolean.difference([ring, inner])
        groove.apply_translation((0, 0, zz))
        cutters.append(groove)
    cut = trimesh.util.concatenate(cutters)
    return trimesh.boolean.difference([body, cut])


# ----------------------------------------------------------------------------
# 5. STORY MARKER — classic pawn, body of revolution, raised star on the head
# ----------------------------------------------------------------------------
def make_marker():
    # profile (radius, z) revolved around the z-axis
    profile = [
        (0.0, 0.0),
        (11.0, 0.0),
        (11.0, 3.0),
        (6.0, 5.0),
        (4.0, 9.0),
        (3.2, 16.0),
        (4.2, 20.0),
        (3.0, 22.0),     # neck
        (5.5, 24.0),     # shoulder
        (5.6, 25.0),
        (4.8, 26.5),
        (0.0, 26.5),
    ]
    # close profile back down the axis
    poly = Polygon(profile + [(0.0, 0.0)])
    pawn = trimesh.creation.revolve(np.array(profile), sections=64)

    # head is a sphere on top for a clean pawn silhouette
    head = trimesh.creation.icosphere(subdivisions=3, radius=6.5)
    head.apply_translation((0, 0, 30))
    body = trimesh.boolean.union([pawn, head])

    # raised star emblem on the front of the head
    Rout, Rin = 4.0, 1.7
    spts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        r = Rout if i % 2 == 0 else Rin
        spts.append((r * math.cos(ang), r * math.sin(ang)))
    star = solid(Polygon(spts), 2.5)
    # orient star to face +Y and sit on the head surface
    star.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]))
    star.apply_translation((0, 4.5, 31))
    body = trimesh.boolean.union([body, star])
    return body


def finalize(name, mesh):
    mesh.merge_vertices()
    if not mesh.is_watertight:
        mesh.fill_holes()
    mesh.fix_normals()
    path = f"{name}.stl"
    mesh.export(path)
    wt = "watertight" if mesh.is_watertight else "NOT watertight"
    print(f"  {path:22s} {len(mesh.faces):6d} faces  {wt}")
    OUT[name] = mesh


if __name__ == "__main__":
    print("Building Pulse token STLs (mm):")
    finalize("pulse-token", make_pulse())
    finalize("drift-token", make_drift())
    finalize("swing-token", make_swing())
    finalize("baton", make_baton())
    finalize("baton-bare", make_baton_bare())
    finalize("story-marker", make_marker())

    # combined preview plate (one of each piece; dialed baton, not the bare one)
    plate = []
    plate_names = ["pulse-token", "drift-token", "swing-token", "baton", "story-marker"]
    xs = [-40, -15, 5, 25, 50]
    for x, n in zip(xs, plate_names):
        mm = OUT[n].copy()
        mm.apply_translation((x, 0, 0))
        plate.append(mm)
    trimesh.util.concatenate(plate).export("all-tokens.stl")
    print("  all-tokens.stl         (combined preview plate)")
    print("Done.")
