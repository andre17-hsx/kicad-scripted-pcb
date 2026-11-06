---
name: kicad-scripted-pcb
description: >-
  Design a manufacturable PCB in KiCad 10 from Python scripts: schematic and board generated
  from one parts table, octilinear routing, IPC-2221 widths, ground pours, teardrops and a clean
  schematic layout; verified with ERC, DRC, schematic-PCB parity and a routing checker; exported
  as Gerbers, drill, BOM, PDF and 3D renders for JLCPCB/PCBWay. Use it whenever the user wants a
  circuit, wiring diagram or set of modules turned into a schematic or PCB, asks for KiCad files,
  Gerbers, a "placa", "esquema" or "board layout", or wants an existing board revised.
---

# Scripted PCB design with KiCad 10

Build the schematic and the board as Python generators instead of clicking in the GUI. A script
is reproducible and easy to revise ("move the connectors", "make a v2"), and KiCad's own checkers
prove the result. The bundled example (`examples/esp32-fan-box/`) was built this way and passes
ERC 0, DRC 0, parity 0 and 0 routing problems.

## What is in this skill

| Path | Use |
|---|---|
| `scripts/kisexpr.py` | Read/write KiCad S-expressions; pull stock symbols (flattens `extends`) |
| `scripts/check_routing.py` | Checks what DRC does not: octilinear tracks, no 90° corners, no acute angles, widths per net class |
| `templates/parts.py` | Single parts table (ref → value, footprint) + deterministic UUIDs shared by schematic and board |
| `templates/gen_sch_template.py` | Schematic generator: blocks, symbols, wires, labels, junctions, notes, title block |
| `templates/gen_pcb_template.py` | Board generator: outline, footprints, routing, pours, stitching, silkscreen, teardrops, schematic link |
| `examples/esp32-fan-box/` | Real project: one circuit, three board versions (v1, v2, v3) |
| `references/` | Routing rules, KiCad 10 quirks, schematic layout, ordering checklist |

## Workflow

### 1. Pin down the requirements before drawing anything

Ask only what changes the design, and suggest a default for each:
- Fabricated 2-layer board or perfboard; through-hole or SMD (hand soldering → THT).
- Maximum size, mounting holes, which edges the connectors go on.
- How modules attach (female sockets, pins, wires) and which modules stay off-board.
- Connector type and pitch (e.g. 5.08 mm screw terminals).

