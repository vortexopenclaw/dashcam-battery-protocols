# Dashcam Battery Bluetooth Protocols

An open technical reference for reading dashcam battery telemetry over Bluetooth Low Energy. It documents transport UUIDs, telemetry requests, packet layouts, units and firmware differences. The reference is independent of any monitoring app.

## Battery coverage

| Battery | Evidence | Protocol | Reference |
|---|---|---|---|
| BlackVue B-124 | Hardware-observed telemetry, firmware 1.44 | `43 06`, big-endian | [B-124](docs/b124.md) |
| BlackVue B-130A | Hardware-observed telemetry, firmware 1.61 | `43 06`, extended voltage fields | [B-130A](docs/b130a.md) |
| BlackboxMyCar BI-750 | Hardware-observed telemetry, firmware 1.6 | `ITSC`, big-endian | [BI-750](docs/bi750.md) |
| BlackboxMyCar PowerCell 8 | GATT discovery only | Unconfirmed; both `FF12` and `FFF0` services observed | [PowerCell 8](docs/powercell8.md) |
| VIOFO BP100 | No hardware capture in this dataset | Unknown | [BP100](docs/bp100.md) |

Coverage reviewed October 10, 2026. A related name, UUID or shared manufacturer does not establish protocol compatibility. B-124X, B-130X and Cellink Neo+ family references have separate evidence limits.

## Start here

- [Shared BlackVue legacy transport and field map](docs/blackvue-legacy.md)
- [Cellink Neo+ research lead](docs/cellink-neo-plus.md)
- [Evidence and measurement methodology](docs/methodology.md)
- [Sources and attribution](docs/sources.md)
- [Contributing](CONTRIBUTING.md)

The five machine-readable coverage profiles live in [profiles/](profiles/). [Synthetic packet examples](examples/vectors.json) demonstrate offsets and units without publishing private captures. Their placeholder response trailer bytes are **not verified checksums**; do not transmit response fixtures to a battery.

## Measurement semantics

Compare manufacturer apps in the ballpark. Preserve raw values and per-field timestamps rather than forcing exact agreement across asynchronous readings. Report charge percentage, temperature, input/output voltage and current, raw time estimates and reported capacity separately. Calculate power as `V × A` and label it calculated.

Reported capacity is a configured or device-reported value, not measured usable capacity, state of health or evidence that an expansion pack is present. Manufacturer displays may smooth runtime estimates or use an `Ah` label for a current field. See each protocol page for the supported interpretation.

## Scope

This reference covers identification and telemetry. It does not provide setting changes, firmware writes, pairing resets or command brute force. Discover the selected battery's GATT properties, verify its identity and subscribe before sending model-specific requests. Unknown protocols remain unknown.

Hardware observations include charging and discharging on the three decoded models, and connection while already charging. They do not prove unattended screen-off logging, automatic reconnection or simultaneous multi-pack connections.

## Validate a contribution

```sh
python3 scripts/verify.py
```

The dependency-free check validates coverage profiles, synthetic packet lengths and decoded expectations, documentation links and common privacy leaks. GitHub Actions repeats it for pushes and pull requests. A passing fixture check does not establish hardware compatibility.

Documentation and data: [CC BY 4.0](LICENSE). Original validation code: [MIT](LICENSE-CODE). Upstream projects retain their own licenses. Related reference: [Dashcam Camera Profiles](https://github.com/vortexopenclaw/dashcam-camera-profiles).
