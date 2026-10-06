"""Validate a finite anonymous-arrow kernel index against native witnesses/census.

This validates the captured factory boundary, never its owning trigger or values.
"""
import collections
import json

from catalog_common import OUT, read_json, sha256
from collect_combat_census import decode_sites


def validate(registry, census, out=OUT):
    assert registry['finite_census_sha256'] == sha256(out / registry['finite_census_file'])
    methods = {(m['entry'], m['method'], m['descriptor']): m for m in census['methods']}
    evidence = {}
    bodies = collections.defaultdict(list)
    calls = collections.defaultdict(list)
    for m in census['methods']:
        for site in decode_sites(census, m, 'calls'):
            calls[site['operand']].append(dict(entry=m['entry'], method=m['method'],
                descriptor=m['descriptor'], offset=site['offset'], code_sha256=m['code_sha256']))

    def native(proof):
        filename = proof['evidence_file']
        if filename not in evidence:
            evidence[filename] = read_json(out / filename)
        witness = next(w for w in evidence[filename]['witnesses'] if w['id'] == proof['witness_id'])
        assert witness['entry'] == proof['entry']
        method = next(m for m in witness['methods'] if m['name'] == proof['method'] and
                      m['descriptor'] == proof['descriptor'])
        assert not method.get('instruction_offset_ranges')
        assert method['code_sha256'] == proof['code_sha256'] == methods[
            (proof['entry'], proof['method'], proof['descriptor'])]['code_sha256']
        return witness, method

    seen = set()
    for row in registry['rows']:
        factory = row['factory']
        assert factory['entry'] not in seen
        seen.add(factory['entry'])
        fw, fm = native(factory)
        instructions = fm['instructions']
        owned = next(i['operand'] + '.class' for i in instructions if i['opcode'] == '0xbb')
        assert owned == row['owned_arrow_entry']
        ctor_w, ctor_m = native(row['constructor'])
        assert ctor_w['entry'] == owned
        assert ctor_w['superclass'] + '.class' == row['intrinsic_arrow_root']
        stores = ctor_m['instructions']
        assert stores[1]['local_index'] == 4 and stores[2]['opcode'] == '0xb5'
        assert stores[2]['operand'].endswith('.val$piercingB')
        assert stores[4]['local_index'] == 5 and stores[5]['opcode'] == '0xb5'
        assert stores[5]['operand'].endswith('.val$knockbackI')
        registry_symbols = [i['operand'] for i in instructions
                            if i['opcode'] == '0xb2' and 'ModEntities.' in str(i['operand'])]
        assert row['native_registry_symbol'] in registry_symbols
        owner_offsets = [i['offset'] for i in instructions if '.setOwner(' in str(i['operand'])]
        assert owner_offsets == ([] if row['owner_set_offset'] is None else [row['owner_set_offset']])
        assert [i['offset'] for i in instructions if '.setBaseDamage(' in str(i['operand'])] == [row['base_damage_set_offset']]
        ownerful = row['owner_set_offset'] is not None
        assert fm['descriptor'] == ('(Lnet/minecraft/world/level/Level;' +
            ('Lnet/minecraft/world/entity/Entity;' if ownerful else '') +
            'FIB)Lnet/minecraft/world/entity/projectile/Projectile;')
        damage_at = next(n for n,i in enumerate(instructions) if i['offset'] == row['base_damage_set_offset'])
        assert instructions[damage_at-1]['opcode'] == '0x8d'  # supplied float, then F2D
        assert instructions[damage_at-2]['opcode'] == ('0x25' if ownerful else '0x24')
        if ownerful:
            owner_at = next(n for n,i in enumerate(instructions) if i['offset'] == row['owner_set_offset'])
            assert instructions[owner_at-1]['opcode'] == '0x2c'  # formal Entity local2
        ctor_at = next(n for n,i in enumerate(instructions) if i['opcode'] == '0xb7' and '.<init>(' in str(i['operand']))
        def int_local(i):
            return i['local_index'] if i['opcode'] == '0x15' else int(i['opcode'],16)-0x1a
        assert int_local(instructions[ctor_at-2]) == (5 if ownerful else 4)  # byte piercing
        assert int_local(instructions[ctor_at-1]) == (4 if ownerful else 3)  # int knockback
        assert [i['offset'] for i in instructions if '.igniteForSeconds(' in str(i['operand'])] == row['self_fire_offsets']
        assert not any(x in str(i['operand']) for i in instructions for x in ('.setPos(', '.shoot(', '.addFreshEntity('))
        symbol = factory['entry'][:-6] + '.getArrow' + factory['descriptor']
        assert row['direct_callers'] == calls[symbol] and row['direct_callers']
        for kind in ('knockback', 'piercing'):
            witness, method = native(row[kind])
            assert witness['entry'] == owned
            normalized = [dict(i, operand=i['operand'].replace(owned[:-6], '@SELF@')
                              if isinstance(i['operand'], str) else i['operand'])
                          for i in method['instructions']]
            bodies[kind].append(json.dumps(normalized, sort_keys=True))
        assert row['disposition'] == 'SHARED_KERNEL_VERIFIED_OWNING_TRIGGER_CONTEXT_NOT_AUTOMATICALLY_CLOSED'
    assert all(len(set(group)) == 1 for group in bodies.values())
    assert registry['summary']['factories'] == len(seen)
    assert registry['summary']['owned_anonymous_arrow_classes'] == len({r['owned_arrow_entry'] for r in registry['rows']})
    assert registry['summary']['owner_setting_factories'] == sum(r['owner_set_offset'] is not None for r in registry['rows'])
    assert registry['summary']['owner_free_factories'] == sum(r['owner_set_offset'] is None for r in registry['rows'])
    assert registry['summary']['self_fire_factories'] == sum(bool(r['self_fire_offsets']) for r in registry['rows'])
    assert registry['canonical_mechanics_added'] == 0 and not registry['whole_mod_complete']
    assert not registry['stage_policy_decided']
    return dict(status='PASS', factories=len(seen), native_methods=len(seen)*4,
                knockback_body_groups=len(set(bodies['knockback'])), piercing_body_groups=len(set(bodies['piercing'])))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('registry')
    args = parser.parse_args()
    registry = read_json(OUT / args.registry)
    print(validate(registry, read_json(OUT / registry['finite_census_file'])))
