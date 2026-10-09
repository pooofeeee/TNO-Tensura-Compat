"""Small Sugar Rush coding fixture whose inputs come only from the V1 CLI.

Models directional motion and one already-admitted LOCAL_ENTITY client copy.
No Minecraft execution, native artifact parsing, global modifiers, or list sync.
"""
import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import struct
import subprocess
import sys

CLI = Path(__file__).resolve().parents[1] / 'mod_intelligence.py'
MECHANIC = 'alexscaves:sugar_rush'
OBLIGATION = 'alexscaves:citadel:sugar_rush_tick_controller'
MOD_VERSION = '2.0.10'
MOD_HASH = '6fad35bf07fcb977aaa32d3fe05bf122150c6a30ed16b057385040207a3b788f'
DEPENDENCY_VERSION = '2.7.6'
DEPENDENCY_HASH = '9e12468c49e5a95b7adbf22b3b4d05bc55565989b89c40b985cd73bdfe63c3c2'


class WorkflowError(Exception):
    def __init__(self, message, code=2):
        super().__init__(message)
        self.code = code


def require(condition, message):
    if not condition:
        raise WorkflowError(message)


def float32(value):
    return struct.unpack('f', struct.pack('f', value))[0]


def call_cli(*args):
    process = subprocess.run([sys.executable, '-B', str(CLI), *args], capture_output=True, text=True)
    response = json.loads(process.stdout)
    if process.returncode:
        raise WorkflowError(response.get('error', 'CLI lookup failed'), process.returncode)
    require(response['schema'] == 'tno.mod_intelligence.v1' and response['status'] == 'OK'
            and response['scope'] == 'STATIC_PINNED_CATALOG', 'Unexpected CLI response contract')
    return response, len(process.stdout.encode('utf-8'))


def load_contract(*, mod_version=MOD_VERSION, mod_hash=MOD_HASH,
                  dependency_version=DEPENDENCY_VERSION, dependency_hash=DEPENDENCY_HASH,
                  mod_jar=None, dependency_jar=None):
    """Exercise the CLI process boundary, including exact pins for both artifacts."""
    mod_checks = ['--expect-version', mod_version, '--expect-sha256', mod_hash]
    if mod_jar:
        mod_checks += ['--jar', str(mod_jar)]
    get, get_bytes = call_cli('get', MECHANIC, '--mod', 'alexscaves', '--section', 'semantics',
                             '--section', 'numbers', '--section', 'evidence', *mod_checks)
    dependencies, dependency_bytes = call_cli('dependencies', 'alexscaves', *mod_checks)
    dependency_checks = ['--expect-version', dependency_version, '--expect-sha256', dependency_hash]
    if dependency_jar:
        dependency_checks += ['--jar', str(dependency_jar)]
    verify, verify_bytes = call_cli('verify', 'citadel', *dependency_checks)
    contract = SugarRush.from_responses(get, dependencies, verify)
    return contract, dict(get=get_bytes, dependencies=dependency_bytes, verify=verify_bytes)