Anything you cannot know exactly (row spacing of a module, hole spacing of a breakout board, a
transistor's pinout) goes into a **"measure before ordering"** list that the user confirms with
calipers. Keep it parameterized in the script (`TPS_DX`, `±7.62`…) so a correction is one number.

### 2. One parts table for everything

Copy `templates/parts.py` and fill `PARTS = {ref: (value, footprint)}`. Both generators read it,
and `sym_uuid(ref)` gives each symbol a fixed UUID: the footprint path `/<uuid>` is what links a
footprint to its symbol, so parity holds on every regeneration.

### 3. Schematic first (`templates/gen_sch_template.py`)

Generate the schematic before the board: the board copies Datasheet and Description from it.
- Divide the sheet into functional **blocks** (power, MCU, each peripheral, mechanical, notes),
  each a dashed rectangle with a numbered title; signal flows left to right inside a block.
- Use power symbols for rails (`power:GND`, `+3V3`, `VCC` with the value set to the net name) and
  global labels for signals that cross blocks. Put a `PWR_FLAG` on every rail that only comes in
  through a connector, but never on a net already driven by a `power_out` pin.
- Mark unused module pins with no-connect flags. Custom modules get their own symbol with pins in
  physical order.
- Keep pins on the 2.54 mm grid and labels on 1.27 mm; split wires at every pin/label point and
  add junctions where three or more meet (the template does both).
- Add short notes that explain *why* (protection, polarity, first power-up test) and fill the
  title block (title, revision, date, comments).

Run ERC until it reports 0 errors and 0 warnings. ERC catches drawing mistakes — e.g. a connector
pin off by one grid step shorting GND and VBAT — before they reach copper.

### 4. Placement: zones, not leftovers

Place by **function**, each group next to the connector it serves: power input chain near the
battery/switch terminals, regulator caps hugging the regulator, MCU in the middle, each driver
channel above its own terminal block, sensitive signals away from switching parts.

When the outline or the connector positions change, **redistribute everything** into the new
space. Moving only the connectors leaves one side crowded and the other empty — users notice
immediately. Always look at the top render before delivering and judge the balance.

Prefer parts lying flat; stand a resistor up only when space really forces it, and say so.

### 5. Routing rules (`references/routing-rules.md`)

- Tracks at 0/45/90° only. Write each route as a list of corner points and pass it through
  `chamfer()`, which turns every 90° corner into a 45° cut. A sharper turn is an error.
- Branches join as 90° T-junctions on the straight part of a track, never as acute Y's.
- A track that must reach a pad ends exactly on the pad centre. Never let a chamfer land on a pad
  (the connection is lost); put the corner away from the pad instead.
- IPC-2221 widths, 1 oz outer copper: power 1.0 mm, ~0.5 A rails 0.8 mm, signals 0.3 mm;
  clearance 0.25 mm.
- GND pour on both layers with thermal reliefs, stitched with vias on a 5 mm grid where free.
- Teardrops on every pad with a track (`SetTeardropsEnabled(True)`): KiCad builds them on refill.
- Use the bottom layer to cross, not vias, for a 2-layer THT board.

### 6. Silkscreen and presentation

- Reference designators inside each part's body (visible while assembling); electrolytics just
  outside the circle; hide the references of connectors and modules and label them instead.
- Every terminal gets its name on both layers (above the screw on top, below the pad on bottom).
- Mark module orientation (USB side, input/output, square pad = pin 1) and a title + version
  on the bottom layer.

### 7. Verify, then export

Run from the project folder with KiCad's bundled Python (`<KiCad>/bin/python.exe` on Windows):

```
python gen_sch.py
python gen_pcb.py
kicad-cli sch erc --severity-all <name>.kicad_sch
kicad-cli pcb drc --refill-zones --save-board --schematic-parity --severity-all <name>.kicad_pcb
python check_routing.py <name>.kicad_pcb --power VBAT,+3V3
```

All must report zero. Then export:

```
kicad-cli pcb export gerbers -o fab/gerber/ --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts <name>.kicad_pcb
kicad-cli pcb export drill -o fab/gerber/ <name>.kicad_pcb
kicad-cli sch export pdf -o <name>.pdf <name>.kicad_sch
kicad-cli pcb render --side top -w 1600 -h 1000 -o render_top.png <name>.kicad_pcb
```

Zip `fab/gerber/` for the fab house, write `BOM.csv`, and a README with the verification table,
the "measure before ordering" list, assembly order (lowest to tallest) and a first power-up test
without the expensive module plugged in.

### 8. Versions and revisions

A new layout goes in a new folder (`v2/`, `v3/`) with its own generator. Never overwrite a version
the user approved: hash its files before and compare after. When several versions share one
schematic generator, give it a flag (`--v2`) and confirm the default output stays byte-identical.

## KiCad 10 quirks that cost time

Read `references/kicad10-quirks.md` before the first run. The short version:
- `ZONE_FILLER` from Python can crash: fill zones with `kicad-cli pcb drc --refill-zones --save-board`.
- Custom footprints: write the `.kicad_mod` as text, then `FootprintLoad` it from the project
  library, and add an `fp-lib-table` with `${KIPRJMOD}`.
- Nets that come from local labels are named `/NAME` in the board.
- Fields of a symbol rotated 90° flip their justification.
- Parity also compares Datasheet and Description: copy them from the schematic into each footprint.

## Example

`examples/esp32-fan-box/` is a real design: ESP32-S3 module in a socket, passive bus sniffer,
two transistor-switched fans and a buck-boost module. `gen_sch.py [--v2|--v3]` and
`gen_pcb.py`, `gen_pcb_v2.py`, `gen_pcb_v3.py` produce three board versions (70 × 50 mm, all
connectors in one row at 96 × 53 mm, and the regulator module mounted on the board). Read it for
patterns; copy the templates for a new design. Comments in the example are in Spanish.
