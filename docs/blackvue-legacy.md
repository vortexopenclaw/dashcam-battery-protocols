# BlackVue B-124 / B-130A wire protocol

The [original Cellink Neo6](cellink-neo6.md) firmware1.52 also uses this transport and classic map. Its own identity/firmware gate and evidence limits remain separate from BlackVue variants.

Evidence: manufacturer-implementation analysis plus hardware observations on B-124 firmware 1.44 and B-130A firmware 1.61. Firmware branches outside those two revisions are source-derived, not hardware-tested here. See [sources](sources.md) and [methodology](methodology.md).

## GATT transport

| Role | UUID |
|---|---|
| Service | `0000fff0-0000-1000-8000-00805f9b34fb` |
| Battery to client | `0000fff1-0000-1000-8000-00805f9b34fb` |
| Client to battery | `0000fff2-0000-1000-8000-00805f9b34fb` |
| Client characteristic configuration descriptor | `00002902-0000-1000-8000-00805f9b34fb` |

The tested writer supports write without response. Check discovered properties rather than assuming write-with-response support. Enable notifications, or indications if that is what the selected characteristic supports, through its configuration descriptor. A successful GATT write does not prove that a battery accepted a command or returned status.

Device names are discovery hints. B-124 names can use a `B124` prefix; B-130A can use `130A` without a leading `B`. Device-specific suffixes are omitted from this reference. Accept returned model identity within the selected family before status polling; do not unlock B-124 status with a B-130 identity or vice versa.

## Request framing

```text
43 06 LL CC [payload] XX
```

`LL` is payload length, `CC` is command, and `XX` is the XOR of all preceding request bytes. Total wire length is `LL + 5`. The two supported zero-payload requests are:

| Command | Purpose | Complete request |
|---|---|---|
| `52` | Firmware/model | `43 06 00 52 17` |
| `51` | Battery status | `43 06 00 51 14` |

Subscribe, request firmware/model, verify the selected identity, then request status. A one-second status interval worked in the tested client; it is an implementation choice, not a known battery limit. Bound identification retries and stop on an unsupported identity or connection failure.

## Response framing

Replies use the same header, length byte and command position. Reassemble notifications into a byte stream: wait for `LL + 5` bytes, consume one frame, and retain any remaining bytes for the next frame. One callback can contain a fragment or more than one frame. Reset incomplete stream state on a new connection.

Incoming trailer/checksum semantics are **unverified**. Observed connection-ready replies do not satisfy the request XOR rule, and the inspected manufacturer receive path does not validate a received checksum. Document a trailer byte without treating it as a validated checksum. The manufacturer implementation allocates extra padding internally; use observed wire length rather than exporting that padding.

| Command | Observed length | Meaning |
|---|---|---|
| `71` | 5 bytes, payload length 0 | Connection ready; contains no measurements |
| `52` | 17 bytes, payload length 12 | Firmware/model identity |
| `51`, B-124 1.44 | 23 bytes, payload length 18 | Classic status |
| `51`, B-130A 1.61 | 29 bytes, payload length 24 | Extended status |

Those lengths apply to the named firmware revisions, not every variant. Repeated `71` messages indicate connection readiness, not a status reply.

## Firmware reply (`52`)

Offsets are zero-based from the start of the complete frame. Multi-byte integers are unsigned big-endian.

| Offset | Bytes | Field | Interpretation |
|---|---|---|---|
| 4 | 2 | Firmware revision | `144` → `1.44`; `161` → `1.61` |
| 10 | 6 | Model | ASCII, trim trailing NUL/space |

Observed model strings are `B-124` and `B-130A`. Manufacturer-source identity handling also includes `B-124X` and `B-130X`; those are not separate hardware-tested models in this dataset. Do not substitute `B-130X` for an observed `B-130A` identity.

## Status reply (`51`)

The following map combines manufacturer-derived offsets with hardware replay. Firmware revision is the integer from the identity reply, not a floating-point version.

| Offset | Bytes | Field | Decode |
|---|---|---|---|
| 4 | 1 | Charge percent | Raw byte; subtract 100 for revision ≥110 |
| 5 | 2 | Discharge runtime estimate | Minutes, big-endian |
| 7 | 2 | Time to full | Minutes, big-endian |
| 9 | 1 | Temperature | Formula below, °C |
| 10 | 1 | Internal battery voltage | Byte / 10, V |
| 11 | 1 | Classic input voltage | Byte / 10, V; revision <160 |
| 12 | 1 | Classic output voltage | Byte / 10, V; revision <160 |
| 13 | 1 | ACC voltage raw field | Source-derived; scale/meaning not hardware-validated here |
| 14 | 2 | Input current | Big-endian / 1000, A |
| 16 | 2 | Output current | Big-endian / 1000, A |
| 18 | 2 | Reported configured capacity | Big-endian, mAh |
| 20 | 1 | State/configuration bits | Preserve byte; low nibble is raw state |
| 21 | 1 | Settings bits | Source-derived; not decoded in this telemetry reference |
| 22 | 1 | Extended USB connection field | Revision ≥160; source-derived, semantics unvalidated |
| 23 | 2 | Extended input voltage | Big-endian / 10, V; revision ≥160 |
| 25 | 2 | Extended output voltage | Big-endian / 10, V; revision ≥160 |
| 27 | 1 | Extended flag field | Present in 29-byte replies; preserve as unknown |

Offset 22 is the trailer on the classic 23-byte frame, not a USB field. Read it as a field only on an extended reply. On the observed 29-byte reply, offset 28 is the trailer. Require enough payload bytes for the selected firmware layout before accessing its extended fields.

For temperature byte `T`:

```text
T >= 100:             T - 100
T < 100, revision>=110: 15 - T
T < 100, revision<110:  -T
```

The tested positive temperatures corroborate the first branch. Other temperature/older-firmware branches follow the inspected manufacturer implementation and synthetic fixtures.

## State interpretation

| Low nibble | Working interpretation | Evidence |
|---|---|---|
| 0 | Stopped / transition | Observed during B-130A charging-to-discharge transition |
| 1 | Charging | Observed on both models with positive input current |
| 2 | Fully charged, unless input is active | Manufacturer-derived; not a full-charge hardware acceptance here |
| 3 | Discharging | Observed on both models |
| Other | Preserve raw code; unknown/protection-related | No complete hardware-validated mapping |

The manufacturer UI interprets state 2 with positive input current or voltage as charging. Extended-firmware protection interpretation can depend on input voltage; do not collapse every remaining nibble into a known alarm. Keep raw bits available for future evidence.

## Units and estimates

Some manufacturer screens label current `Ah`; the implementation scales these fields by 1000, yielding A. Power is calculated from voltage/current. The runtime field is the raw battery estimate, independent of manufacturer UI averaging. See the [B-124](b124.md) and [B-130A](b130a.md) model-specific layouts.

## Configuration commands

Source-derived from BlackVue Android 3.60; these writes remain unverified on hardware. Requests use the same `43 06 LL CC payload XOR` framing.

| Command | Payload | Meaning |
| --- | --- | --- |
| `64` | One byte, 0 or 1 | Beep disabled/enabled |
| `6A` | Two-byte unsigned big-endian mAh | Configured battery capacity, B-124/B-124X app path |

The native app waits for a reply carrying the matching command, then queries status `51`. Its B-124/B-124X save flow sends `64` followed by `6A`; other model paths do not automatically send capacity. Preserve model-specific limits. Neo 6 settings compatibility and full acknowledgement payload/persistence behavior remain unspecified.
