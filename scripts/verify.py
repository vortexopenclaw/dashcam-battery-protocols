#!/usr/bin/env python3
"""Validate public reference links, coverage, synthetic examples and privacy."""
import json
import math
from pathlib import Path
import re
from render_examples import render
from ivolt_ascii import decode as decode_ivolt
from test_ivolt import run_tests as test_ivolt

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def be16(packet, offset):
    return int.from_bytes(packet[offset:offset + 2], 'big')


def le(packet, offset, size=2):
    return int.from_bytes(packet[offset:offset + size], 'little')


def bp_crc(packet):
    crc = 0
    for index, byte in enumerate(packet):
        crc ^= (0 if index in (8, 9) else byte) << 8
        for _ in range(8):
            crc = ((crc << 1) ^ (0x1021 if crc & 0x8000 else 0)) & 0xffff
    return crc


def decode_example(example, packet):
    """Check documented example fields offline; no BLE or setting operations."""
    if example['protocol'] == 'ivolt_ascii':
        return decode_ivolt(packet)
    if example['protocol'] == 'viofo_bp100':
        require(packet[:4] == bytes.fromhex('aa55aa55') and len(packet) == le(packet, 4) + 12, 'BP100 framing')
        command, payload = packet[6], packet[12:]
        require(len(payload) == {0x41: 5, 1: 2, 2: 4, 3: 8, 4: 8}.get(command), 'BP100 shape')
        require(packet[8:10] == bytes(2), 'Synthetic unverified BP100 CRC placeholder')
        if command == 0x41:
            require(payload[4] == 16 and le(payload, 0, 4) > 0, 'BP100 application identity')
            return {'firmware': str(le(payload, 0, 4)), 'model': 'BP100'}
        if command == 1:
            return {'charge_percent': payload[0] & 127, 'state_code': int(bool(payload[0] & 128))}
        if command == 2:
            temperature = payload[0] / 10 + (payload[1] & 127)
            return {'temperature_c': -temperature if payload[1] & 128 else temperature}
        prefix = 'input_' if command == 3 else 'output_'
        volts = payload[0] / 10 + payload[1]
        amps = payload[2] / (10 if command == 3 else 100) + payload[3]
        return {prefix + 'v': volts, prefix + 'a': amps, prefix + 'w': volts * amps,
                'time_to_full_min' if command == 3 else 'runtime_estimate_min': le(payload, 6)}
    if example['protocol'] == 'neo_plus':
        require(packet[:2] == b'@@' and len(packet) == packet[4] + 7 and packet[-2:] == b'\n\r', 'Neo+ framing')
        if example['kind'] == 'identity':
            require(packet[2] == 0x30, 'Neo+ identity command')
            return {'model': packet[5:-2].decode('ascii')}
        require(packet[2] == 0x41 and len(packet) == 75 and packet[59:61] == bytes(2), 'Neo+ standard status/PIN placeholders')
        iv, ov, ia, oa = (le(packet, offset) / 1000 for offset in (7, 9, 11, 13))
        return {'firmware': 'F' + str(packet[5]), 'charge_percent': packet[6],
                'input_v': iv, 'output_v': ov, 'input_a': ia, 'output_a': oa,
                'input_w': iv * ia, 'output_w': ov * oa, 'battery_v': le(packet, 17) / 1000,
                'temperature_c': int.from_bytes(packet[23:25], 'little', signed=True),
                'time_to_full_min': le(packet, 19), 'runtime_estimate_min': le(packet, 21),
                'reported_capacity_mah': le(packet, 25, 4) + le(packet, 29, 4), 'state_code': packet[44]}
    if example['protocol'] == 'blackvue_legacy':
        require(packet[:2] == b'\x43\x06', 'Legacy example header')
        require(len(packet) == packet[2] + 5, 'Legacy example length')
        if example['kind'] == 'identity':
            require(packet[3] == 0x52 and packet[2] >= 12, 'Identity layout')
            revision = be16(packet, 4)
            return {'firmware': f'{revision // 100}.{revision % 100:02d}',
                    'model': packet[10:16].decode('ascii').rstrip('\x00 ')}
        revision = example['firmware_revision']
        require(packet[3] == 0x51, 'Status command')
        require(packet[2] >= (23 if revision >= 160 else 18), 'Status payload')
        raw = packet[9]
        temperature = raw - 100 if raw >= 100 else 15 - raw if revision >= 110 else -raw
        input_v = be16(packet, 23) / 10 if revision >= 160 else packet[11] / 10
        output_v = be16(packet, 25) / 10 if revision >= 160 else packet[12] / 10
        input_a, output_a = be16(packet, 14) / 1000, be16(packet, 16) / 1000
        return {'charge_percent': packet[4] - (100 if revision >= 110 else 0),
                'temperature_c': temperature, 'input_v': input_v, 'output_v': output_v,
                'input_a': input_a, 'output_a': output_a,
                'input_w': input_v * input_a, 'output_w': output_v * output_a,
                'time_to_full_min': be16(packet, 7), 'runtime_estimate_min': be16(packet, 5),
                'reported_capacity_mah': be16(packet, 18), 'state_code': packet[20] & 15}
    require(example['protocol'] == 'itsc' and packet[:4] == b'ITSC', 'ITSC example header')
    word = packet[6]
    require(word in (0x32, 0x33, 0x34, 0x35) and len(packet) == (17 if word == 0x32 else 16), 'ITSC layout')
    require(packet[4:6] == b'\x00\x00', 'Synthetic device-ID placeholders')
    if word == 0x32:
        return {'firmware': f'{packet[7] // 10}.{packet[7] % 10}',
                'model': packet[11:16].decode('ascii').strip()}
    if word == 0x33:
        return {'charge_percent': packet[7], 'temperature_c': packet[8], 'state_code': packet[9]}
    if word == 0x34:
        iv, ia, ov, oa = (be16(packet, offset) / 1000 for offset in (7, 9, 11, 13))
        return {'input_v': iv, 'input_a': ia, 'output_v': ov, 'output_a': oa,
                'input_w': iv * ia, 'output_w': ov * oa}
    return {'time_to_full_min': be16(packet, 7), 'runtime_estimate_min': be16(packet, 9),
            'reported_capacity_mah': be16(packet, 11)}


