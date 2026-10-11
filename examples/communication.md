# Example Bluetooth conversations

[vectors.json](vectors.json) contains individual machine-readable request/response fixtures. [exchanges.json](exchanges.json) connects them into model-specific initialization and charging/discharging sequences. This page shows those bytes with direction and decoded fields.

**All RX values are invented.** These are independent illustrations, not raw captures or one continuous charging-to-discharge recording. Legacy/ITSC trailer bytes and incoming BP100 CRC fields are unverified zero placeholders. PC8 PIN/reserved bytes are zeroed. TX examples are documented identification/status queries; never transmit an RX fixture to a battery.

## Start every connection this way

1. Connect to the intended device and discover its actual service/characteristic properties. Advertised names and similar UUIDs are hints, not model/firmware verification.
2. Enable notification delivery on the listed response characteristic. For its standard CCCD `00002902-0000-1000-8000-00805f9b34fb`, notification-enable value is `01 00`; if the discovered property is indications instead, use `02 00`. This is a GATT descriptor write, not a packet sent to the query writer. Await subscription completion before querying.
3. Send the model's identification query and reassemble the reply. Verify the expected model/firmware or application mode before status queries. These query/reply steps are the initialization exchange, not proof that a separate pairing/authentication protocol is absent.
4. Serialize operations and match response command/shape. A write-without-response has no ATT acknowledgement; local write acceptance is not an application reply. Preserve timeouts and unknown replies rather than manufacturing telemetry. Do not repeatedly read a notify response stream as a substitute for subscribing.
5. Repeat status queries conservatively. On disconnect discard partial frames, reconnect, subscribe and identify again. Independent groups need independent timestamps; old cached fields are not live measurements.

`TX` means client to battery through the listed writer. `RX` means the reassembled battery-to-client notification/indication frame, not necessarily one radio notification. Decoded blocks show selected expected fields, with units in names (`_v`, `_a`, `_w`, `_min`, `_mah`, `_c`). Watts are volts × amps, not a separate measured-energy claim.

## BlackVue B-124, firmware 1.44

[Protocol reference](../docs/b124.md).

- Service: `0000fff0-0000-1000-8000-00805f9b34fb`
- Writer: `0000fff2-0000-1000-8000-00805f9b34fb`
- Response: `0000fff1-0000-1000-8000-00805f9b34fb`
- TX mode: write without response.

Match B-124 and revision 144 before decoding the classic status layout. Output current can be positive during charging.

### Identification / initialization

```text
TX [blackvue_identify]: 43 06 00 52 17
RX [b124_identity]: 43 06 0C 52 00 90 00 00 00 00 42 2D 31 32 34 00 00
```

Selected decoded fields:

```json
{
  "firmware": "1.44",
  "model": "B-124"
}
```

### Charging illustration

```text
TX [blackvue_status]: 43 06 00 51 14
RX [b124_charging]: 43 06 12 51 B8 00 00 00 0E 80 8A 8A 8A 00 23 28 02 08 31 38 01 00 00
```

Selected decoded fields:

```json
{
  "charge_percent": 84,
  "temperature_c": 28,
  "input_v": 13.8,
  "input_a": 9,
  "output_v": 13.8,
  "output_a": 0.52,
  "time_to_full_min": 14,
  "reported_capacity_mah": 12600,
  "state_code": 1
}
```

### Discharging illustration

```text
TX [blackvue_status]: 43 06 00 51 14
RX [b124_discharge]: 43 06 12 51 AF 04 37 00 00 81 84 00 84 00 00 00 02 08 31 38 03 00 00
```

Selected decoded fields:

```json
{
  "charge_percent": 75,
  "temperature_c": 29,
  "input_v": 0,
  "input_a": 0,
  "output_v": 13.2,
  "output_a": 0.52,
  "runtime_estimate_min": 1079,
  "state_code": 3
}
```

## BlackVue B-130A, firmware 1.61

