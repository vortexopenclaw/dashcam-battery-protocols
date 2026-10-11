# Implementing a Bluetooth client

## Evidence levels

1. **Hardware-observed:** a selected battery returned the documented bytes or GATT metadata. A firmware/model check and parser replay establish which device/revision supplied telemetry.
2. **Manufacturer-derived:** offline analysis of a named manufacturer-app version establishes a field or branch. It does not prove that every supported model uses that branch in the field.
3. **Upstream-source-derived:** a cited, commit-pinned project describes the behavior. Retain the upstream project's tested-model limits.
4. **Synthetic fixture:** invented bytes exercise the documented map. They establish example consistency, not a real measurement, checksum or model capability.
5. **Unknown:** no adequate evidence. Keep unknowns visible rather than filling them from a related model.

Use the model page's firmware and source information to select a layout. Synthetic examples check the byte map; they are not device captures. Test-session measurements and app-specific validation history are intentionally kept out of this protocol reference.

## Field semantics

Keep raw values and freshness per field when separate commands return separate measurement groups. Manufacturer displays may smooth time estimates; document wire values independently of UI formatting.

Record input and output separately. Positive input current supports charging activity; positive output current supports load activity, which can coexist with charging. Preserve raw mode codes instead of using electrical activity to invent undocumented modes. Voltage without current does not establish energy delivered.

Calculate power as volts × amps and distinguish reported capacity from measured energy. Energy integration needs timestamps, gap handling and a stated estimate method. Do not interpret missing data as zero consumption, assume uninterrupted runtime or draw battery-health conclusions from configured capacity.

## Transport and runtime

Subscribe before polling; respect actual GATT properties; serialize client operations; verify expected frame length before decoding. Reset stream state on reconnection. A header can occur inside a payload, so consume a complete length-delimited frame rather than splitting on every header occurrence.

On disconnect, discard partial frames and re-identify before resuming commands. A connection timeout before service discovery is not a decoded protocol error. Preserve original advertised names for identity; replacement characters can be removed only from presentation. Battery measurements do not identify the connected dashcam model.

## Privacy

Public examples use generalized names and synthetic packets. Exclude BLE addresses, serials, advertisement suffixes, phone identifiers, screenshots, app exports, credentials and APK/decompiled source archives. Protocol UUIDs, model names, firmware revisions and source artifact hashes are protocol/provenance facts, not private device identifiers.

Before accepting any new raw example, review every byte, including unknown/reserved fields and trailer bytes. Use [the contribution template](../examples/observation-template.json) for protocol facts and unknowns. Public examples remain explicitly synthetic unless a separate reviewed publication process establishes otherwise.
