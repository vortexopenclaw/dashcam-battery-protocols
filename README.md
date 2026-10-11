# Dashcam Battery Bluetooth Protocols

An open Bluetooth protocol reference for building your own dashcam-battery apps and interfaces, including keeping batteries usable after manufacturer app support ends. UUIDs, connection sequences, commands, packet layouts, units and firmware differences are documented independently of any particular app.

## Battery coverage

| Battery | Evidence | Protocol | Reference |
|---|---|---|---|
| BlackVue B-124 | Hardware-observed telemetry, firmware 1.44 | `43 06`, big-endian | [B-124](docs/b124.md) |
| BlackVue B-130A | Hardware-observed telemetry, firmware 1.61 | `43 06`, extended voltage fields | [B-130A](docs/b130a.md) |
| BlackboxMyCar BI-750 | Hardware-observed telemetry, firmware 1.6 | `ITSC`, big-endian | [BI-750](docs/bi750.md) |
| BlackboxMyCar PowerCell 8 | Hardware-observed telemetry, F141 | `@@`, little-endian, `FF12` status transport | [PowerCell 8](docs/powercell8.md) |
| VIOFO BP100 | Hardware-observed telemetry, V39 | `AA 55 AA 55`, command-specific decimal fields | [BP100](docs/bp100.md) |
| Original Cellink Neo 6 | Hardware-observed telemetry, 1.52 | `43 06`, classic big-endian layout | [Neo 6](docs/cellink-neo6.md) |

Coverage reviewed October 10, 2026. A related name, UUID or shared manufacturer does not establish protocol compatibility. B-124X, B-130X and Cellink Neo+ family references have separate evidence limits.

## Start here

- [Shared BlackVue legacy transport and field map](docs/blackvue-legacy.md)
- [Cellink Neo+ family protocol](docs/cellink-neo-plus.md)
- [Implementing a Bluetooth client](docs/methodology.md)
- [Sources and attribution](docs/sources.md)
- [Contributing](CONTRIBUTING.md)

The six machine-readable coverage profiles live in [profiles/](profiles/). [Synthetic packet examples](examples/vectors.json) demonstrate offsets and units without private captures. Legacy/ITSC trailers and BP100 CRC fields are **unverified zero placeholders**; Neo+ family replies end in `0A 0D` (LF then CR) and use zeroed PIN/reserved fields. Do not transmit response fixtures to a battery.

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