[Protocol reference](../docs/b130a.md).

- Service: `0000fff0-0000-1000-8000-00805f9b34fb`
- Writer: `0000fff2-0000-1000-8000-00805f9b34fb`
- Response: `0000fff1-0000-1000-8000-00805f9b34fb`
- TX mode: write without response.

Match B-130A and revision 161; use extended voltage offsets 23/25. Zero output current while input is powered does not establish zero attached-load consumption.

### Identification / initialization

```text
TX [blackvue_identify]: 43 06 00 52 17
RX [b130a_identity]: 43 06 0C 52 00 A1 00 00 00 00 42 2D 31 33 30 41 00
```

Selected decoded fields:

```json
{
  "firmware": "1.61",
  "model": "B-130A"
}
```

### Charging illustration

```text
TX [blackvue_status]: 43 06 00 51 14
RX [b130a_charging]: 43 06 18 51 B4 00 00 00 1E 7C 90 00 00 00 13 88 00 00 1D 4C 01 00 00 00 78 00 8C 00 00
```

Selected decoded fields:

```json
{
  "charge_percent": 80,
  "temperature_c": 24,
  "input_v": 12.0,
  "input_a": 5.0,
  "output_v": 14.0,
  "output_a": 0.0,
  "runtime_estimate_min": 0,
  "time_to_full_min": 30,
  "reported_capacity_mah": 7500,
  "state_code": 1
}
```

### Discharging illustration

```text
TX [blackvue_status]: 43 06 00 51 14
RX [b130a_discharge]: 43 06 18 51 9D 00 F3 00 00 80 83 00 00 00 00 00 04 06 1D 4C 03 00 00 00 00 00 81 00 00
```

Selected decoded fields:

```json
{
  "charge_percent": 57,
  "temperature_c": 28,
  "input_v": 0,
  "input_a": 0,
  "output_v": 12.9,
  "output_a": 1.03,
  "runtime_estimate_min": 243,
  "reported_capacity_mah": 7500,
  "state_code": 3
}
```

## BlackVue B-130X, firmware 1.61

[Protocol reference](../docs/b130x.md).

- Service: `0000fff0-0000-1000-8000-00805f9b34fb`
- Writer: `0000fff2-0000-1000-8000-00805f9b34fb`
- Response: `0000fff1-0000-1000-8000-00805f9b34fb`
- TX mode: write without response.

Match B-130X and revision 161 separately from B-130A. State 0/zero current can coexist with output voltage. Charging-mode zero discharge current does not prove that a camera is off.

### Identification / initialization

```text
TX [blackvue_identify]: 43 06 00 52 17
RX [b130x_identity]: 43 06 0C 52 00 A1 00 00 00 00 42 2D 31 33 30 58 00
```

Selected decoded fields:

```json
{
  "firmware": "1.61",
  "model": "B-130X"
}
```

### Charging illustration

```text
TX [blackvue_status]: 43 06 00 51 14
RX [b130x_charging]: 43 06 18 51 B4 00 00 00 1E 7C 90 00 00 00 13 88 00 00 1D 4C 01 00 00 00 78 00 8C 00 00
```

Selected decoded fields:

```json
{
  "charge_percent": 80,
  "temperature_c": 24,
  "input_v": 12.0,
  "input_a": 5.0,
  "output_v": 14.0,
  "output_a": 0.0,
  "runtime_estimate_min": 0,
  "time_to_full_min": 30,
  "reported_capacity_mah": 7500,
  "state_code": 1
}
```

### Discharging illustration

```text
TX [blackvue_status]: 43 06 00 51 14
RX [b130x_discharge]: 43 06 18 51 96 01 2C 00 00 7D 88 00 00 00 00 00 01 F4 1D 4C 03 00 00 00 00 00 82 00 00
```

Selected decoded fields:

