# Cellink Neo

Verified protocol revision: **Cellink Neo firmware 1.52**. This model uses the original `43 06` family; Neo+/PowerCell 8 use `@@`. Advertisement shape `CN6-XXXX`, returned model `Neo 6`, firmware integer 152. `Neo 6` is the Bluetooth identity string, not the product name. Other Neo models/firmware are not established by this map.

## Transport

Service `FFF0`, response `FFF1` (read+notify), writer `FFF2` (write without response), using Bluetooth base UUID expansion: `0000xxxx-0000-1000-8000-00805f9b34fb`. Subscribe before identity `43 06 00 52 17`; request status `43 06 00 51 14` after matching model/firmware. Outgoing trailer is XOR; incoming checksum is unverified. Additional service `FFFA`/characteristics `FFFB`–`FFFE` have unknown purposes.

Reply header `43 06`, payload length at offset 2, command at 3, total length payload+5. Reassemble split/coalesced notifications. Identity `52`: BE16 firmware at 4–5, six ASCII model bytes at 10–15. `71` means connection-ready. The [shared legacy map](blackvue-legacy.md) supplies source context; this Neo's replies establish its classic branch. Other Neo firmware requires a separate layout check.

## Firmware 1.52 status map

Zero-based complete-frame offsets; multibyte integers big-endian. Command `51` requires at least 18 payload bytes.

| Offset | Field | Decode |
| --- | --- | --- |
| 4 | Percent | Byte−100 |
| 5–6 / 7–8 | Runtime / time to full | BE16 minutes |
| 9 | Temperature | Byte ≥100 gives byte−100°C; otherwise 15−byte, source-derived negative branch |
| 10 / 11 / 12 | Battery/input/output voltage | Byte/10 V |
| 14–15 / 16–17 | Input/output current | BE16/1000 A |
| 18–19 | Configured capacity | BE16 mAh |
| 20 | State | Low nibble; observed 1 Charging |

Watts are calculated, not reported. Other legacy state mappings are source-derived. Neo-specific capacity/beep/parking-sustained/reset commands are not yet specified; BlackVue settings opcodes must not be assumed compatible from a shared status layout.

Zero reported runtime with no output load is not an empty-battery indicator. Configured capacity is editable, not measured health. Other firmware and complete protection-state meanings remain unknown. [Synthetic examples](../examples/vectors.json) exercise the layout.