IVOLT_HARDWARE_EVIDENCE = ['gatt_transport',
 'checksum_valid_CONT_controls',
 'DATA_only_startup_without_GET1',
 'DAT1_DAT2_DAT3_strict_production_parser_acceptance',
 'charging_state_1',
 'loaded_discharge_state_3',
 'positive_temperature',
 'ordinary_input_output_current',
 'charging_zero_output_current_unavailable']
IVOLT_SUPPORT_QUALIFICATION = {'evidence_basis': 'strict_production_parser_records_without_retained_raw_replies',
 'returned_model_identity': 'unknown',
 'independent_raw_replay': False,
 'measurement_calibration': False,
 'group_cadence': 'approximately_5_seconds_observed_not_hard_limit',
 'transition_freshness': 'old_numeric_values_may_persist_one_cycle_including_input_current_and_runtime',
 'source_only_branches': ['full_state_2',
                          'negative_temperature',
                          'FFFF_output_sentinel',
                          'special_9900',
                          'alternative_decimal_zero'],
 'other_revisions': 'unverified',
 'complete_protection_semantics': 'unknown',
 'GET1_and_settings_writes': 'not_authorized_by_telemetry_support'}
IVOLT_CORROBORATED_FIXTURES = ['ivolt_charging_dat1',
 'ivolt_charging_dat2',
 'ivolt_charging_dat3',
 'ivolt_discharge_dat1',
 'ivolt_discharge_dat2',
 'ivolt_discharge_dat3']


