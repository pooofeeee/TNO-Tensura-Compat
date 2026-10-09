"""Preview one fixed Corrodent animation using only Mod Intelligence CLI JSON.

Duration is a supplied scenario value, not a claim about a native animation.
Start replacement, Tick listeners, networking, and actor damage remain external.
"""
import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from examples.sugar_rush_workflow import (call_cli, require, WorkflowError,
    MOD_VERSION, MOD_HASH, DEPENDENCY_VERSION, DEPENDENCY_HASH)

MECHANIC = 'alexscaves:corrodent_bite_native_dig_light_fear'
OBLIGATION = 'alexscaves:citadel:actor_animation_clock'


def load_clock(*, mod_version=MOD_VERSION, mod_hash=MOD_HASH,
               dependency_version=DEPENDENCY_VERSION, dependency_hash=DEPENDENCY_HASH):
    checks = ['--expect-version', mod_version, '--expect-sha256', mod_hash]
    commands = [
        ['search', 'corrodent animation', '--mod', 'alexscaves', '--limit', '2', *checks],
        ['get', MECHANIC, '--mod', 'alexscaves', '--section', 'semantics', '--section', 'evidence', *checks],
        ['dependencies', 'alexscaves', '--mechanic', MECHANIC, '--obligation', OBLIGATION, *checks,
         '--expect-dependency-version', dependency_version, '--expect-dependency-sha256', dependency_hash],
    ]
    responses, measurements = [], []
    for command in commands:
        response, byte_count = call_cli(*command)
        responses.append(response)
        measurements.append(dict(arguments=command, response_bytes=byte_count))
    return AnimationClock.from_responses(*responses), measurements


@dataclass(frozen=True)
class Frame:
    tick: int
    active: bool = True


@dataclass(frozen=True)
class AnimationClock:
    increment: int
    provenance: dict

    @classmethod
    def from_responses(cls, search, get, dependencies):
        inputs = {}
        for response in (search, get, dependencies):
            require(response['schema'] == 'tno.mod_intelligence.v1' and response['status'] == 'OK'
                    and response['scope'] == 'STATIC_PINNED_CATALOG', 'Unexpected CLI response')
            for item in response['inputs']:
                require(item['file'] not in inputs or inputs[item['file']] == item['sha256'],
                        'Catalog changed between CLI calls')
                inputs[item['file']] = item['sha256']
            pin = response['data']['source_check']['catalog_pin']
            require(pin['sha256'] == MOD_HASH and any(m['version'] == MOD_VERSION for m in pin['declared_mods']),
                    'Stale mod source identity')
        require(any(r['id'] == MECHANIC for r in search['data']['results']), 'Mechanic not found by search')
        require(get['data']['requested_id'] == MECHANIC and len(get['data']['mechanics']) == 1,
                'Wrong mechanic response')
        row = get['data']['mechanics'][0]
        native = [e for e in row['evidence'] if e['entry'].endswith('/CorrodentEntity.class')]
        require(row['id'] == MECHANIC and any(m['name'] == 'tick' and m.get('code_sha256')
                for e in native for m in e['methods']), 'Missing native caller witness')
        data = dependencies['data']
        require(data['requested_mechanic'] == MECHANIC and data['obligation_status'] == 'COMPLETE'
                and len(data['obligations']) == 1, 'Wrong or incomplete dependency selection')
        artifact = data['artifact']
        require(artifact['mod_id'] == 'citadel' and artifact['status'] == 'AVAILABLE_VERIFIED'
                and artifact['exact_installed_version'] == DEPENDENCY_VERSION
                and artifact['sha256'] == DEPENDENCY_HASH, 'Stale dependency artifact')
        obligation = data['obligations'][0]
        require(obligation['id'] == OBLIGATION and obligation['status'] == 'RESOLVED_PINNED'
                and MECHANIC in obligation['affected_mechanic_ids']
                and obligation['validation_state'] in ('WITNESSES_RESOLVED', 'WITNESSES_RESOLVED_WITH_MISSING_HASHES'),
                'Unresolved animation obligation')
        handlers = [w for w in obligation['witnesses'] if w['class_name'] and w['class_name'].endswith('/AnimationHandler')]
        require(len(handlers) == 1, 'Missing animation handler identity')
        handler = handlers[0]
        methods = {m['name']: m for m in handler['methods']}
        require(all(name in methods and methods[name].get('code_sha256')
                    for name in ('sendAnimationMessage', 'updateAnimations')), 'Missing required method hash')
        numbers = obligation['contract']['numerical_contract']
        require(type(numbers['clock_increment']) is int and numbers['clock_increment'] > 0,
                'Invalid clock increment')
        require(numbers['end_condition'] == 'animationTick == currentAnimation.getDuration(), after optional Tick event',
                'Animation end rule changed; review the adapter')
        return cls(numbers['clock_increment'], dict(mechanic=MECHANIC, obligation=OBLIGATION,
            artifact=artifact, native_caller=native, handler=handler,
            dependency_contract=obligation['contract'], inputs=inputs))

    def advance(self, state, duration, *, start_cancelled=False, server=True):
        """One update of an unchanged animation with no listener mutations."""
        require(type(duration) is int and type(state.tick) is int and state.tick >= 0,
                'Expected integer duration and nonnegative animation tick')
        if not state.active:
            return state, []
        actions, tick = [], state.tick
        if tick == 0:
            actions.append(dict(action='POST_START', cancelled=start_cancelled))
            if server and not start_cancelled:
                actions.append(dict(action='SEND_ANIMATION'))
        if tick < duration:
            tick += self.increment
            actions.append(dict(action='POST_TICK', tick=tick))
        if tick == duration:
            actions.append(dict(action='RESET_TO_NO_ANIMATION'))
            return Frame(0, False), actions
        return Frame(tick), actions


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--duration', type=int, required=True, help='Supplied scenario duration, not inferred native data')
    cli.add_argument('--initial-tick', type=int, default=0)
    cli.add_argument('--updates', type=int, default=4)
    cli.add_argument('--start-cancelled', action='store_true')
    cli.add_argument('--client', action='store_true')
    args = cli.parse_args(argv)
    try:
        require(0 <= args.updates <= 20, 'updates must be between 0 and 20')
        clock, measurements = load_clock()
        state, trace = Frame(args.initial_tick), []
        for _ in range(args.updates):
            before = state
            state, actions = clock.advance(state, args.duration, start_cancelled=args.start_cancelled, server=not args.client)
            trace.append(dict(before=before.__dict__, after=state.__dict__, actions=actions))
        print(json.dumps(dict(scope='STATIC_FIXED_ANIMATION_SCENARIO', duration_input=args.duration,
            trace=trace, cli_measurements=measurements, provenance=clock.provenance), separators=(',', ':')))
        return 0
    except WorkflowError as error:
        print(json.dumps(dict(status='ERROR', error=str(error))))
        return error.code


if __name__ == '__main__':
    sys.exit(main())