```json
{
  "charge_percent": 50,
  "temperature_c": 25,
  "input_v": 0.0,
  "input_a": 0.0,
  "output_v": 13.0,
  "output_a": 0.5,
  "runtime_estimate_min": 300,
  "time_to_full_min": 0,
  "reported_capacity_mah": 7500,
  "state_code": 3
}
```

### Input off, zero-load illustration

```text
TX [blackvue_status]: 43 06 00 51 14
RX [b130x_no_load]: 43 06 18 51 96 00 00 00 00 7D 88 00 00 00 00 00 00 00 1D 4C 00 00 00 00 00 00 82 00 00
```

Selected decoded fields:

```json
{
  "charge_percent": 50,
  "temperature_c": 25,
  "input_v": 0.0,
  "input_a": 0.0,
  "output_v": 13.0,
  "output_a": 0.0,
  "runtime_estimate_min": 0,
  "time_to_full_min": 0,
  "reported_capacity_mah": 7500,
  "state_code": 0
}
```

## BlackboxMyCar BI-750, firmware 1.6

[Protocol reference](../docs/bi750.md).

- Service: `49535343-fe7d-4ae5-8fa9-9fafd205e455`
- Writer: `49535343-8841-43f4-a8d4-ecbe34729bb3`
- Response: `49535343-1e4d-4bd9-ba61-23c647249616`
- TX mode: write with response in the upstream implementation; inspect actual properties.

Word 32 identifies model/firmware. Cycle 33/34/35 and timestamp groups separately; they are not an atomic snapshot. Raw mode 4 is not a complete state specification. Raw mode 0 plus zero input and positive output supports discharging; zero charging-mode output current does not establish zero camera consumption.

### Identification / initialization

```text
TX [bi750_identify]: 49 54 53 43 00 00 32 00
RX [bi750_identity]: 49 54 53 43 00 00 32 10 00 00 00 42 69 37 35 30 00
```

Selected decoded fields:

```json
{
  "firmware": "1.6",
  "model": "Bi750"
}
```

### Charging illustration

```text
TX [bi750_vitals_request]: 49 54 53 43 00 00 33 00
RX [bi750_vitals]: 49 54 53 43 00 00 33 2B 2C 04 00 00 00 00 00 00
```

Selected decoded fields:

```json
{
  "charge_percent": 43,
  "temperature_c": 44,
  "state_code": 4
}
```

```text
TX [bi750_electrical_request]: 49 54 53 43 00 00 34 00
RX [bi750_electrical]: 49 54 53 43 00 00 34 36 10 37 14 37 5A 00 00 00
```

Selected decoded fields:

```json
{
  "input_v": 13.84,
  "input_a": 14.1,
  "input_w": 195.144,
  "output_v": 14.17,
  "output_a": 0,
  "output_w": 0
}
```

```text
TX [bi750_time_capacity_request]: 49 54 53 43 00 00 35 00
RX [bi750_time_capacity]: 49 54 53 43 00 00 35 00 28 00 00 3A 98 00 00 00
```

Selected decoded fields:

```json
{
  "time_to_full_min": 40,
  "runtime_estimate_min": 0,
  "reported_capacity_mah": 15000
}
```

### Discharging illustration

```text
TX [bi750_vitals_request]: 49 54 53 43 00 00 33 00
RX [bi750_discharge_vitals]: 49 54 53 43 00 00 33 32 19 00 00 00 00 00 00 00
```

Selected decoded fields:

```json
{
  "charge_percent": 50,
  "temperature_c": 25,
  "state_code": 0
}
```

```text
TX [bi750_electrical_request]: 49 54 53 43 00 00 34 00
RX [bi750_discharge_electrical]: 49 54 53 43 00 00 34 00 00 00 00 32 C8 01 F4 00
```

Selected decoded fields:

```json
{
  "input_v": 0.0,
  "input_a": 0.0,
  "input_w": 0.0,
  "output_v": 13.0,
  "output_a": 0.5,
  "output_w": 6.5
}
```

