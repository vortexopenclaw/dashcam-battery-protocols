# Dashcam Battery Bluetooth Protocols

An open Bluetooth protocol reference for the BlackVue B-124, B-130A, and B-130X, BlackboxMyCar BI-750 and PowerCell 8, VIOFO BP100, Cellink Neo, and Thinkware iVolt XTRA / BAB-95. Use it to build your own dashcam-battery apps and interfaces and keep batteries usable after manufacturer app support ends. Each battery reference documents its Bluetooth services, connection sequence, commands, packet layouts and telemetry conversions, with example exchanges for implementing your own client. Model-specific behavior, known configuration commands and remaining unknowns are documented on the individual reference pages.

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
| Thinkware iVolt XTRA / BAB-95 | Hardware-observed charging/discharging telemetry; firmware unknown | ASCII `Snn`, additive checksum | [iVolt XTRA](docs/ivolt-xtra.md) |

Coverage reviewed October 11, 2026. A related name, UUID or shared manufacturer does not establish protocol compatibility. B-124X and Cellink Neo+ family references have separate evidence limits.

## Start here

- [VIOFO HK6 / HK6-F hardwire Bluetooth broadcasts](docs/hk6.md): battery and ACC input-voltage fields observed on HK6-F; accessory reference, separate from battery-pack coverage.
- [Example Bluetooth conversations: initialization, charging and discharging](examples/communication.md)
- [Shared BlackVue legacy transport and field map](docs/blackvue-legacy.md)
- [Cellink Neo+ family protocol](docs/cellink-neo-plus.md)
- [Implementing a Bluetooth client](docs/methodology.md)
- [Sources and attribution](docs/sources.md)
- [Contributing](CONTRIBUTING.md)

The eight machine-readable coverage profiles live in [profiles/](profiles/). [Synthetic packet fixtures](examples/vectors.json) demonstrate offsets and units; [exchange sequences](examples/exchanges.json) and the [annotated conversation guide](examples/communication.md) show subscription, initialization, charging and discharging examples for each battery. All examples use invented values, not private captures. The guide and model pages distinguish hardware-observed behavior from source-derived branches, explain checksum and placeholder conventions, and identify private fields that must not be logged. Do not transmit response fixtures to a battery.

## Interpreting fields

Preserve raw values and per-field timestamps when commands report different measurement groups. Decode input/output voltage and current separately. Calculate power as `V × A` and label it calculated.

Reported capacity is a configured or device-reported value, not measured usable capacity, state of health or evidence that an expansion pack is present. Manufacturer displays may smooth runtime estimates or use an `Ah` label for a current field. See each protocol page for the supported interpretation.

## Scope

The reference documents known identification, status and configuration protocols. Incomplete command layouts are marked unknown rather than inferred from another model. Discover actual GATT properties, subscribe before querying, and match returned identity/firmware where available before selecting a decoder. Where identity is not established, follow the model page's transport and frame-validation gates rather than assuming another battery's protocol. Configuration support and locked-setting masks can differ by model. Test-session readings and application-specific logging history are intentionally omitted.

## Validate a contribution

```sh
python3 scripts/verify.py
```

The dependency-free check validates coverage profiles, synthetic packet lengths and decoded expectations, documentation links and common privacy leaks. GitHub Actions repeats it for pushes and pull requests. A passing fixture check does not establish hardware compatibility.

Documentation and data: [CC BY 4.0](LICENSE). Original validation code: [MIT](LICENSE-CODE). Upstream projects retain their own licenses. Related reference: [Dashcam Camera Profiles](https://github.com/vortexopenclaw/dashcam-camera-profiles).
