#!/usr/bin/env python3
"""Render readable exchanges from canonical synthetic fixtures and session references."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INTRO = '''# Example Bluetooth conversations

[vectors.json](vectors.json) contains individual machine-readable request/response fixtures. [exchanges.json](exchanges.json) connects them into model-specific initialization and charging/discharging sequences. This page shows those bytes with direction and decoded fields.

**All RX values are invented.** These are independent illustrations, not raw captures or one continuous charging-to-discharge recording. Legacy/ITSC trailer bytes and incoming BP100 CRC fields are unverified zero placeholders. PC8 PIN/reserved bytes are zeroed. TX examples are documented identification/status queries; never transmit an RX fixture to a battery.

## Start every connection this way

1. Connect to the intended device and discover its actual service/characteristic properties. Advertised names and similar UUIDs are hints, not model/firmware verification.
2. Enable notification delivery on the listed response characteristic. For its standard CCCD `00002902-0000-1000-8000-00805f9b34fb`, notification-enable value is `01 00`; if the discovered property is indications instead, use `02 00`. This is a GATT descriptor write, not a packet sent to the query writer. Await subscription completion before querying.
3. Send the model's identification query and reassemble the reply. Verify the expected model/firmware or application mode before status queries. These query/reply steps are the initialization exchange, not proof that a separate pairing/authentication protocol is absent.
4. Serialize operations and match response command/shape. A write-without-response has no ATT acknowledgement; local write acceptance is not an application reply. Preserve timeouts and unknown replies rather than manufacturing telemetry. Do not repeatedly read a notify response stream as a substitute for subscribing.
5. Repeat status queries conservatively. On disconnect discard partial frames, reconnect, subscribe and identify again. Independent groups need independent timestamps; old cached fields are not live measurements.

`TX` means client to battery through the listed writer. `RX` means the reassembled battery-to-client notification/indication frame, not necessarily one radio notification. Decoded blocks show selected expected fields, with units in names (`_v`, `_a`, `_w`, `_min`, `_mah`, `_c`). Watts are volts × amps, not a separate measured-energy claim.
'''

ENDING = '''
## Fragmentation and coalescing

A single complete response can arrive in multiple callbacks. For the synthetic B-124 charging reply above, one possible split is:

```text
{fragments}
```

Accumulate bytes before interpreting fields. If two complete replies arrive in one callback, consume the first complete frame and continue with the remainder; do not split at every apparent header inside a payload. Legacy length is byte 2 + 5; BP100 length is LE16 at 4 + 12; standard PC8 length is byte 4 + 7, ending in `0A 0D`. BI word 32 is 17 bytes; words 33-35 are 16 bytes. Reset the buffer and identity gate on reconnect.

## What is not a handshake or setting recipe

Legacy unsolicited command `71` is connection-ready, not a status reply; it does not replace `52` identification or contain established charge/temperature fields. Manufacturer apps may perform extra reads or binding steps. The examples do not change identity, binding, firmware or battery settings.

Known configuration layouts are documented separately in [BlackVue settings](../docs/blackvue-legacy.md#configuration-commands) and [Neo+ configuration](../docs/cellink-neo-plus.md#configuration-protocol). Those source-derived writes have different model/firmware limits from the hardware-observed telemetry. Read supported/locked masks where specified; a shared status format does not make a setting command compatible. BP100 additional command identifiers have incomplete payload/acknowledgement specifications, and Cellink Neo-specific configuration remains unknown. Do not turn a known command number into a guessed empty write.

Reported capacity is configured, not battery health or measured usable energy. Reported runtime is an estimate, and zero runtime without load is not evidence of an empty battery. A zero charging-mode discharge-current field can be an unavailable load measurement, not zero actual consumption. See [client implementation guidance](../docs/methodology.md) and each model's reference for framing, checksums, unknowns and evidence limits.

This page is generated from the two JSON files by `python3 scripts/render_examples.py`. Validation checks its exact consistency with those files.
'''

def render(vectors, exchanges, profiles):
    requests = {row['id']: row for row in vectors['requests']}
    responses = {row['id']: row for row in vectors['responses']}
    lines = [INTRO.rstrip()]
    for session in exchanges['sessions']:
        lines += ['', '## ' + session['title'], '', '[Protocol reference](../' + profiles[session['profile']]['reference'] + ').', '',
                  '- Service: `' + session['service'] + '`', '- Writer: `' + session['writer'] + '`',
                  '- Response: `' + session['response'] + '`', '- TX mode: ' + session['write_mode'] + '.', '', session['notes']]
        for phase, title in [('identity', 'Identification / initialization'), ('charging', 'Charging illustration'), ('discharging', 'Discharging illustration'), ('no_load', 'Input off, zero-load illustration')]:
            if phase not in session:
                continue
            lines += ['', '### ' + title]
            for request_id, response_id in session[phase]:
                request, response = requests[request_id], responses[response_id]
                lines += ['', '```text', 'TX [' + request_id + ']: ' + request['hex'], 'RX [' + response_id + ']: ' + response['hex'], '```', '', 'Selected decoded fields:', '', '```json', json.dumps(response['expected'], indent=2), '```']
    packet = bytes.fromhex(responses['b124_charging']['hex'])
    chunks = [packet[:3], packet[3:10], packet[10:]]
    fragments = '\n'.join(f'Notification {index + 1}: {chunk.hex(" ").upper()}' for index, chunk in enumerate(chunks))
    return '\n'.join(lines) + '\n' + ENDING.replace('{fragments}', fragments)

def main():
    vectors = json.loads((ROOT / 'examples/vectors.json').read_text())
    exchanges = json.loads((ROOT / 'examples/exchanges.json').read_text())
    profiles = {row['id']: row for row in (json.loads(path.read_text()) for path in (ROOT / 'profiles').glob('*.json'))}
    (ROOT / 'examples/communication.md').write_text(render(vectors, exchanges, profiles))

if __name__ == '__main__':
    main()