def validate_ivolt_profile(profile):
    """Require scoped hardware evidence without inventing firmware or raw replay."""
    require(profile['capacity_semantics'] == 'not_reported_by_measurement_queries', 'iVolt has no measurement capacity field')
    require(profile['incoming_checksum'] == 'native_DAT_not_gated_strict_client_recommended', 'Native DAT acceptance discrepancy')
    require(profile['coverage'] == 'hardware_telemetry' and profile['protocol'] == 'ivolt_ascii',
            'iVolt hardware telemetry protocol scope')
    require(profile['tested_firmware'] == [] and profile['physical_telemetry_accepted'] is True
            and profile['firmware_identity'] == 'unknown',
            'iVolt accepted telemetry must retain unknown firmware')
    require(profile['hardware_evidence'] == IVOLT_HARDWARE_EVIDENCE,
            'iVolt hardware support requires precise observed behaviors')
    require(profile.get('support_qualification') == IVOLT_SUPPORT_QUALIFICATION,
            'iVolt hardware support requires explicit identity, replay, branch and calibration limits')
    require(profile.get('checksum_evidence') == 'strict_production_parser_acceptance_not_independent_raw_replay',
            'iVolt checksum acceptance is not independent raw replay')
    require(profile['source_app']['version'] == '1.1.7' and profile['source_app']['package'] == 'com.thinkware.ivolt',
            'Pinned source app')
    require(profile['request_commands'] == ['DATA', 'GET1'] and profile['private_reply_commands'] == ['GET1']
            and profile['unknown_raw_replies'] == 'withhold_before_persistence', 'iVolt read-only/privacy scope')