@dataclass(frozen=True)
class SugarRush:
    coefficient: float
    upward: float
    downward: float
    slow_fall: dict
    speed_multiplier: float
    flying_factor: float
    duration_multiplier: float
    radius: float
    local_multiplier: float
    normal_ms: float
    regular_duration: int
    long_duration: int
    provenance: dict

    @classmethod
    def from_responses(cls, get, dependencies, verify):
        for response in [get, dependencies, verify]:
            require(response['schema'] == 'tno.mod_intelligence.v1' and response['status'] == 'OK',
                    'Cannot consume an unsuccessful or incompatible response')
            require(response['scope'] == 'STATIC_PINNED_CATALOG', 'Expected static catalog evidence')
        data, dependency = get['data'], dependencies['data']
        require(data['requested_id'] == MECHANIC and len(data['mechanics']) == 1, 'Wrong mechanic')
        require(data['mod_key'] == dependency['mod_key'] == 'alexscaves', 'Wrong target mod')
        for source in [data['source_check'], dependency['source_check']]:
            pin = source['catalog_pin']
            require(pin['sha256'] == MOD_HASH and any(m['version'] == MOD_VERSION for m in pin['declared_mods']),
                    'Stale AlexCaves source identity')
        artifact = dependency['artifact']
        require(dependency['obligation_status'] == 'COMPLETE' and artifact['mod_id'] == 'citadel'
                and artifact['sha256'] == DEPENDENCY_HASH
                and artifact['exact_installed_version'] == DEPENDENCY_VERSION, 'Stale or incomplete Citadel contract')
        pin = verify['data']['source_check']['catalog_pin']
        require(verify['data']['mod_key'] == 'citadel' and pin['sha256'] == DEPENDENCY_HASH
                and pin['recorded_version'] == DEPENDENCY_VERSION, 'Stale verified dependency identity')
        row = data['mechanics'][0]
        require(row['id'] == MECHANIC and row['evidence'], 'Missing mechanic evidence')
        obligations = [o for o in dependency['obligations'] if o['id'] == OBLIGATION]
        require(len(obligations) == 1 and obligations[0]['status'] == 'RESOLVED_PINNED'
                and MECHANIC in obligations[0]['affected_mechanic_ids'], 'Unresolved controller obligation')
        obligation = obligations[0]
        components = {c['primitive']: c for c in row['components']}
        numbers = {key: c['numerical_parameters'] for key, c in components.items()}
        time = components['TIME_CONTROL_REQUEST']
        numeric_contract = obligation['contract']['numerical_contract']
        require(time['external_dependency_contract'] == OBLIGATION
                and numbers['TIME_CONTROL_REQUEST']['duration_multiplier'] == numeric_contract['native_multiplier']
                and time['native_protocol_context']['third_constructor_double'] == numeric_contract['native_radius_blocks'],
                'Native request and dependency parameters disagree')
        inputs = {}
        for response in [get, dependencies, verify]:
            for item in response['inputs']:
                require(item['file'] not in inputs or inputs[item['file']] == item['sha256'],
                        'Catalog changed between CLI calls')
                inputs[item['file']] = item['sha256']
        sites = []
        for candidate in row['parameter_candidates']:
            consumer = candidate['native_consumer']
            matches = [e for e in row['evidence'] if e['file'] == consumer['evidence_file']
                       and e['entry'] == consumer['entry'] and e.get('site', {}).get('offset') == consumer['offset']
                       and any(m['name'] in consumer['methods'] and m.get('descriptor') == consumer['descriptor']
                               for m in e['methods'])]
            require(len(matches) == 1, 'Missing selected numeric site evidence')
            evidence = matches[0]
            sites.append(dict(primitive=candidate['primitive'], parameters=candidate['parameters'],
                              consumer=consumer, file_sha256=evidence['file_sha256'], methods=evidence['methods']))
        provenance = dict(mechanic=row['canonical_ref'], dependency_obligation=OBLIGATION,
            dependency_file=dependency['evidence_file'],
            source_checks=dict(mod=data['source_check'], dependency=verify['data']['source_check']),
            inputs=inputs,
            numeric_sites=sites,
            dependency_evidence=obligation['evidence'])
        slow_fall = dict(numbers['MOB_EFFECT_SLOW_FALLING'], flags=components['MOB_EFFECT_SLOW_FALLING']['native_flags'])
        return cls(numbers['ATTRIBUTE_MODIFIER']['movement_speed_coefficient'],
                   numbers['FORCED_MOVEMENT']['upward_y_factor'], numbers['FORCED_MOVEMENT']['downward_y_factor'],
                   slow_fall, numbers['PLAYER_SPEED_QUERY']['speed_multiplier'],
                   numbers['PLAYER_SPEED_QUERY']['flying_from_getSpeed_factor'],
                   numbers['TIME_CONTROL_REQUEST']['duration_multiplier'], numeric_contract['native_radius_blocks'],
                   numeric_contract['native_multiplier'], time['native_protocol_context']['server_active_comparison'],
                   numbers['MOB_EFFECT_SUGAR_RUSH']['potion_regular_duration'],
                   numbers['MOB_EFFECT_SUGAR_RUSH']['potion_long_duration'], provenance)

    def attribute_amount(self, amplifier):
        return self.coefficient * (amplifier + 1)

    def motion(self, velocity, *, on_server=True, remaining_duration=1, slow_falling_present=False):
        x, y, z = velocity
        active = on_server and remaining_duration > 0
        movement = (x, y * (self.downward if y < 0 else self.upward), z) if active else velocity
        request = self.slow_fall if active and y < 0 and not slow_falling_present else None
        return dict(velocity=movement, slow_falling_request=request)

    def controller_query(self, distance, *, duration=None, master_ticks=0, owner_has_sugar_rush=True,
                         recipient_has_sugar_rush=True,
                         entity_valid=True, local_modifier_present=True, config=True,
                         original_speed=0.1, original_flying_speed=0.02):
        """One client copy, no global modifiers; original_speed is the native RETURN value.

        Assume an already-admitted Player Added/ServerLevel/config event. Expiry
        age is client master ticks; no inactive server hook is simulated.
        """
        duration = self.regular_duration if duration is None else duration
        require(0 < duration <= self.long_duration and duration == int(duration),
                'Fixture duration must be a positive integer within the recorded potion range')
        max_duration = math.ceil(float32(float32(duration) * float32(self.duration_multiplier)))
        expires_at = max_duration / self.local_multiplier
        applies = (local_modifier_present and entity_valid and owner_has_sugar_rush
                   and master_ticks < expires_at and distance * distance < self.radius * self.radius)
        client_ms = max(1, self.normal_ms * self.local_multiplier * self.local_multiplier) if applies else self.normal_ms
        server_ms = self.normal_ms  # LOCAL_ENTITY does not alter the server GLOBAL-only query.
        client_gate = config and recipient_has_sugar_rush and client_ms != self.normal_ms
        speed = float32(float32(original_speed) * float32(self.speed_multiplier)) if client_gate else original_speed
        flying = float32(speed * float32(self.flying_factor)) if client_gate else original_flying_speed
        return dict(max_duration=max_duration, local_multiplier=self.local_multiplier, radius=self.radius,
                    client_expiry_master_tick=expires_at, local_query_applies=applies,
                    server_tick_ms=server_ms, client_tick_ms=client_ms,
                    server_speed_return=original_speed, client_speed_return=speed, client_flying_return=flying)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mod-jar', type=Path, help='Optional exact AlexCaves artifact for a byte identity check')
    parser.add_argument('--dependency-jar', type=Path, help='Optional exact Citadel artifact for a byte identity check')
    args = parser.parse_args(argv)
    try:
        contract, sizes = load_contract(mod_jar=args.mod_jar, dependency_jar=args.dependency_jar)
        result = dict(status='OK', fixture=MECHANIC,
            scope='STATIC_CODING_FIXTURE_ONE_LOCAL_MODIFIER',
            demonstration=dict(attribute_amount_amplifier_0=contract.attribute_amount(0),
                attribute_amount_amplifier_1=contract.attribute_amount(1),
                ascending=contract.motion((1, 2, 3)), descending=contract.motion((1, -2, 3)),
                inside_radius=contract.controller_query(9), at_radius=contract.controller_query(contract.radius),
                at_expiry=contract.controller_query(0, master_ticks=contract.regular_duration)),
            cli_output_bytes=sizes, provenance=contract.provenance)
        print(json.dumps(result, separators=(',', ':')))
        return 0
    except (WorkflowError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps(dict(status='ERROR', error=str(error)), separators=(',', ':')))
        return getattr(error, 'code', 2)


if __name__ == '__main__':
    sys.exit(main())
