# Thinkware iVolt XTRA / BAB-95

Status: **hardware-observed GATT discovery, not a verified telemetry decoder**. Firmware identity, measurement layouts and proprietary command semantics remain unknown. iVolt Mini / BAB950 is a different product and is not covered by this profile.

## Discovery

The observed device name uses `IVT-` followed by four hexadecimal characters. Treat this as a discovery hint, not a returned model identity or proof that another iVolt revision is compatible. Never publish the device-specific suffix.

Short UUIDs below expand to `0000xxxx-0000-1000-8000-00805f9b34fb`. The selected device exposes these proprietary characteristics:

| Service | Characteristic | Observed properties | Interpretation |
| --- | --- | --- | --- |
| `FF12` | `FF01` | Write without response (`0x04`) | Purpose and command format unknown |
| `FF12` | `FF02` | Notify (`0x10`) | Candidate response channel; telemetry not established |
| `FF12` | `FF03` through `FF0A` | Read + write (`0x0A`) | Readable values; field meanings and writes unverified |
| `FFF0` | `FFF1` | Read + notify (`0x12`) | Received data; status framing/meaning unknown |
| `FFF0` | `FFF2` | Write without response (`0x04`) | Purpose and command format unknown |

Standard GAP, GATT and Device Information services are also present. Their values can contain private names, serials and other identifiers; they are not a public telemetry specification.

## Read-only client foundation

1. Discover the selected device's actual services and properties. Preserve its identity privately and do not select a decoder solely from its advertised name.
2. For observation, enable notification delivery on a discovered notify characteristic using its standard CCCD `2902` with value `01 00`. Subscribe before optional reads, and await the platform subscription result.
3. Record notification chunks privately with timestamps and characteristic UUIDs. Keep completed reads separate from notifications: a readable-and-notifiable characteristic can deliver both, and neither a callback nor its length establishes a complete status packet.
4. If examining the readable `FF03` through `FF0A` values, serialize reads, bound timeouts and keep values uninterpreted until independently mapped. Do not repeatedly read a response stream instead of subscribing.
5. Disconnect cleanly to release the battery for its native app. Do not send proprietary query, configuration, pairing or reset commands merely because a characteristic is writable.

No manufacturer-specific TX request or decoded charging/discharging exchange is published yet. There are deliberately no invented response vectors for this profile. Recover initialization, response framing, field offsets, units, state codes and firmware identity before implementing status queries or presenting measurements.

## Similarities and differences

The discovered `FF12`/`FF01`/`FF02`, `FF03` through `FF0A`, and `FFF0`/`FFF1`/`FFF2` service topology and properties match those documented for [PowerCell 8](powercell8.md). This is evidence of similar GATT transport, **not proof of the same `@@` packet format, commands, field map or settings**. Do not send PowerCell 8 identify/status packets to this battery until iVolt-specific evidence establishes them.

The `FFF0` service also resembles the transport used by [BlackVue and original Cellink Neo](blackvue-legacy.md), but their `43 06` framing is not established for iVolt. [BI-750](bi750.md) uses different custom UUIDs and `ITSC` framing; [BP100](bp100.md) uses different custom UUIDs and its own frame/CRC policy.

Shared UUIDs do not establish the original equipment manufacturer, common firmware or a safe settings interface. Manufacturer/OEM attribution remains unverified here.

## Unknowns and privacy

- Returned model and firmware identity; initialization or authentication requirements.
- Which channel carries measurements, and whether notifications are telemetry or connection/control messages.
- Complete frame boundaries, checksums, command acknowledgements and polling limits.
- Charge, voltage/current, temperature, estimates, capacity and state-field semantics.
- Settings, protection states, binding and persistence.
- Whether charging-mode zero output current means unavailable reporting or a real no-load condition.

Public facts are derived from privately reviewed discovery records. No owner screenshot, serial, device suffix or raw payload is redistributed. Use the [profile](../profiles/ivolt-xtra.json) and [implementation guidance](methodology.md) to preserve this evidence boundary.