```text
TX [bi750_time_capacity_request]: 49 54 53 43 00 00 35 00
RX [bi750_discharge_time_capacity]: 49 54 53 43 00 00 35 00 00 01 2C 3A 98 00 00 00
```

Selected decoded fields:

```json
{
  "time_to_full_min": 0,
  "runtime_estimate_min": 300,
  "reported_capacity_mah": 15000
}
```

## Cellink Neo, firmware 1.52

[Protocol reference](../docs/cellink-neo6.md).

- Service: `0000fff0-0000-1000-8000-00805f9b34fb`
- Writer: `0000fff2-0000-1000-8000-00805f9b34fb`
- Response: `0000fff1-0000-1000-8000-00805f9b34fb`
- TX mode: write without response.

The product is Cellink Neo; its returned six-byte identity is Neo 6. Require revision 152 and use classic voltage offsets 11/12, not the B-130 extended map. This charging illustration has no output load. State 0/zero runtime with no load does not indicate an empty battery. Shared telemetry does not authorize BlackVue configuration commands.

### Identification / initialization

```text
TX [blackvue_identify]: 43 06 00 52 17
RX [neo6_identity]: 43 06 0C 52 00 98 00 00 00 00 4E 65 6F 20 36 00 00
```

Selected decoded fields:

```json
{
  "model": "Neo 6",
  "firmware": "1.52"
}
```

### Charging illustration

```text
TX [blackvue_status]: 43 06 00 51 14
RX [neo6_charging_no_load]: 43 06 12 51 B4 00 00 00 0F 7C 82 6E 82 00 13 88 00 00 17 70 01 00 00
```

Selected decoded fields:

```json
{
  "charge_percent": 80,
  "temperature_c": 24,
  "input_v": 11.0,
  "input_a": 5.0,
  "output_v": 13.0,
  "output_a": 0.0,
  "reported_capacity_mah": 6000,
  "time_to_full_min": 15,
  "runtime_estimate_min": 0,
  "state_code": 1
}
```

### Discharging illustration

```text
TX [blackvue_status]: 43 06 00 51 14
RX [neo6_discharge]: 43 06 12 51 96 01 2C 00 00 7D 82 00 82 00 00 00 01 F4 17 70 03 00 00
```

Selected decoded fields:

```json
{
  "charge_percent": 50,
  "temperature_c": 25,
  "input_v": 0.0,
  "input_a": 0.0,
  "output_v": 13.0,
  "output_a": 0.5,
  "reported_capacity_mah": 6000,
  "time_to_full_min": 0,
  "runtime_estimate_min": 300,
  "state_code": 3
}
```

### Input off, zero-load illustration

```text
TX [blackvue_status]: 43 06 00 51 14
RX [neo6_no_load]: 43 06 12 51 96 00 00 00 00 7D 82 00 82 00 00 00 00 00 17 70 00 00 00
```

Selected decoded fields:

```json
{
  "charge_percent": 50,
  "temperature_c": 25,
  "input_v": 0.0,
  "input_a": 0.0,
  "output_v": 13.0,
  "output_a": 0.0,
  "reported_capacity_mah": 6000,
  "time_to_full_min": 0,
  "runtime_estimate_min": 0,
  "state_code": 0
}
```

## BlackboxMyCar PowerCell 8, F141

[Protocol reference](../docs/powercell8.md).

- Service: `0000ff12-0000-1000-8000-00805f9b34fb`
- Writer: `0000ff01-0000-1000-8000-00805f9b34fb`
- Response: `0000ff02-0000-1000-8000-00805f9b34fb`
- TX mode: write without response.

Charging state 1 is source-derived and NOT hardware-verified on F141; this fixture illustrates the documented branch, not accepted charging support. Discharging state 2 is hardware-observed. Require PWC8 identity before status. Use the six-byte requests on FF12, not the separately present FFF0 service; LF then CR terminates frames. Settings PIN and reserved fields are zeroed, not real credentials.

### Identification / initialization

