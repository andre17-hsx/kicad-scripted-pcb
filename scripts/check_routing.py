# Checks track geometry against common routing practice (IPC-2221 / IPC-7351), the things
# KiCad's DRC does not look at:
#   1. Segments only at 0, 45 or 90 degrees (octilinear routing).
#   2. No 90-degree corners: direction changes use two 45-degree segments.
#   3. No acute angle (< 90) between tracks of the same node: it traps etchant.
#   4. Minimum width per class: power nets >= --power-width, everything else >= --signal-width.
# 90-degree T-junctions (a track ending on the middle of another) are accepted.
# Usage (with KiCad's bundled Python):
#   python check_routing.py board.kicad_pcb --power VBAT,+3V3,+5V [--power-width 0.8] [--signal-width 0.3]
# Exit code 0 = no problems, 1 = problems found (usable in CI).
import argparse
import math
import sys
from collections import defaultdict

import pcbnew

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("board")
ap.add_argument("--power", default="", help="comma-separated power net names (a leading '/' is ignored)")
ap.add_argument("--power-width", type=float, default=0.8)
ap.add_argument("--signal-width", type=float, default=0.3)
args = ap.parse_args()
POWER = {n.strip().lstrip("/") for n in args.power.split(",") if n.strip()}
TOL = 0.01    # mm: two endpoints closer than this are the same point
OX, OY = 100.0, 100.0  # board origin offset used by the generators (positions are reported relative to it)

b = pcbnew.LoadBoard(args.board)
segs = []
for t in b.GetTracks():
    if t.GetClass() != "PCB_TRACK":
        continue
    a, e = t.GetStart(), t.GetEnd()
    segs.append((t.GetNetname(), t.GetLayer(), pcbnew.ToMM(t.GetWidth()),
                 (pcbnew.ToMM(a.x), pcbnew.ToMM(a.y)), (pcbnew.ToMM(e.x), pcbnew.ToMM(e.y))))

problems = []


def where(p):
    return "(%.2f, %.2f)" % (p[0] - OX, p[1] - OY)


for n, lay, w, a, e in segs:
    ang = math.degrees(math.atan2(e[1] - a[1], e[0] - a[0])) % 45
    if min(ang, 45 - ang) > 0.6:
        problems.append("not octilinear  %-8s %s -> %s" % (n, where(a), where(e)))
    need = args.power_width if n.lstrip("/") in POWER else args.signal_width
    if w + 1e-6 < need:
        problems.append("width %.2f < %.2f  %-8s %s" % (w, need, n, where(a)))

# directions leaving each node (endpoints, and interior points where another track ends)
nodes = defaultdict(list)
for i, (n, lay, w, a, e) in enumerate(segs):
    for p, q in ((a, e), (e, a)):
        key = (n, lay, round(p[0] / TOL), round(p[1] / TOL))
        nodes[key].append((math.atan2(q[1] - p[1], q[0] - p[0]), i, p))
for i, (n, lay, w, a, e) in enumerate(segs):            # T: endpoint on the interior of another track
    for j, (n2, lay2, w2, a2, e2) in enumerate(segs):
        if i == j or n != n2 or lay != lay2:
            continue
        for p in (a2, e2):
            dx, dy = e[0] - a[0], e[1] - a[1]
            L = dx * dx + dy * dy
            if L == 0:
                continue
            u = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L
            if 0.001 < u < 0.999 and math.hypot(a[0] + u * dx - p[0], a[1] + u * dy - p[1]) < TOL:
                key = (n, lay, round(p[0] / TOL), round(p[1] / TOL))
                for q in (a, e):
                    nodes[key].append((math.atan2(q[1] - p[1], q[0] - p[0]), i, p))

for (n, lay, _, _), dirs in nodes.items():
    dirs = {(round(math.degrees(d), 1), i): (d, p) for d, i, p in dirs}
    items = list(dirs.values())
    if len(items) < 2:
        continue
    p = items[0][1]
    for x in range(len(items)):
        for y in range(x + 1, len(items)):
            diff = abs(math.degrees(items[x][0] - items[y][0])) % 360
            diff = min(diff, 360 - diff)
            if diff < 89.4:
                problems.append("acute angle %.0f  %-8s %s" % (diff, n, where(p)))
            elif diff < 90.6 and len(items) == 2:
                problems.append("90-degree corner  %-8s %s" % (n, where(p)))

print("segments checked:", len(segs))
for s in sorted(set(problems)):
    print("  " + s)
print("problems:", len(set(problems)))
sys.exit(1 if problems else 0)
