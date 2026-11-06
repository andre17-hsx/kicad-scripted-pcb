# KiCad 10 quirks found while scripting

| Symptom | Cause | Fix |
|---|---|---|
| Python crashes when filling zones | `pcbnew.ZONE_FILLER` is unstable from a script | Fill with `kicad-cli pcb drc --refill-zones --save-board` |
| `FootprintLibCreate` returns `None` | API change | Write the `.kicad_mod` as plain text, then `pcbnew.FootprintLoad(libdir, name)` |
| DRC: `lib_footprint_mismatch` | Board copy differs from the library file | Load the footprint from the same file you wrote; regenerate both together |
| Parity: net names differ | Nets from local labels are `/NAME` on the board | Prefix those nets with `/` when creating `NETINFO_ITEM` |
| Parity: Datasheet/Description differ | Parity compares these fields too | Copy them from the parsed schematic into each footprint (`fp.SetField`) |
| Parity: unconnected module pins | KiCad names them `unconnected-(U1-NAME-PadN)` | Give unused pads that exact net name |
| Parity: mounting holes | Holes are excluded from BOM in the schematic | Keep the hole symbols `in_bom no`, footprints from `MountingHole` |
| Field text on a 90°-rotated symbol is mirrored | Justification flips at 90° | Write the field angle as 90 and swap left/right justification |
| Annotation warning | Reference like `C1b` | Use plain numbers (`C8`) |
| ERC: power output conflict | `PWR_FLAG` on a net already driven by a `power_out` pin | Drop the flag on that net |
| Heredoc in bash breaks `\n` inside Python strings | Shell escaping | Write helper scripts to files instead of heredocs |
| Running the v1 generator "to test" rewrites v1 | New UUIDs on every run | Test generators in a temp copy |

## Board coordinates

Footprints placed with `SetOrientationDegrees(90)` rotate counter-clockwise on screen: a pad at
local `(+5, 0)` ends up at `(0, -5)` (above). For rotation 270 it ends at `(0, +5)`. Courtyards
rotate the same way; compute them before placing neighbours.

## Useful commands

```
kicad-cli pcb drc --refill-zones --save-board --schematic-parity --severity-all board.kicad_pcb
kicad-cli sch erc --severity-all board.kicad_sch
kicad-cli pcb render --side top --rotate "-45,0,20" --perspective -w 1600 -h 1100 -o iso.png board.kicad_pcb
kicad-cli sch export svg -o out/ board.kicad_sch
```
