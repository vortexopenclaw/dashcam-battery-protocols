# Evidence and measurement methodology

## Evidence levels

1. **Hardware-observed:** a selected battery returned the documented bytes or GATT metadata. A firmware/model check and parser replay establish which device/revision supplied telemetry.
2. **Manufacturer-derived:** offline analysis of a named manufacturer-app version establishes a field or branch. It does not prove that every supported model uses that branch in the field.
3. **Upstream-source-derived:** a cited, commit-pinned project describes the behavior. Retain the upstream project's tested-model limits.
4. **Synthetic fixture:** invented bytes exercise the documented map. They establish example consistency, not a real measurement, checksum or model capability.
5. **Unknown:** no adequate evidence. Keep unknowns visible rather than filling them from a related model.

Profiles distinguish telemetry coverage from discovery. Individual pages distinguish tested firmware branches from source-derived ones. The dated observation summaries publish model-level facts without raw captures or device identifiers.

## Observation inventory

Reviewed October 10, 2026:

| Model | Hardware telemetry evidence | Important limits |
|---|---|---|
| B-124, 1.44 | 487 full status frames plus 3 firmware replies | Full-charge/protection states and other revisions not established |
| B-130A, 1.61 | 346 full status frames in successful session | One disconnect/reconnection; automatic recovery unverified |
| BI-750, 1.6 | 200 vitals replies plus separate electrical/time packets | Raw mode 4 incomplete; packets are asynchronous |
| PowerCell 8 | 2 connections with GATT metadata | No telemetry replies |
| BP100 | None | Entire wire protocol unknown |

Counts describe the reviewed dataset, not the number of unique batteries. An upload batch, BLE callback, reconstructed frame and decoded status sample are different units. Never compare them as if interchangeable.

## Comparison and logging

Use manufacturer displays as approximate references for units, scales and states. Measurements change between apps; time estimates can smooth differently. Keep raw values, timestamp and freshness per field. Do not manufacture same-time precision or request repeated scans solely to eliminate small asynchronous differences.

Record input and output separately. Positive input current supports charging activity; positive output current supports load activity, which can coexist with charging. Preserve raw mode codes instead of using electrical activity to invent undocumented modes. Voltage without current does not establish energy delivered.

Calculate power as volts × amps and distinguish reported capacity from measured energy. Energy integration needs timestamps, gap handling and a stated estimate method. Do not interpret missing data as zero consumption, assume uninterrupted runtime or draw battery-health conclusions from configured capacity.

## Transport and runtime

Subscribe before polling; respect actual GATT properties; serialize client operations; verify expected frame length before decoding. Reset stream state on reconnection. A header can occur inside a payload, so consume a complete length-delimited frame rather than splitting on every header occurrence.

Connection while already charging is observed for B-124 and BI-750. B-130A transitioned through charging after connection; its initial engine-on connection remains unverified. No simultaneous multi-pack, background/screen-off or automatic reconnect acceptance is claimed. Current data establishes telemetry compatibility, not a finished unattended monitoring system.

## Privacy

Public evidence uses generalized names, aggregate observations and synthetic packets. Exclude BLE addresses, serials, advertisement suffixes, phone identifiers, exact session timestamps, owner screenshots, app exports, service-account details, capture endpoints, credentials and APK/decompiled source archives. Protocol UUIDs, model names, firmware revisions and the source APK's public integrity hash are not private device identifiers.

Before accepting any new raw example, review every byte, including unknown/reserved fields and trailer bytes. Use [the contribution template](../examples/observation-template.json) for telemetry-only summaries. Public examples remain explicitly synthetic unless a separate reviewed publication process establishes otherwise.
