#!/usr/bin/env python3
"""Render readable exchanges from canonical synthetic fixtures and session references."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INTRO = '''# Example Bluetooth conversations

[vectors.json](vectors.json) contains individual machine-readable request/response fixtures. [exchanges.json](exchanges.json) connects them into model-specific initialization and charging/discharging sequences. This page shows those bytes with direction and decoded fields.

**All RX values are invented.** These are independent illustrations, not raw captures or one continuous charging-to-discharge recording. Legacy/ITSC trailer bytes and incoming BP100 CRC fields are unverified zero placeholders. PC8 PIN/reserved bytes are zeroed. iVolt CONT is independently checksum-generated; DAT groups are source-derived with no physical telemetry acceptance. Its response checksums are computed sums; its native DATA/GET1 requests contain two spaces and CR/LF. GET replies are omitted. TX examples are documented read-only requests; never transmit an RX fixture to a battery.

## Start every connection this way

1. Connect to the intended device and discover its actual service/characteristic properties. Advertised names and similar UUIDs are hints, not model/firmware verification.
2. Enable notification delivery on the listed response characteristic. For its standard CCCD `00002902-0000-1000-8000-00805f9b34fb`, notification-enable value is `01 00`; if the discovered property is indications instead, use `02 00`. This is a GATT descriptor write, not a packet sent to the query writer. Await subscription completion before querying.
3. For iVolt, follow the separate CONT-triggered DATA sequence below; no model/firmware identity query is established. For other models, send the model's identification query and reassemble the reply. Verify the expected model/firmware or application mode before status queries. These query/reply steps are the initialization exchange, not proof that a separate pairing/authentication protocol is absent.
4. Serialize operations and match response command/shape. A write-without-response has no ATT acknowledgement; local write acceptance is not an application reply. Preserve timeouts and unknown replies rather than manufacturing telemetry. Do not repeatedly read a notify response stream as a substitute for subscribing.
5. Repeat established status queries conservatively; no periodic iVolt polling recipe is established here. On disconnect discard partial frames, reconnect and repeat the model-specific subscription/initialization gates. Independent groups need independent timestamps; old cached fields are not live measurements.

`TX` means client to battery through the listed writer. `RX` means the reassembled battery-to-client notification/indication frame, not necessarily one radio notification. Decoded blocks show selected expected fields, with units in names (`_v`, `_a`, `_w`, `_min`, `_mah`, `_c`). Watts are volts × amps, not a separate measured-energy claim.
'''

ENDING = '''
## Fragmentation and coalescing

A single complete response can arrive in multiple callbacks. For the synthetic B-124 charging reply above, one possible split is:

```text
{fragments}
```

Accumulate bytes before interpreting fields. If two complete replies arrive in one callback, consume the first complete frame and continue with the remainder; do not split at every apparent header inside a payload. Legacy length is byte 2 + 5; BP100 length is LE16 at 4 + 12; standard PC8 length is byte 4 + 7, ending in `0A 0D`. BI word 32 is 17 bytes; words 33-35 are 16 bytes. iVolt ordinary wire length is decimal nn + 15; CONT is special nn + 14, ending in `0D 0A` (CR then LF). Reset the buffer and identity gate on reconnect.

## What is not a handshake or setting recipe

Legacy unsolicited command `71` is connection-ready, not a status reply; it does not replace `52` identification or contain established charge/temperature fields. Manufacturer apps may perform extra reads or binding steps. iVolt CONT likewise is control, not a measurement or firmware identity; only DAT groups can refresh their own measurement timestamps. GET1 is a privacy-sensitive password/settings read, not a measurement request; omit its raw reply from logging/export. The examples do not change identity, binding, firmware or battery settings.

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
        if session['profile'] == 'ivolt-xtra':
            lines += ['', '### Control-triggered read-only handshake']
            for response_id, request_id in session['control']:
                response, request = responses[response_id], requests[request_id]
                lines += ['', '```text', 'RX [' + response_id + ']: ' + response['hex'],
                          'TX [' + request_id + ']: ' + request['hex'],
                          'ASCII TX: ' + repr(bytes.fromhex(request['hex']).decode('ascii')), '```']
            request = requests[session['private_read_request']]
            lines += ['', '### Native privacy-sensitive read, not a measurement query', '',
                      '```text', 'TX [' + request['id'] + ']: ' + request['hex'],
                      'ASCII TX: ' + repr(bytes.fromhex(request['hex']).decode('ascii')), 'RX: withheld password/settings reply; deliberately no raw example', '```']
            for phase, response_ids in session['stream'].items():
                lines += ['', '### Source-derived ' + phase.replace('_', ' ') + ' illustrations', '',
                          'No physical DAT telemetry acceptance. These groups are not individual DATA polls.']
                for response_id in response_ids:
                    response = responses[response_id]
                    lines += ['', '```text', 'RX [' + response_id + ']: ' + response['hex'],
                              'ASCII RX: ' + repr(bytes.fromhex(response['hex']).decode('ascii')), '```', '',
                              'Selected decoded fields:', '', '```json', json.dumps(response['expected'], indent=2), '```']
            continue
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Check generated output without writing')
    args = parser.parse_args()
    text = render(vectors, exchanges, profiles)
    path = ROOT / 'examples/communication.md'
    if args.check:
        if path.read_text() != text:
            raise SystemExit('Communication guide stale; run scripts/render_examples.py')
        print('PASS: communication guide matches canonical JSON')
    else:
        path.write_text(text)

if __name__ == '__main__':
    main()