```text
TX [pc8_get_30]: 40 40 30 00 0A 0D
RX [pc8_identity]: 40 40 30 00 04 50 57 43 38 0A 0D
```

Selected decoded fields:

```json
{
  "model": "PWC8"
}
```

### Charging illustration

```text
TX [pc8_get_41]: 40 40 41 00 0A 0D
RX [pc8_charging]: 40 40 41 00 44 8D 50 E0 2E C8 32 88 13 00 00 00 00 C8 32 1E 00 00 00 19 00 4C 1D 00 00 4C 1D 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0A 0D
```

Selected decoded fields:

```json
{
  "firmware": "F141",
  "charge_percent": 80,
  "input_v": 12.0,
  "input_a": 5.0,
  "input_w": 60.0,
  "output_v": 13.0,
  "output_a": 0.0,
  "output_w": 0.0,
  "temperature_c": 25,
  "reported_capacity_mah": 15000,
  "time_to_full_min": 30,
  "runtime_estimate_min": 0,
  "state_code": 1
}
```

### Discharging illustration

```text
TX [pc8_get_41]: 40 40 41 00 0A 0D
RX [pc8_discharge]: 40 40 41 00 44 8D 3C 00 00 C8 32 00 00 20 03 00 00 C8 32 00 00 58 02 19 00 4C 1D 00 00 4C 1D 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0A 0D
```

Selected decoded fields:

```json
{
  "firmware": "F141",
  "charge_percent": 60,
  "input_v": 0.0,
  "input_a": 0.0,
  "output_v": 13.0,
  "output_a": 0.8,
  "output_w": 10.4,
  "temperature_c": 25,
  "reported_capacity_mah": 15000,
  "runtime_estimate_min": 600,
  "state_code": 2
}
```

## VIOFO BP100, V39

[Protocol reference](../docs/bp100.md).

- Service: `c0a12213-64b5-6e57-3299-aab3c4d1eaf0`
- Writer: `c0a12213-143a-7ed7-5291-a3bfc5c1da0f`
- Response: `c0a12213-2455-fe56-3866-5ad3e4f112b0`
- TX mode: write with response where supported; observed writer also supports no-response.

GET_MODE must return positive firmware and application mode 16 before 01-04; boot mode 1 is not ready. The charging bit is command-01 payload bit 7, not the same enumeration as BlackVue or PC8. Current fractions differ: input p2/10+p3, output p2/100+p3. Outgoing CRC is XMODEM; native sessions skip incoming CRC verification. No UID/binding mutation is part of these exchanges.

### Identification / initialization

```text
TX [bp100_get_41]: AA 55 AA 55 00 00 41 00 06 5C 00 00
RX [bp100_identity]: AA 55 AA 55 05 00 41 00 00 00 00 00 27 00 00 00 10
```

Selected decoded fields:

```json
{
  "firmware": "39",
  "model": "BP100"
}
```

### Charging illustration

```text
TX [bp100_get_01]: AA 55 AA 55 00 00 01 00 16 36 00 00
RX [bp100_charging]: AA 55 AA 55 02 00 01 00 00 00 00 00 E0 00
```

Selected decoded fields:

```json
{
  "charge_percent": 96,
  "state_code": 1
}
```

```text
TX [bp100_get_02]: AA 55 AA 55 00 00 02 00 F6 F8 00 00
RX [bp100_temperature]: AA 55 AA 55 04 00 02 00 00 00 00 00 04 17 00 14
```

Selected decoded fields:

```json
{
  "temperature_c": 23.4
}
```

```text
TX [bp100_get_03]: AA 55 AA 55 00 00 03 00 56 BD 00 00
RX [bp100_input]: AA 55 AA 55 08 00 03 00 00 00 00 00 03 0B 07 04 00 00 03 00
```

Selected decoded fields:

```json
{
  "input_v": 11.3,
  "input_a": 4.7,
  "input_w": 53.11,
  "time_to_full_min": 3
}
```

