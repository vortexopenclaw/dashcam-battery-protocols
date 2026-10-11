# Contributing

Submit a small, evidence-backed correction or a telemetry-only observation summary. Link the relevant model page and state whether evidence comes from hardware, a manufacturer implementation, another project or a synthetic example.

## New hardware evidence

1. Copy [the observation template](examples/observation-template.json).
2. Record model, firmware, GATT service/characteristic UUIDs and properties. Leave unknown fields null.
3. Describe charging/discharging activity and decoded measurements, with units and approximate reference values. Use elapsed intervals rather than original session timestamps.
4. Keep device identifiers and private bytes out of the submission. Read [privacy guidance](docs/methodology.md#privacy).
5. Open a pull request or an issue with the summary. Do not attach an unreviewed phone export, HCI log, screenshot, APK or full packet dump.

Model matching must come from the selected device and returned identity where available. A discovered service is weaker evidence than a matching response; a synthetic test does not upgrade a profile to hardware-observed.

## Protocol corrections

Name the affected model/firmware, command and offset. Cite a stable source or describe reviewed hardware evidence. Preserve disagreements instead of silently replacing another revision's behavior. Unknown states and reserved fields should stay unknown until evidence resolves them.

When adding a packet example, construct it from documented fields with zero placeholders for device-ID/reserved bytes. Mark it synthetic and do not invent a checksum claim. Add the decoded expectations to [vectors.json](examples/vectors.json), then run:

```sh
python3 scripts/verify.py
```

Maintainers review identity, scope, evidence and privacy before publishing. New setting writes, firmware-update procedures and blind protocol probes are outside this telemetry reference. Source links retain attribution; original documentation/data uses CC BY 4.0 and original helper code uses MIT.
