# Thinkware iVolt XTRA / BAB-95

Status: **hardware-corroborated charging and loaded-discharge telemetry, DAT1/DAT2/DAT3 and DATA-only startup**. DAT field groups and the read-only handshake below come from offline review of THINKWARE iVolt Android **1.1.7**, package `com.thinkware.ivolt`. Battery firmware and returned model identity remain unknown. iVolt Mini / BAB950 is excluded.

## Evidence and provenance

The [official app compatibility guide](https://support.thinkware.com/hc/en-us/articles/360045289593-Which-Thinkware-Mobile-App-do-I-use) maps iVolt Xtra to this package and lists percentage, status, temperature, input/output voltage/current and charge/discharge estimates. The [official installation/app guide](https://support.thinkware.com/hc/en-us/articles/16357652595859-How-to-Install-the-iVolt-Xtra-Battery-Pack) identifies BAB-95. These primary sources establish product/app context, not an official wire specification. The Play listing also uses the label iVolt PRO for BAB-95; that label does not establish compatibility with every revision.

Protocol facts are independently described from the compatible native app's transport, receive/parser and display paths. The inspected base APK SHA256 is `c3e87c1380f8463aa4e68d3048b58bb3cc5f59fa0a65938c077ea71ed8191461`; it was privately obtained from a third-party mirror, not directly from Play. Artifact hash/signature checks do not independently establish a manufacturer delivery chain. No APK, manufacturer source, private capture or owner identifier is redistributed. See [sources](sources.md#thinkware-ivolt-xtra).

Hardware evidence corroborates these protocol behaviors:

- FFF1/FFF2 transport, CONT handling and DATA-only startup without GET1.
- Continuing DAT1/DAT2/DAT3 groups, charging state 1 and loaded-discharge state 3, with transitions in both directions.
- SOC, voltage and ordinary current decoding, positive temperature and device-reported minute estimates.
- Charging-mode zero output-current sentinel interpreted as unavailable output current/power, not zero attached-load consumption.
- Strict production-parser acceptance of CONT and DAT responses, including its length, field and additive-checksum checks.

This corroborates the source-derived map through production decoder records. Raw reply bytes were not retained, so there is no independent raw-packet checksum replay or calibration claim. Firmware and returned model identity remain unknown; this is not support for every revision. All public examples remain synthetic, not published hardware packets or native-app equivalence tests.

## Discovery and transport

The observed advertised name is `IVT-` followed by four hexadecimal characters, case-insensitively. This is only a discovery hint. Keep its device-specific suffix private; do not treat it as returned model identity or authentication.

Short UUIDs expand to `0000xxxx-0000-1000-8000-00805f9b34fb`.

| Service | Characteristic | Observed properties | Reviewed use |
| --- | --- | --- | --- |
| `FFF0` | `FFF1` | Read + notify (`0x12`) | Native ASCII response notifications, including corroborated CONT and DAT1-3 |
| `FFF0` | `FFF2` | Write without response (`0x04`) | Native DATA and GET1 requests |
| `FF12` | `FF01` | Write without response (`0x04`) | Not the reviewed native telemetry writer; semantics unknown |
| `FF12` | `FF02` | Notify (`0x10`) | Not the reviewed native telemetry reader; semantics unknown |
| `FF12` | `FF03` through `FF0A` | Read + write (`0x0A`) | Unmapped readable/settings values; do not infer safe writes |

The inspected native callbacks do not establish descriptor-completion serialization before the first request. Do not copy that timing limitation. Discover actual properties. Enable FFF1 local notification delivery and write CCCD `2902` with `01 00`; await subscription completion before FFF2 writes. Do not repeatedly read the response stream. Write-without-response has no ATT acknowledgement; local write success is not telemetry acceptance. Standard Device Information values may contain private identifiers and are not a firmware specification here.

## Read-only DATA handshake

1. Connect to the intended iVolt XTRA, discover FFF0/FFF1/FFF2 and complete notification subscription. Keep stream buffers, queues and connection generations per device.
2. Reassemble and strictly validate the unsolicited **CONT** control frame. CONT is a control signal, not SOC, heartbeat measurement, model identity or firmware identification.
3. Answer a valid CONT on FFF2 with the exact native ASCII/UTF-8 literal below. There are **two ASCII spaces** before `E`, then **CR followed by LF**. They are not checksum digits. Do not trim, substitute a calculated checksum or reverse the terminator.

```text
S00,DATA,  E\r\n
```

4. Await actual DAT groups. The native app's CONT branch calls its verification helper and sends DATA even if that helper marked a checksum mismatch. A new client should instead require a valid CONT before replying, serialize writes, bound retries and avoid an unbounded write for every duplicate control.
5. Preserve DATA acknowledgement/control separately from DAT1/DAT2/DAT3 measurements. DATA-only startup and continuing DAT groups without GET1 are hardware-corroborated. Group cadence of approximately five seconds was observed, not a hard interval, timeout or retry limit. No established ACK payload or periodic polling recipe is specified here. Continued CONT without DAT is not telemetry readiness.

This is a read-only protocol request carried by a GATT write, not permission to configure the battery. Do not send PowerCell 8 `@@` or BlackVue `43 06` queries just because UUIDs overlap. OEM/common-firmware attribution remains unknown.

## GET1 and privacy

The native view-creation path calls the following read request; the writer does nothing if FFF2 is not yet available. View creation therefore does not prove an on-wire request. The first native PRC receive path also schedules GET1 once, independently of the PRC/UI checksum-gated connection-ready branch. It is not a periodic request after every DAT group or a returned firmware gate.

```text
S00,GET1,  E\r\n
```

Again, two spaces precede `E`, followed by CR/LF. GET replies populate **password and settings**, including charging/password enable flags, connection type, configured capacity/model, input/charging selections and additional-battery selection. An ERR branch exists. These are settings readbacks, not measured capacity, health or identity proof. This reference does not publish a GET reply, even with a dummy password, or a settings-write recipe.

**Withhold GET and unknown raw response payloads from diagnostic logs, exports, cloud capture and crash reports.** Filter before persistence, not only before rendering. A telemetry-only client should avoid GET1 unless necessary under an explicit privacy policy; a read-only request can still disclose a credential. No SET, binding, password mutation, reset or OTA command is authorized by the DATA handshake.

## ASCII response framing and checksum

Ordinary source-consistent measurement frame:

```text
Snn,COMMAND,fields,hhE\r\n
```

- `S` is ASCII `53`; `nn` is two **decimal** digits. The reviewed native parser accepts lengths `00` through `29`.
- `COMMAND` is four ASCII characters, specifically DAT1, DAT2 or DAT3 for the mapped groups. Do not use substring command matching.
- `fields` is comma-separated ASCII field text. `nn` is its byte length including internal commas, excluding the comma immediately before `hh`. This follows the native length arithmetic and is corroborated by strict production-parser DAT acceptance, not independent raw replay.
- All ordinary mapped fields are decimal integers, not hexadecimal, except the exact output-current sentinel text `FFFF`. Preserve the exact text distinction for `0000`.
- `hh` is the two-digit **lowercase ASCII hexadecimal** encoding of the sum modulo 256 of every prefix byte through the comma immediately before `hh`. Include `S`, the length digits, command and commas. Exclude `hh`, `E`, CR and LF. This is an additive checksum, not a polynomial CRC.
- Native ordinary verification window is `nn + 13` bytes, ending in `E`, excluding CR/LF. The full wire frame is `nn + 15` bytes.

CONT is special, without a separate fields/terminating-comma pair:

```text
S00,CONT,hhE\r\n
```

Its native verification window is `00 + 13 - 1 = 12` bytes and the wire frame is 14 bytes. The synthetic CONT example independently computes its checksum from the public command prefix, not from an owner packet. Request literals with two spaces are a separate grammar; do not run response checksum generation on them.

### Native acceptance discrepancy

The reviewed checksum helper sets a shared flag false on mismatch. DAT setters then run and return **before any flag gate**. Only a later PRC/UI/connection-ready path checks the flag; its mismatch branch resets it. The CONT branch sends DATA regardless of that flag. Do not claim that the native app universally rejects invalid-checksum DAT or CONT frames.

**Recommended strict-client policy:** require exact length, command, field count, ASCII integer syntax, terminator and checksum before accepting a DAT measurement or reacting to CONT. This deliberately differs from the native acceptance path. It is not evidence that all firmware sends correct DAT checksums. Revisit the policy with sanitized hardware evidence if a firmware differs; never silently make invalid traffic fresh telemetry.

Accumulate fragments and preserve coalesced leftovers. BLE callback boundaries are not frame boundaries. Bound memory and resynchronize at a validated header; do not copy the native fixed-buffer/discard behavior. Require CR/LF for these public fixtures while recognizing that the native verification window itself excludes them. Reset partial frames, readiness and freshness on reconnect.

## Measurement groups and hardware scope

Field positions below start after `COMMAND`; native comma-split indices are 2 onward. The native map is corroborated for ordinary charging/loaded-discharge telemetry, not every branch. These are not an atomic snapshot.

| Command | Fields in order | Interpretation |
| --- | --- | --- |
| DAT1 | input voltage, output voltage, SOC | Voltages: integer / 10 V; SOC: percent |
| DAT2 | encoded temperature, charging state, ACC status, input current | Temperature rule below; preserve raw state/ACC; ordinary current / 1000 A |
| DAT3 | output current, discharge time, charge time | Ordinary current / 1000 A; both time estimates in minutes; sentinel rules below |

No firmware, authenticated model identity, measured capacity or battery health field is established in these groups. ACC is a raw status integer; do not infer its complete polarity/protection semantics.

### State and temperature

Source-derived native presentation:

| Raw state | Native presentation |
| --- | --- |
| 0 | Standby; initial standby state hardware-corroborated |
| 1 | Charging; charge-time estimate displayed; hardware-corroborated |
| 2 | Charge/full presentation; source-derived only |
| 3 | Discharging; discharge-time estimate displayed; loaded discharge hardware-corroborated |

These are not complete protection/fault semantics. Preserve unknown raw states without inventing labels. Encoded temperature `t >= 100` displays positive `t % 100` degrees C; positive temperature is hardware-corroborated, not independently calibrated; `t < 100` displays negative `t` degrees C. This negative branch is source-derived, not physically corroborated. Do not substitute another family's temperature formula.

### Current availability and presentation

- DAT3 output-current text exactly `0000` or `FFFF` makes native supported-device false and stores output current zero. Preserve the raw sentinel and mark output current/power **unavailable**, not a measured zero load. Do not automatically interpret every differently spelled decimal zero as the same sentinel.
- The charging-mode zero/unavailable output-current behavior is hardware-corroborated through production decoding. Exact sentinel-text semantics come from source review; `FFFF` remains source-derived only without retained raw replay.
- Ordinary input/output currents are mA and are hardware-corroborated in charging/loaded discharge, not independently calibrated. Native display uses integer mA below 1000 and truncates to one decimal A at/above 1000. Keep numerical precision in a decoder; presentation rounding is not protocol scaling.
- The shared native current formatter treats raw **9900** specially as **13 A**, not 9.9 A. Its meaning is unresolved and this branch remains source-derived, not hardware-observed. Preserve raw 9900 and flag it as special/unresolved instead of publishing 9.9 A or a calibrated 13 A measurement. This formatter can affect either current display.
- Calculate watts only from available, ordinary voltage/current fields with compatible freshness. Label `V × A` as calculated; do not calculate with sentinels or unresolved 9900.

### Time, smoothing and freshness

Charge and discharge values are minute estimates, not observed parking duration. Native discharge presentation caps at 99:59; preserve larger raw minute values rather than treating this UI cap as a protocol limit. SOC and each time array accept the first value, then sort batches of 12 and use index 6 before clearing and repeating. This upper-middle batch selection is native display smoothing, not wire scaling or an average of the two middle values.

State transitions can retain old numeric values for one group cycle, including input current and runtime. Do not treat a new state as an atomic refresh of all fields or a lingering input current as definitive charging activity. A client may expose unsmoothed values with timestamps. Timestamp DAT1, DAT2 and DAT3 independently; a fresh DAT1 cannot refresh an old current, state or runtime. CONT, DATA acknowledgement, GET, PRC and unknown traffic must not refresh measurement timestamps. On timeout/disconnect keep historical values explicitly stale, not live. Do not infer depletion, camera shutdown, health or expansion capacity from gaps or zero estimates.

## Examples, tests and remaining limits

[Machine-readable vectors](../examples/vectors.json), [exchange sequences](../examples/exchanges.json) and the [generated guide](../examples/communication.md) contain independently constructed ASCII requests/control and invented DAT groups. Ordinary charging/loaded-discharge examples illustrate hardware-corroborated interpretations with invented values; they are not physically captured packets. Full, negative temperature, FFFF, special 9900 and alternative decimal-zero examples remain source-derived only. GET replies are omitted. The strict offline validator and stream tests exercise checksum/length/units, fragmentation/coalescing, privacy withholding and sentinel distinctions; they do not establish a working radio session.

Remaining unknowns: battery firmware/model identity, wider authentication requirements, independent raw DAT/checksum replay, measurement and usable-capacity calibration, polling/retry limits, complete protection/fault/full behavior, complete ACK/PRC/settings semantics, negative temperature, FFFF, special 9900 meaning and other iVolt revisions. DATA-only acceptance does not authorize GET1 or settings writes. No borrowed PC8 packets, manufacturer implementation, private logs or owner identifiers are included. See the [profile](../profiles/ivolt-xtra.json) and [implementation guidance](methodology.md).
