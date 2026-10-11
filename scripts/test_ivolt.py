#!/usr/bin/env python3
"""Offline regression tests; invented frames never establish physical acceptance."""
import json
from pathlib import Path
import unittest
from ivolt_ascii import Stream, build_reply, decode

ROOT = Path(__file__).resolve().parents[1]


class IvoltTests(unittest.TestCase):
    def setUp(self):
        self.rows = [row for row in json.loads((ROOT / 'examples/vectors.json').read_text())['responses']
                     if row['protocol'] == 'ivolt_ascii']
        self.packets = [bytes.fromhex(row['hex']) for row in self.rows]

    def reject(self, packet):
        with self.assertRaises(ValueError):
            decode(packet)

    def test_independent_checksum_and_expected_fields(self):
        # Compute from public prefix facts, not private capture bytes.
        prefix = b'S00,CONT,'
        checksum = format(sum(prefix) & 255, '02x').encode('ascii')
        self.assertEqual(self.packets[0], prefix + checksum + b'E\r\n')
        for row, packet in zip(self.rows, self.packets):
            self.assertEqual(decode(packet), row['expected'])
            self.assertEqual(packet[-5:-3], format(sum(packet[:-5]) & 255, '02x').encode('ascii'))

    def test_every_fragment_boundary_and_coalescing(self):
        for packet, row in zip(self.packets, self.rows):
            for index in range(1, len(packet)):
                stream = Stream()
                self.assertEqual(stream.feed(packet[:index]), [])
                self.assertEqual(stream.feed(packet[index:]), [row['expected']])
                self.assertEqual(len(stream.buffer), 0)
        self.assertEqual(Stream().feed(b''.join(self.packets)), [row['expected'] for row in self.rows])

    def test_bytewise_noise_bounded_memory_and_reconnect(self):
        stream = Stream()
        self.assertEqual(stream.feed(b'x' * 10000), [])
        self.assertLessEqual(len(stream.buffer), 44)
        output = []
        for byte in b''.join(self.packets):
            output += stream.feed(bytes([byte]))
        self.assertEqual(output, [row['expected'] for row in self.rows])
        stream.feed(self.packets[1][:10])
        stream.reset()
        self.assertEqual(stream.feed(self.packets[1][10:]), [])
        self.assertEqual(stream.feed(self.packets[2]), [self.rows[2]['expected']])

    def test_bad_checksum_length_delimiters_and_terminator(self):
        packet = self.packets[1]
        for index in (0, 1, 2, 3, 8, len(packet)-6, len(packet)-5, len(packet)-4, len(packet)-3, len(packet)-2, len(packet)-1):
            bad = bytearray(packet)
            bad[index] ^= 1
            self.reject(bytes(bad))
        self.reject(packet[:-1])
        self.reject(packet + b'\x00')
        self.reject(packet[:-2] + b'\n\r')
        # Strict policy differs from native DAT setter acceptance.
        bad = packet[:-5] + b'00' + packet[-3:]
        self.reject(bad)
        self.assertEqual(Stream().feed(bad + packet), [self.rows[1]['expected']])

    def test_uppercase_checksum_rejected(self):
        packet = next(p for p in self.packets if any(c in b'abcdef' for c in p[-5:-3]))
        self.reject(packet[:-5] + packet[-5:-3].upper() + packet[-3:])

    def test_field_count_decimal_syntax_and_soc(self):
        for command, fields in [('DAT1', ['1', '2']), ('DAT1', ['1','2','101']),
                                ('DAT2', ['-3','1','0','0']), ('DAT2', ['FF','1','0','0']),
                                ('DAT3', ['ffff','0','0']), ('DAT3', ['1','2','3','4'])]:
            self.reject(build_reply(command, fields))
        with self.assertRaises(ValueError):
            build_reply('DAT1', ['1' * 30, '2', '3'])
        self.assertEqual(decode(build_reply('DAT2', ['125','9','2','0']))['state_code'], 9)

    def test_sentinels_special_currents_and_time_not_capped(self):
        for sentinel in ('0000', 'FFFF'):
            result = decode(build_reply('DAT3', [sentinel, '6000', '17']))
            self.assertFalse(result['output_current_available'])
            self.assertNotIn('output_a', result)
            self.assertEqual(result['runtime_estimate_min'], 6000)
        self.assertEqual(decode(build_reply('DAT3', ['0','0','0']))['output_a'], 0)
        self.assertNotIn('output_a', decode(build_reply('DAT3', ['9900','0','0'])))
        self.assertNotIn('input_a', decode(build_reply('DAT2', ['127','1','1','9900'])))
        self.assertEqual(decode(build_reply('DAT3', ['1234','0','0']))['output_a'], 1.234)

    def test_temperature_and_states(self):
        for encoded, expected in ((0,0),(7,-7),(99,-99),(100,0),(127,27),(201,1)):
            for state in range(4):
                result = decode(build_reply('DAT2', [str(encoded),str(state),'0','0']))
                self.assertEqual(result['temperature_c'], expected)
                self.assertEqual(result['state_code'], state)

    def test_privacy_no_public_get_replies(self):
        # Empty opaque bodies exercise withholding, not a password/settings example.
        for command in ('GET1', 'PRC1', 'DATA', 'HIDE'):
            prefix = ('S00,' + command + ',,').encode('ascii')
            packet = prefix + format(sum(prefix) & 255, '02x').encode('ascii') + b'E\r\n'
            self.assertEqual(decode(packet), {'withheld': True})
            self.assertEqual(Stream().feed(packet), [{'withheld': True}])
            with self.assertRaises(ValueError):
                build_reply(command, [])
        self.assertTrue(all(p[4:8] in (b'CONT', b'DAT1', b'DAT2', b'DAT3') for p in self.packets))

    def test_exact_read_only_requests(self):
        requests = json.loads((ROOT / 'examples/vectors.json').read_text())['requests']
        selected = [row for row in requests if row['protocol'] == 'ivolt_ascii']
        self.assertEqual({row['command'] for row in selected}, {'DATA', 'GET1'})
        for row in selected:
            self.assertEqual(bytes.fromhex(row['hex']), ('S00,' + row['command'] + ',  E\r\n').encode('ascii'))

    def test_coverage_and_privacy_cannot_be_promoted(self):
        import verify
        from unittest.mock import patch
        target = ROOT / 'profiles/ivolt-xtra.json'
        original_read = Path.read_text
        profile = json.loads(original_read(target))
        changes = [('coverage', 'hardware_telemetry'), ('tested_firmware', ['invented']),
                   ('physical_telemetry_accepted', True), ('capacity_semantics', 'configured_mah'),
                   ('incoming_checksum', 'unverified'), ('request_commands', ['DATA', 'SET1']),
                   ('unknown_raw_replies', 'log_raw')]
        for field, value in changes:
            modified = dict(profile, **{field: value})
            def read(path, *args, **kwargs):
                return json.dumps(modified) if path == target else original_read(path, *args, **kwargs)
            with patch.object(Path, 'read_text', read), self.assertRaises(ValueError):
                verify.main()

    def test_control_cannot_refresh_a_measurement(self):
        # Decoder emits neither measurements nor an identity from control/private traffic.
        self.assertEqual(decode(self.packets[0]), {'control': 'CONT'})
        groups = {b'DAT1': {'input_v','output_v','charge_percent'},
                  b'DAT2': {'temperature_c','state_code','acc_raw','input_a'},
                  b'DAT3': {'output_a','runtime_estimate_min','time_to_full_min'}}
        for packet in self.packets[1:]:
            decoded = decode(packet)
            for command, fields in groups.items():
                if command != packet[4:8]:
                    self.assertFalse(fields & decoded.keys())
            self.assertNotIn('firmware', decoded)
            self.assertNotIn('model', decoded)


def run_tests():
    result = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(IvoltTests))
    if not result.wasSuccessful():
        raise ValueError('iVolt offline regression failure')


if __name__ == '__main__':
    run_tests()
