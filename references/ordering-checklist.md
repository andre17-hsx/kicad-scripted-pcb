# Before ordering: checklist to hand the user

## Measure with calipers (anything estimated from a photo or a generic datasheet)

- Row spacing of socketed modules (e.g. 15.24 mm for many ESP32 mini boards).
- Hole spacing of breakout modules mounted on pins (regulators, sensors).
- Electrolytic diameter and lead pitch (a Ø10 mm cap will not fit a Ø8 mm footprint).
- Terminal block pitch (5.08 mm vs 3.5 mm are not interchangeable).
- Transistor pinout (2N2222 is E-B-C, some P2N2222A are C-B-E).
- PTC fuse lead spacing.

## Module settings

- Output-voltage jumpers on regulator modules set correctly before plugging in the MCU.
- Enable pins: note whether the module pulls them up itself.

## Order (JLCPCB / PCBWay)

Upload the Gerber zip; 2 layers, 1.6 mm, HASL, 1 oz copper. Boards up to 100 × 100 mm get the
cheapest price. THT parts need no assembly service.

## Assembly order

Lowest to tallest: flat resistors and diodes → ceramic caps, PTCs, transistors → sockets,
electrolytics (long lead to +) → terminal blocks with the wire entry toward the edge.

## First power-up

1. Continuity: no short between each supply rail and GND.
2. Power the board without the MCU module; measure the regulated rail at the module socket.
3. Switch off, plug the module in, switch on again.
