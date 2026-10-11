# Cellink Neo+ family protocol

Evidence: **upstream-source-derived for Neo+ models**. [RobXYZ/cellink2mqtt](sources.md#cellink-neo) documents Neo 8+ validation and a wider model list including `PWC8`. The separate [PowerCell 8 F141 reference](powercell8.md) covers that pack's corroborated status path. Other model/firmware compatibility requires independent confirmation.

This family uses service `FF12`, writer `FF01` and notification characteristic `FF02`, expanded with the Bluetooth base UUID. Subscribe before querying. Replies begin ASCII `@@` (`40 40`), carry command/subcommand/length, and end `0A 0D`; complete reply length is the byte at offset 4 plus 7. Identify/status requests: `40 40 30 00 0A 0D` / `40 40 41 00 0A 0D`. Multibyte measurement fields are little-endian, unlike legacy/ITSC.

The standard status is 75 bytes. Its payload includes settings and a PIN-bearing region at complete-frame offsets 59–60. Unknown response types can contain different private fields, so zeroing those two bytes is not a universal sanitizer. See the [pinned upstream protocol document](https://github.com/RobXYZ/cellink2mqtt/blob/d97ab241aa92d22a00482ecdcddf28e491ad13b5/PROTOCOL.md) for provenance.

The older original-Neo family uses different framing. Keep `@@` and `43 06` decoders separate. [Cellink Neo firmware 1.52](cellink-neo6.md) has its own profile.

## Additional status fields

The [PowerCell 8 map](powercell8.md#complete-frame-status-map) covers the core measurements. The following additional offsets come from the upstream Neo+ reference; these settings/flags remain source-derived on PC8. Offsets are zero-based complete-frame positions, with unsigned little-endian integers unless noted.

| Offset | Bytes | Field |
| --- | --- | --- |
| 15 | 2 | ACC voltage, mV |
| 37 / 38 / 39 | 1 each | R-charging / E-charging / parking sustained mode, 0/1 |
| 40 / 41 / 42 | 1 each | Low voltage / high voltage / high temperature warning, 0/1 |
| 43 | 1 | Vehicle selection: 0=12V, 1=24V |
| 45 / 47 | 2 each | Configured charge current mA / output voltage mV |
| 49 / 51 | 2 each | Minimum / maximum output voltage, mV |
| 53 / 55 | 2 each | Minimum / maximum charge current, mA |
| 57 | 1 | Use vehicle battery, 0/1 |
| 58 | 1 | Voltage selection: 0=low, 1=medium, 2=high |
| 61 / 62 | 1 each | Beep / stop charging at full, 0/1 |
| 63–64 / 69–72 | Reserved | Meaning unknown |
| 65 / 67 | 2 each | Supported / locked settings masks |

Source-derived state byte 44: 0 unused, 1 charging, 2 discharging, 4 full, 8 low voltage, 16 high voltage, 32 high temperature, 64 vehicle-battery mode, 129 cigar-jack charging. Keep raw codes for unknown firmware behavior.

## Other query commands

`40 40 31 00 0A 0D` queries configuration; the upstream app ignores its reply, so its response layout remains unknown. `40 40 47 00 0A 0D` requests extended status when base or expansion capacity is at least 65,000mAh. This extended layout is source-derived and unverified on hardware: each field is four-byte little-endian.

| Offset | Field / units |
| --- | --- |
| 5 / 9 | Input / output voltage, mV |
| 13 / 17 | Input / output current, mA |
| 21 / 25 | ACC / battery voltage, mV |
| 29 / 33 | Configured charging current mA / output voltage mV |
| 37 / 41 | Minimum / maximum output voltage, mV |
| 45 / 49 | Minimum / maximum charging current, mA |

Full extended response length and other fields require further specification. Do not decode a `47` reply as a standard 75-byte `41` reply.

## Configuration protocol

These writes are source-derived, not hardware-verified on PC8 or the original Cellink Neo. Status bytes 65–66 hold the little-endian supported-setting mask, 67–68 the locked-setting mask. Only supported and unlocked settings are eligible. Authentication packet: `40 40 43 3D 02 PP PP 0A 0D`, where `PP PP` is the private two-byte **big-endian** settings password. The reported reply prefix is `40 40 43 3D 02 4F 4B` (`OK`); the full acknowledgement frame remains unspecified.

Write packet: `40 40 43 ID NN [value] 0A 0D`; NN is value length, multibyte write values are **big-endian**, unlike status measurements.

| ID | Setting | Bytes / units | Capability bit |
| --- | --- | --- | --- |
| `31` | Base capacity | 4 / mAh | 4 |
| `32` | Expansion capacity | 4 / mAh | 5 |
| `33` / `34` | E-charging / R-charging | 1 / boolean | 1 / 2 |
| `35` | Parking mode | 1 / boolean | 0 |
| `36` | Vehicle 12/24V selection | 1 / boolean | 3 |
| `37` | Charging current | 2 / mA | 6 |
| `38` | Use main vehicle battery | 1 / boolean | 8 |
| `39` | Voltage selection | 1 / enum 0,1,2 | 9 |
| `3A` | Output voltage | 2 / mV | 7 |
| `3F` | Beep | 1 / boolean | 10 |
| `40` | Stop charging at full | 1 / boolean | 11 |
| `50` | Persist settings | 1 / value 1 | Not specified |

Save packet: `40 40 43 50 01 01 0A 0D`. The upstream implementation applies writes immediately, then saves them for persistence. Current/voltage writes must respect status-reported limits; capacity limits are supplied separately by the manufacturer's app/server. Exact acknowledgements and wider firmware behavior need further specification.

Other source-derived identifiers: `4A` writes a one-byte 0/1 charge-current lock and disconnects after saving; `3B` changes the password with unspecified payload; `4F` resets factory settings with unspecified payload and disconnects. No credentials or device-specific setting values are included in this reference.
