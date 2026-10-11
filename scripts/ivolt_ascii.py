#!/usr/bin/env python3
"""Independent strict offline iVolt reference decoder, not hardware acceptance."""
import re


def build_reply(command, fields):
    """Build synthetic public CONT/DAT examples only, never settings replies."""
    if command == 'CONT':
        if fields:
            raise ValueError('CONT has no fields')
        prefix = b'S00,CONT,'
    elif command in ('DAT1', 'DAT2', 'DAT3'):
        text = ','.join(fields)
        if len(text) > 29:
            raise ValueError('Field length outside reviewed native window')
        prefix = f'S{len(text):02d},{command},{text},'.encode('ascii')
    else:
        raise ValueError('Not a public synthetic reply command')
    return prefix + f'{sum(prefix) % 256:02x}E\r\n'.encode('ascii')


def decode(packet):
    """Return allowlisted fields only; GET/unknown raw bodies never escape."""
    if not re.fullmatch(rb'S[0-2][0-9],[A-Z0-9]{4},[^\r\n]*[0-9a-f]{2}E\r\n', packet):
        raise ValueError('ASCII frame syntax')
    n = int(packet[1:3])
    command = packet[4:8].decode('ascii')
    if len(packet) != n + (14 if command == 'CONT' else 15):
        raise ValueError('Length window')
    if packet[-5:-3] != f'{sum(packet[:-5]) % 256:02x}'.encode('ascii'):
        raise ValueError('Additive checksum')
    if command == 'CONT':
        if n != 0 or packet[:9] != b'S00,CONT,':
            raise ValueError('CONT shape')
        return {'control': 'CONT'}
    if command not in ('DAT1', 'DAT2', 'DAT3'):
        return {'withheld': True}
    if packet[-6] != 44:
        raise ValueError('Missing field terminator')
    text = packet[9:-6].decode('ascii')
    fields = text.split(',')
    if len(text) != n or len(fields) != (4 if command == 'DAT2' else 3):
        raise ValueError('DAT field shape')
    for index, field in enumerate(fields):
        if command == 'DAT3' and index == 0 and field == 'FFFF':
            continue
        if not re.fullmatch(r'[0-9]+', field):
            raise ValueError('Decimal integer required')
    if command == 'DAT1':
        iv, ov, soc = map(int, fields)
        if not 0 <= soc <= 100:
            raise ValueError('SOC bounds')
        return {'input_v': iv / 10, 'output_v': ov / 10, 'charge_percent': soc}
    if command == 'DAT2':
        temp, state, acc, current = map(int, fields)
        values: dict[str, object] = {'temperature_raw': temp, 'temperature_c': temp % 100 if temp >= 100 else -temp,
                  'state_code': state, 'acc_raw': acc, 'input_current_raw': current}
        values['input_current_available'] = current != 9900
        if current != 9900:
            values['input_a'] = current / 1000
        else:
            values['input_current_special'] = '9900_unresolved_native_13A_display'
        return values
    raw, discharge, charge = fields
    values = {'output_current_raw_text': raw, 'runtime_estimate_min': int(discharge),
              'time_to_full_min': int(charge), 'output_current_available': raw not in ('0000', 'FFFF') and int(raw) != 9900}
    if raw in ('0000', 'FFFF'):
        values['output_current_sentinel'] = raw
    elif int(raw) == 9900:
        values['output_current_special'] = '9900_unresolved_native_13A_display'
    else:
        values['output_a'] = int(raw) / 1000
    return values


class Stream:
    """Bounded per-connection synthetic stream replay with strict framing."""
    def __init__(self):
        self.buffer = bytearray()

    def reset(self):
        self.buffer.clear()

    def feed(self, chunk):
        # Process incrementally so large coalesced input cannot grow the buffer.
        output = []
        for byte in chunk:
            self.buffer.append(byte)
            while self.buffer:
                if self.buffer[0] != ord('S'):
                    del self.buffer[0]
                    continue
                if len(self.buffer) < 9:
                    break
                if not re.fullmatch(rb'S[0-2][0-9],[A-Z0-9]{4},', self.buffer[:9]):
                    del self.buffer[0]
                    continue
                command = bytes(self.buffer[4:8])
                size = int(self.buffer[1:3]) + (14 if command == b'CONT' else 15)
                if len(self.buffer) < size:
                    break
                packet = bytes(self.buffer[:size])
                try:
                    values = decode(packet)
                except ValueError:
                    del self.buffer[0]
                    continue
                del self.buffer[:size]
                output.append(values)
        return output