def main():
    models = {'b124', 'b130a', 'b130x', 'bi750', 'powercell8', 'bp100', 'cellink-neo6'}
    qualified_models = {'ivolt-xtra'}
    profiles = [json.loads(path.read_text()) for path in sorted((ROOT / 'profiles').glob('*.json'))]
    require({profile['id'] for profile in profiles} == models | qualified_models, 'Eight distinct model profiles required')
    require({profile['id'] for profile in profiles if profile['coverage'] == 'hardware_telemetry'} == models | qualified_models,
            'Eight scoped hardware telemetry profiles required')
    for profile in profiles:
        require(profile['incoming_checksum'] == ('native_DAT_not_gated_strict_client_recommended' if profile['id'] in qualified_models else 'unverified'), 'Checksum evidence must remain explicit')
        require(profile['capacity_semantics'] in ('configured_mah', 'configured_base_plus_expansion_mah',
                                                  'not_reported_by_measurement_queries', 'unknown_not_decoded'), 'Capacity field semantics')
        if profile['id'] in qualified_models:
            require(profile['capacity_semantics'] == 'not_reported_by_measurement_queries', 'iVolt has no measurement capacity field')
        require((ROOT / profile['reference']).is_file(), 'Model reference missing')
        require((ROOT / profile['evidence_page']).is_file(), 'Evidence reference missing')
        for uuid in profile['service_uuids']:
            require(re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', uuid), 'UUID syntax')
        if profile['id'] == 'ivolt-xtra':
            validate_ivolt_profile(profile)
        else:
            require(profile['tested_firmware'] and profile['protocol'], 'Implemented telemetry needs scoped firmware/protocol')
    vectors = json.loads((ROOT / 'examples/vectors.json').read_text())
    require(vectors['synthetic'] is True and vectors['response_checksum'] == 'per_protocol_see_notes',
            'Examples must be synthetic and disclose unknown trailers')
    ids = []
    for request in vectors['requests']:
        ids.append(request['id'])
        packet = bytes.fromhex(request['hex'])
        if request['protocol'] == 'ivolt_ascii':
            require(request['command'] in ('DATA', 'GET1') and packet == ('S00,' + request['command'] + ',  E\r\n').encode('ascii'), 'Exact iVolt read-only literals')
            continue
        command = int(request['command'], 16)
        if request['protocol'] == 'blackvue_legacy':
            require(len(packet) == 5 and packet[:3] == b'\x43\x06\x00'
                    and command in (0x51, 0x52) and packet[3] == command, 'Telemetry-only legacy request')
            checksum = 0
            for byte in packet[:-1]:
                checksum ^= byte
            require(checksum == packet[-1], 'Request XOR')
        elif request['protocol'] == 'viofo_bp100':
            require(command in (0x41, 1, 2, 3, 4) and len(packet) == 12
                    and packet[:4] == bytes.fromhex('aa55aa55') and le(packet, 4) == 0
                    and packet[6] == command and le(packet, 8) == bp_crc(packet), 'BP100 request and outgoing CRC')
        elif request['protocol'] == 'neo_plus':
            require(command in (0x30, 0x41) and packet == b'@@' + bytes((command, 0, 10, 13)), 'Exact six-byte Neo+ request')
        else:
            require(request['protocol'] == 'itsc' and command in (0x32, 0x33, 0x34, 0x35)
                    and packet == b'ITSC\x00\x00' + bytes((command, 0)), 'Telemetry-only ITSC request')
    for example in vectors['responses']:
        ids.append(example['id'])
        packet = bytes.fromhex(example['hex'])
        if example['protocol'] in ('blackvue_legacy', 'itsc'):
            require(packet[-1] == 0, 'Synthetic response trailer placeholder')
        if example['protocol'] == 'ivolt_ascii':
            require(example['response_checksum'] == 'computed_additive_lowercase_ascii', 'iVolt computed response checksum')
            expected_evidence = ('observed_control_shape_independently_generated' if example['kind'] == 'control'
                                 else 'synthetic_illustration_of_hardware_corroborated_interpretation'
                                 if example['id'] in IVOLT_CORROBORATED_FIXTURES
                                 else 'synthetic_source_derived_branch_not_hardware_observed')
            require(example['evidence'] == expected_evidence, 'iVolt synthetic example evidence qualification')
            require(packet[4:8] in (b'CONT', b'DAT1', b'DAT2', b'DAT3'), 'No GET/settings/raw unknown fixtures')
        values = decode_example(example, packet)
        for field, expected in example['expected'].items():
            require(field in values, f'{example["id"]}: missing field {field}')
            actual = values[field]
            agrees = math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9) \
                if isinstance(expected, (int, float)) else actual == expected
            require(agrees, f'{example["id"]}: expectation mismatch for {field}')
    require(len(ids) == len(set(ids)), 'Unique example IDs required')
    exchanges = json.loads((ROOT / 'examples/exchanges.json').read_text())
    require(exchanges['synthetic'] is True, 'Exchange examples must be synthetic')
    require(len(exchanges['sessions']) == len(models | qualified_models) and {session['profile'] for session in exchanges['sessions']} == models | qualified_models,
            'One exchange session per supported profile')
    requests = {row['id']: row for row in vectors['requests']}
    responses = {row['id']: row for row in vectors['responses']}
    profile_map = {profile['id']: profile for profile in profiles}
    for session in exchanges['sessions']:
        require(session['service'] in profile_map[session['profile']]['service_uuids'], 'Exchange service matches profile')
        for role in ('writer', 'response'):
            require(re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', session[role]), 'Exchange characteristic UUID')
        if session['profile'] == 'ivolt-xtra':
            require(session['writer'] == profile_map['ivolt-xtra']['writer_uuid'] and session['response'] == profile_map['ivolt-xtra']['response_uuid'], 'iVolt FFF1/FFF2 roles')
            require(session['write_mode'] == 'write without response', 'iVolt write mode')
            require(session['control'] == [['ivolt_cont', 'ivolt_data']] and session['private_read_request'] == 'ivolt_get1', 'Control precedes DATA; GET reply omitted')
            require(all(limit in session['notes'] for limit in (
                'hardware-corroborated', 'strict production-parser acceptance', 'not independent raw replay',
                'firmware/model identity unknown', 'remain synthetic', 'source-derived only',
                'not a hard limit', 'may persist one cycle', 'not needed or authorized')),
                'iVolt evidence boundaries in guide')
            require(set(session['stream']) == {'charging', 'discharging', 'edge_cases'}, 'iVolt illustration groups')
            for phase, response_ids in session['stream'].items():
                for response_id in response_ids:
                    require(response_id in responses and responses[response_id]['protocol'] == 'ivolt_ascii' and responses[response_id]['kind'] == 'status', 'Synthetic iVolt stream references')
                if phase in ('charging', 'discharging'):
                    require([bytes.fromhex(responses[row]['hex'])[4:8] for row in response_ids] == [b'DAT1', b'DAT2', b'DAT3'], 'Three separate DAT groups')
            continue
        for phase in ('identity', 'charging', 'discharging', 'no_load'):
            if phase not in session:
                continue
            require(session[phase], 'Nonempty exchange phase')
            for request_id, response_id in session[phase]:
                require(request_id in requests and response_id in responses, 'Exchange references existing packets')
                request, response = requests[request_id], responses[response_id]
                require(request['protocol'] == response['protocol'], 'Exchange protocol agreement')
                packet = bytes.fromhex(response['hex'])
                offset = {'blackvue_legacy': 3, 'itsc': 6, 'neo_plus': 2, 'viofo_bp100': 6}[response['protocol']]
                require(int(request['command'], 16) == packet[offset], 'Reply command matches request')
                require((response['kind'] == 'identity') == (phase == 'identity'), 'Identification precedes measurement examples')
                if response_id == 'pc8_charging':
                    require(response.get('state_evidence') == 'source_derived_not_hardware_observed_on_f141'
                            and 'NOT hardware-verified' in session['notes'], 'PC8 charging evidence remains qualified')
    require((ROOT / 'examples/communication.md').read_text() == render(vectors, exchanges, profile_map),
            'Readable communication examples must match canonical JSON; run scripts/render_examples.py')
    files = [path for path in ROOT.rglob('*') if path.is_file()
             and '.git' not in path.relative_to(ROOT).parts
             and '__pycache__' not in path.relative_to(ROOT).parts]
    forbidden = [r'/Users/', r'/Volumes/', r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
                 r'\b(?:ghp_|github_pat_|sk_live_)[A-Za-z0-9_]{12,}',
                 r'\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b',
                 r'\b(?:B124|130A|130X)[0-9A-F]{4,}\b', r'PWC8\s+[0-9A-F]{6}\b',
                 r'phone-capture-\d', r'vortex-battery-lab[^\s]*workers\.dev',
                 r'CN6-[0-9A-F]{4}\b', r'IVT-[0-9A-F]{4}\b', r'\b20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d']
    for path in files:
        relative = path.relative_to(ROOT)
        require(path.suffix in ('.md', '.json', '.py', '.yml')
                or path.name in ('LICENSE', 'LICENSE-CODE', '.gitignore'), f'Unexpected public file: {relative}')
        require(path.stat().st_size < 1_000_000, f'Oversized file: {relative}')
        text = path.read_text()
        require(chr(0x2014) not in text, f'Em dash: {relative}')
        # The scanner source contains its own deny-list literals; scan its content
        # for secrets/addresses, but not the literal examples of banned path prefixes.
        for pattern in forbidden:
            if path == Path(__file__) and pattern in (r'/Users/', r'/Volumes/'):
                continue
            require(not re.search(pattern, text), f'Privacy pattern in {relative}')
        if path.suffix == '.json':
            json.loads(text)
        if path.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if target.startswith(('https://', 'http://', '#')):
                    continue
                local = target.split('#', 1)[0]
                destination = (path.parent / local).resolve()
                require(destination.is_relative_to(ROOT), f'Link outside repository: {relative}')
                require(destination.exists(), f'Broken local link in {relative}: {target}')
    test_ivolt()
    print(f'PASS: {len(profiles)} coverage profiles, {len(vectors["requests"])} requests, '
          f'{len(vectors["responses"])} synthetic replies, {len(files)} public files; links/privacy checked')


if __name__ == '__main__':
    main()
