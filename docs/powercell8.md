# BlackboxMyCar PowerCell 8

Status: **GATT discovery only**. The observed advertisement uses a `PWC8` prefix. Firmware, returned model identity, request acceptance, telemetry fields and checksum semantics are unknown in this dataset.

## Observed proprietary services

Two connections provided discovery metadata. The snapshot contains both service families:

| Service | Characteristic | Discovered properties |
|---|---|---|
| `FF12` | `FF01` | Write without response (`0x04`) |
| `FF12` | `FF02` | Notify (`0x10`) |
| `FF12` | `FF03`–`FF0A` | Read + write (`0x0A`) |
| `FFF0` | `FFF1` | Read + notify (`0x12`) |
| `FFF0` | `FFF2` | Write without response (`0x04`) |

Short UUIDs expand to `0000xxxx-0000-1000-8000-00805f9b34fb`. These are discovered properties, not verified telemetry roles for this battery. Standard Generic Access, Generic Attribute and Device Information services also appeared; their identifying values are excluded.

No telemetry replies were captured. Do not treat connection success, readable metadata or a shared UUID as a successful decoder.

## Research lead

The upstream Cellink Neo+ reference includes the `PWC8` advertised-name prefix in its manufacturer-app model list. Its hardware validation is on a Neo 8+, not this PowerCell 8. `FF12`/`FF01`/`FF02` matches that transport description, while the observed `FFF0` service also resembles the legacy family. Which commands this pack accepts is unresolved.

See the [source-derived Neo+ appendix](cellink-neo-plus.md). It is a research lead, not a PowerCell 8 compatibility claim or instruction to send another model's commands blindly.

## Evidence needed

Confirm returned model/firmware and the selected service, then obtain privacy-reviewed status replies with charging/discharging observations and an approximate manufacturer-display comparison. Until then, keep the [coverage profile](../profiles/powercell8.json) at discovery-only. Do not publish serials, full advertisement suffixes, PIN-bearing frames or unreviewed device-information values.
