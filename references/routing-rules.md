# Routing rules

These are the rules `check_routing.py` and KiCad's DRC enforce together.

## Geometry

| Rule | Why |
|---|---|
| Segments at 0°, 45° or 90° only | Standard octilinear routing; looks professional and is predictable |
| No 90° corners (cut with a 45° segment) | Avoids acid traps in etching and current crowding |
| No acute angle between tracks of one node | Acute wedges trap etchant and over-etch |
| T-junctions at 90° are fine | The branch meets a straight track; there is no wedge |
| Track ends on a pad centre | KiCad connects a track to a pad only if its end point lies in the pad |

How to route a net: list corner points as if you were drawing with right angles and 45° diagonals,
then pass the list through `chamfer()` (see `templates/gen_pcb_template.py`). `chamfer()` refuses
a turn sharper than 90°, so a mistake fails loudly.

Diagonal segments must be exact 45°: `dx == dy`. When the target is a pad, compute the diagonal
start from the pad centre (`(xpad + d, ypad - d)`) rather than guessing.

## Widths and clearance (IPC-2221, 1 oz outer copper, 10 °C rise)

| Class | Width | Typical nets |
|---|---|---|
| Power (≤ 2 A) | 1.0 mm | battery, protected battery, fan supply |
| Medium (≤ 0.5 A) | 0.8 mm | 3V3 rail, motor/fan return |
| Signal | 0.3 mm | GPIO, data, clock |

Clearance 0.25 mm (IPC-2221 asks for 0.1 mm below 15 V; 0.25 mm gives margin for cheap fabs).
Copper to board edge 0.5 mm.

## Planes and finishing

- GND zone on both copper layers, clearance 0.4 mm, min width 0.3 mm, thermal reliefs
  (gap 0.5 mm, spoke 0.6 mm) so THT ground pads can be hand soldered.
- Stitching vias (0.8/0.4 mm) on a 5 mm grid, only where at least 1.6 mm from every pad and track.
- Teardrops on every pad that has a track, curved.

## Crossing nets on a 2-layer board

Keep one layer mostly for vertical/long runs of one kind and use the other to cross. A power trunk
can run on the bottom layer under a module (between its pins), which keeps the top free. Avoid
vias for power on hand-made THT boards; a THT pad already connects both layers.
