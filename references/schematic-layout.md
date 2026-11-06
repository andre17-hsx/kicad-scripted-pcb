# Professional schematic layout

## Sheet

- A4 landscape for small boards; fill the title block (title, revision, date, three comments:
  what it is and the board size, how it was generated, how it was verified).
- Split into numbered dashed blocks: 1 power, 2 MCU, 3+ each peripheral, a mechanical block
  (mounting holes, board size, stack-up) and a notes block clear of the title block.

## Inside a block

- Signal and power flow left to right; ground symbols point down, supply symbols up.
- Connector symbols at the edge where the wire enters; capacitors hang from the rail they decouple.
- Values and references horizontal and readable, never overlapping wires or pin numbers.
- One short explanatory note per non-obvious part (why a series resistor, why a Schottky diode,
  input voltage range of a regulator).

## Connectivity hygiene

- Power symbols for rails, global labels between blocks, local labels for nets inside a block.
- `PWR_FLAG` on rails that only enter through a connector; none on a `power_out`-driven net.
- No-connect flag on every unused pin of a module.
- Junction dots wherever three or more wires meet; no four-way junctions.

## Custom module symbols

Draw pins in the same order as the physical module (left row top to bottom, right row top to
bottom), name them as on the module silkscreen, hide pin numbers if they are not meaningful, and
set the footprint, datasheet and description fields in the symbol.