```text
TX [bp100_get_04]: AA 55 AA 55 00 00 04 00 17 75 00 00
RX [bp100_output]: AA 55 AA 55 08 00 04 00 00 00 00 00 01 0D 46 00 00 00 58 02
```

Selected decoded fields:

```json
{
  "output_v": 13.1,
  "output_a": 0.7,
  "output_w": 9.17,
  "runtime_estimate_min": 600
}
```

### Discharging illustration

```text
TX [bp100_get_01]: AA 55 AA 55 00 00 01 00 16 36 00 00
RX [bp100_discharging]: AA 55 AA 55 02 00 01 00 00 00 00 00 60 00
```

Selected decoded fields:

```json
{
  "charge_percent": 96,
  "state_code": 0
}
```

```text
TX [bp100_get_02]: AA 55 AA 55 00 00 02 00 F6 F8 00 00
RX [bp100_temperature]: AA 55 AA 55 04 00 02 00 00 00 00 00 04 17 00 14
```

Selected decoded fields:

```json
{
  "temperature_c": 23.4
}
```

```text
TX [bp100_get_03]: AA 55 AA 55 00 00 03 00 56 BD 00 00
RX [bp100_input_off]: AA 55 AA 55 08 00 03 00 00 00 00 00 00 00 00 00 00 00 00 00
```

Selected decoded fields:

```json
{
  "input_v": 0.0,
  "input_a": 0.0,
  "input_w": 0.0,
  "time_to_full_min": 0
}
```

```text
TX [bp100_get_04]: AA 55 AA 55 00 00 04 00 17 75 00 00
RX [bp100_output]: AA 55 AA 55 08 00 04 00 00 00 00 00 01 0D 46 00 00 00 58 02
```

Selected decoded fields:

```json
{
  "output_v": 13.1,
  "output_a": 0.7,
  "output_w": 9.17,
  "runtime_estimate_min": 600
}
```

## Fragmentation and coalescing

A single complete response can arrive in multiple callbacks. For the synthetic B-124 charging reply above, one possible split is:

```text
Notification 1: 43 06 12
Notification 2: 51 B8 00 00 00 0E 80
Notification 3: 8A 8A 8A 00 23 28 02 08 31 38 01 00 00
```

Accumulate bytes before interpreting fields. If two complete replies arrive in one callback, consume the first complete frame and continue with the remainder; do not split at every apparent header inside a payload. Legacy length is byte 2 + 5; BP100 length is LE16 at 4 + 12; standard PC8 length is byte 4 + 7, ending in `0A 0D`. BI word 32 is 17 bytes; words 33-35 are 16 bytes. Reset the buffer and identity gate on reconnect.

## What is not a handshake or setting recipe

Legacy unsolicited command `71` is connection-ready, not a status reply; it does not replace `52` identification or contain established charge/temperature fields. Manufacturer apps may perform extra reads or binding steps. The examples do not change identity, binding, firmware or battery settings.

Known configuration layouts are documented separately in [BlackVue settings](../docs/blackvue-legacy.md#configuration-commands) and [Neo+ configuration](../docs/cellink-neo-plus.md#configuration-protocol). Those source-derived writes have different model/firmware limits from the hardware-observed telemetry. Read supported/locked masks where specified; a shared status format does not make a setting command compatible. BP100 additional command identifiers have incomplete payload/acknowledgement specifications, and Cellink Neo-specific configuration remains unknown. Do not turn a known command number into a guessed empty write.

Reported capacity is configured, not battery health or measured usable energy. Reported runtime is an estimate, and zero runtime without load is not evidence of an empty battery. A zero charging-mode discharge-current field can be an unavailable load measurement, not zero actual consumption. See [client implementation guidance](../docs/methodology.md) and each model's reference for framing, checksums, unknowns and evidence limits.

This page is generated from the two JSON files by `python3 scripts/render_examples.py`. Validation checks its exact consistency with those files.
