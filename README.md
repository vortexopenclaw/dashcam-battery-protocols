# Dashcam Battery Bluetooth Protocols

An open Bluetooth protocol reference for the BlackVue B-124, B-130A and B-130X, BlackboxMyCar BI-750 and PowerCell 8, VIOFO BP100, Cellink Neo, and Thinkware iVolt XTRA / BAB-95. All eight models have scoped hardware telemetry evidence. iVolt XTRA charging and loaded-discharge DAT groups corroborate the native-app-derived ASCII map through strict production-parser acceptance; its battery firmware and returned model identity remain unknown. Use it to build your own dashcam-battery apps and interfaces and keep batteries usable after manufacturer app support ends. UUIDs, connection sequences, commands, packet layouts, units and firmware differences are documented independently of any particular app.

## Battery coverage

| Battery | Evidence | Protocol | Reference |
|---|---|---|---|
| BlackVue B-124 | Hardware-observed telemetry, firmware 1.44 | `43 06`, big-endian | [B-124](docs/b124.md) |
| BlackVue B-130A | Hardware-observed telemetry, firmware 1.61 | `43 06`, extended voltage fields | [B-130A](docs/b130a.md) |
| BlackVue B-130X | Hardware-observed charging/discharging telemetry, firmware 1.61 | `43 06`, extended voltage fields | [B-130X](docs/b130x.md) |
| BlackboxMyCar BI-750 | Hardware-observed telemetry, firmware 1.6 | `ITSC`, big-endian | [BI-750](docs/bi750.md) |
| BlackboxMyCar PowerCell 8 | Hardware-observed telemetry, F141 | `@@`, little-endian, `FF12` status transport | [PowerCell 8](docs/powercell8.md) |
| VIOFO BP100 | Hardware-observed telemetry, V39 | `AA 55 AA 55`, command-specific decimal fields | [BP100](docs/bp100.md) |
| Cellink Neo | Hardware-observed telemetry, 1.52 | `43 06`, classic big-endian layout | [Cellink Neo](docs/cellink-neo6.md) |
| Thinkware iVolt XTRA / BAB-95 | Hardware-corroborated charging/loaded-discharge DAT1-3 and DATA-only startup; firmware/model identity unknown | ASCII `Snn`, FFF1 notify / FFF2 write, additive checksum | [iVolt XTRA](docs/ivolt-xtra.md) |

Coverage reviewed October 11, 2026. A related name, UUID or shared manufacturer does not establish protocol compatibility. B-124X and Cellink Neo+ family references have separate evidence limits.

## Start here

- [Example Bluetooth conversations: initialization, charging and discharging](examples/communication.md)
- [Shared BlackVue legacy transport and field map](docs/blackvue-legacy.md)
- [Cellink Neo+ family protocol](docs/cellink-neo-plus.md)
- [Implementing a Bluetooth client](docs/methodology.md)
- [Sources and attribution](docs/sources.md)
- [Contributing](CONTRIBUTING.md)

The eight machine-readable coverage profiles live in [profiles/](profiles/): eight hardware-telemetry profiles, with iVolt XTRA explicitly qualified by unknown firmware/model identity and production-parser evidence. [Synthetic packet fixtures](examples/vectors.json) demonstrate offsets and units; [exchange sequences](examples/exchanges.json) and the [annotated conversation guide](examples/communication.md) show model-specific subscription and initialization, including the hardware-corroborated iVolt control-triggered DATA-only stream. All iVolt examples remain synthetic: ordinary charging/loaded-discharge DAT interpretations are hardware-corroborated, while full, negative temperature, FFFF, special 9900 and alternative decimal-zero branches remain source-derived. CONT and response checksums are independently constructed, not replayed hardware bytes. GET1 is documented as a native privacy-sensitive read, not a required or authorized telemetry step. GET replies contain password/settings and are deliberately omitted. iVolt response checksums are computed lowercase ASCII sums, not zero placeholders; requests preserve two spaces and CR then LF. Examples contain no private captures. PC8 charging state remains source-derived, not hardware-verified on F141. Legacy/ITSC trailers and BP100 CRC fields are **unverified zero placeholders**; Neo+ family replies end in `0A 0D` (LF then CR) and use zeroed PIN/reserved fields. Do not transmit response fixtures to a battery.

## Interpreting fields

Preserve raw values and per-field timestamps when commands report different measurement groups. Decode input/output voltage and current separately. Calculate power as `V × A` and label it calculated.

Reported capacity is a configured or device-reported value, not measured usable capacity, state of health or evidence that an expansion pack is present. Manufacturer displays may smooth runtime estimates or use an `Ah` label for a current field. See each protocol page for the supported interpretation.

## Scope

The reference documents known identification, status and configuration protocols. Incomplete command layouts are marked unknown rather than inferred from another model. Discover actual GATT properties, subscribe before querying, and match returned identity/firmware before selecting a decoder. Configuration support and locked-setting masks can differ by model. Test-session readings and application-specific logging history are intentionally omitted.

## Validate a contribution

```sh
python3 scripts/verify.py
```

The dependency-free check validates coverage profiles, synthetic packet lengths and decoded expectations, documentation links and common privacy leaks. GitHub Actions repeats it for pushes and pull requests. A passing fixture check does not establish hardware compatibility.

Documentation and data: [CC BY 4.0](LICENSE). Original validation code: [MIT](LICENSE-CODE). Upstream projects retain their own licenses. Related reference: [Dashcam Camera Profiles](https://github.com/vortexopenclaw/dashcam-camera-profiles).
