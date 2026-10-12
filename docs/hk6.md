# VIOFO HK6 / HK6-F hardwire telemetry

HK6 is a hardwire power accessory that broadcasts vehicle-voltage information.
It is not a rechargeable battery pack. This reference covers passive Bluetooth
advertisements observed on **one HK6-F powering a T330W**. Accessory firmware is
unknown. HK6 and HK6-A advertise related manufacturer features, but their packet
compatibility with this layout remains unverified.

## Transport and discovery

- Observed Bluetooth name: `HK6`, including on the tested HK6-F.
- Non-connectable advertisements; no pairing, GATT connection, subscriptions or
  telemetry requests were needed for the observed fields.
- Manufacturer data: observed length **10 bytes** in the macOS CoreBluetooth
  `CBAdvertisementDataManufacturerDataKey` value. Offsets below include every
  byte in that value; do not strip its first two bytes before applying the map.
- Enable duplicate delivery and keep scanning. The initial discovery callback
  can contain no manufacturer data; absence in one callback is not evidence
  that the accessory lacks telemetry.
- Do not identify a device from the name alone. Multiple accessories can share
  that name. Bind observations to the selected local peripheral and preserve
  its identity privately. Cross-device identity matching is not documented.

These are broadcasts from the hardwire kit, not a camera connection. No HK6-F
command service or general camera-control API was established.

## Manufacturer-data field map

| Offset | Width | Field | Interpretation and evidence |
| --- | --- | --- | --- |
| 0 | 2 | Unresolved prefix | Treat as opaque. Company/model/device semantics unverified; do not use the observed prefix as a universal identification rule. |
| 2 | 2 | Battery input voltage | `b[2] + b[3] / 100` V; controlled supply changes and fixed-voltage ACC switching support this map. |
| 4 | 2 | ACC input voltage | `b[4] + b[5] / 100` V; repeatedly falls near zero with ACC off and rises with ACC on while battery supply stays fixed. |
| 6 | 1 | Unresolved state-associated byte | `0x0B` observed with ACC off / owner-confirmed parking, `0x0E` with ACC on / driving. Bit definitions and other states unknown. |
| 7 | 1 | Unknown | No semantic mapping established. |
| 8 | 2 | Unknown trailer | A checksum-like relationship exists in some frames but does not generalize. No validated checksum, endianness or counter interpretation. |

Voltage pairs use an integer byte plus fractional hundredths, not an ordinary
16-bit integer. Their roles are supported by controlled input changes and a
parking-driving-parking round trip on the tested unit. Precision of the format
does not establish sensor accuracy. Do not add an offset to force agreement
with a power-supply setpoint. Calibrated measurements at the kit inputs,
native-app comparison, wider ranges and other accessory revisions remain gaps.

ACC input state does not prove the dashcam is recording, that its card is
healthy, or which parking algorithm is running. A low ACC reading need not be
exactly zero. Thresholds, hysteresis and transition latency are not established.

## Synthetic decoding example

This invented example demonstrates offsets only. Prefix, state, reserved and
trailer bytes are zero placeholders. It is not a valid transmitter frame or
checksum fixture and must not be transmitted:

```text
00 00 0D 32 00 00 00 00 00 00
      ----- -----
      battery ACC
```

The battery field represents `13 + 50/100 = 13.50 V`; ACC represents `0.00 V`.
Do not use this example to infer device identity or status-byte semantics.

## Manufacturer-documented Bluetooth functionality

The [HK6-F product documentation](https://www.viofo.com/products/viofo-type-c-hk6-f-acc-hardwire-kit-for-t330-t340-support-parking-mode)
describes pairing-free voltage broadcasts and voltage stamps on recordings
for T330/T340. These features do not establish remotely writable settings.

The [HK6 app setup guide](https://www.viofo.com/blogs/viofo-car-dash-camera-guide-faq-and-news/bp100-hk6-dashcam-app-setup)
describes enabling **Show Voltage Value** in the VIOFO app's Help tab. Within
Bluetooth range, voltage remains available without a camera Wi-Fi connection
and even while the camera is off. Camera-off broadcast behavior is
manufacturer-documented, not independently exercised here.

Battery-pack capacity belongs to a BP100/BP60 integration, not an HK6 voltage
field. Mixed compatibility text on product pages does not establish identical
protocols across accessories. Use model-specific manuals and firmware notes.

## Remaining protocol and acceptance gaps

- Prefix meaning, reliable model matching, firmware identification and
  compatibility across HK6/HK6-A/HK6-F revisions.
- State bitfield, trailer/checksum rules, extra frame types and full raw
  advertising layout across host platforms.
- Input-voltage accuracy, fractional-byte limits, 24 V operation, ACC
  thresholds/hysteresis and time from an input change to its broadcast.
- Additional telemetry fields beyond input voltage and the observed status
  byte. Their presence and meaning remain unknown.
- Broadcast behavior during camera-off and accessory power restoration;
  association with multiple nearby kits and native-app selection behavior.
- Any remote configuration, firmware-update or control protocol. No write
  commands are documented for this accessory. Do not reuse BP100 commands.

Retain timestamps, raw unknown fields and stale/absent state in a local client.
Do not infer battery capacity, charge percentage, health or remaining runtime
from voltage alone. This is a public protocol reference, not a released HK6
integration or a ninth battery coverage profile.
