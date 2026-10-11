# BlackboxMyCar PowerCell 8

Verified status transport: **FF12, firmware F141**, returned model `PWC8`. The separately discovered `FFF0` transport is not needed for this implementation.

## Observed proprietary services

The device exposes both service families:

| Service | Characteristic | Discovered properties |
|---|---|---|
| `FF12` | `FF01` | Write without response (`0x04`) |
| `FF12` | `FF02` | Notify (`0x10`) |
| `FF12` | `FF03`–`FF0A` | Read + write (`0x0A`) |
| `FFF0` | `FFF1` | Read + notify (`0x12`) |
| `FFF0` | `FFF2` | Write without response (`0x04`) |

Short UUIDs expand to `0000xxxx-0000-1000-8000-00805f9b34fb`. `FF01` query writer/`FF02` response stream are now hardware-verified; auxiliary read/write characteristics and `FFF0` telemetry remain unverified. Identifying standard-service values are excluded.

## Requests and response framing

Subscribe to `FF02`, then six-byte identify request `40 40 30 00 0A 0D`. Require returned canonical `PWC8` identity before six-byte status request `40 40 41 00 0A 0D`. Do not insert an extra speculative zero byte or use `43 06` merely because `FFF0` exists.

Reply header `40 40`, command at offset 2, subcommand at 3, payload length at 4; total length is payload+7, ending `0A 0D`. PWC8 identity is 11 bytes; standard status is 75 bytes with a 68-byte payload. Reassemble notifications. Incoming checksum semantics are unverified; terminator/shape/value checks are not checksum validation. The [Neo+ reference](cellink-neo-plus.md) supplies pinned source context.

## Complete-frame status map

All multibyte fields are little-endian.

| Offset | Bytes | Interpretation |
| --- | --- | --- |
| 5 | 1 | Firmware code, observed 141 |
| 6 | 1 | Percent |
| 7 / 9 | 2 each | Input/output voltage /1000 V |
| 11 / 13 | 2 each | Input/output current /1000 A |
| 17 | 2 | Battery voltage /1000 V |
| 19 / 21 | 2 each | Minutes to full/runtime |
| 23 | 2 | Signed temperature °C |
| 25 / 29 | 4 each | Configured base/expansion capacity mAh |
| 33 | 4 | Remaining-charge counter /3600 mAh, source-derived |
| 44 | 1 | Raw state |
| 59–60 | 2 | Settings PIN, redact before export |

Configured total is base+expansion, not usable capacity, health or detected expansion model/count. Calculate watts from V×A. State 2 means Discharging. Source-derived states: 0 Not used, 1/129 Charging, 4 Fully charged, others protection/unknown. These other states remain unverified on this revision.

## Configuration and unknown fields

The related `@@C` configuration family is described in the [Neo+ reference](cellink-neo-plus.md#configuration-protocol), with authentication, subcommands and supported/locked masks. Its writes are source-derived and not exercised on PC8 F141; check each setting's support bit. Unknown reply layouts can carry private fields outside offsets 59–60. Use [synthetic examples](../examples/vectors.json) for implementation checks.
