"""Protect accepted sections and verify the Naga research checkpoint contract."""
from collections import Counter
from catalog_common import *
from assemble_twilight_naga import START
from validate_twilight_lich import validate_lich


def validate_naga():
    prior_integrity = validate_lich()
    prefix = 'docs/benchmarks/external-effects-catalog/'
    tracked = git('ls-tree', '-r', '--name-only', START, '--', prefix).splitlines()
    protected = [p for p in tracked if any(x in p for x in (
        'frosted', 'lich', 'twilightforest-r2f2-partial', 'twilightforest-r2f3-partial'))]
    for path in protected:
        original = subprocess.check_output(['git', 'show', START + ':' + path], cwd=ROOT)
        current = (ROOT / path).read_bytes()
        assert current.replace(b'\r\n', b'\n') == original.replace(b'\r\n', b'\n'), path
    section = read_json(OUT / 'semantic-sections/twilightforest-naga.json')
    assert section['subsection_decision'] == 'NAGA_SEMANTIC_REVIEW_COMPLETE'
    assert set(section['closure_checklist']) == {
        'attacks', 'defenses', 'body_segments', 'health_phases',
        'source_delivery', 'exclusions', 'damage_types', 'classification_audit'}
    assert all(section['closure_checklist'].values())
    assert len(section['effects']) == 8 and len(section['paths']) == 18
    classification = dict(Counter(e['primary_classification'] for e in section['effects']))
    assert classification == {'VANILLA_LIKE_EXTENDED': 3, 'CUSTOM_CONTROL': 3,
                              'BINARY_MECHANIC': 1, 'CUSTOM_RESOURCE': 1}
    assert section['counts']['classification_totals'] == classification
    assert section['counts']['review_required'] == section['counts']['custom_damage_types'] == 0
    assert {p['type'] for p in section['damage_profiles']} == {
        'minecraft:mob_attack', 'minecraft:generic'}
    assert all(p['future_controls'] and p['setup'] and p['implementation'] for p in section['paths'])
    old = read_json(OUT / 'partial-drafts/twilightforest-r2f3-partial.json')
    new = read_json(OUT / 'partial-drafts/twilightforest-r2f4-partial.json')
    assert new['effects'] == old['effects'] + section['effects']
    assert new['paths'] == old['paths'] + section['paths']
    assert len(new['effects']) == 19 and len(new['paths']) == 55
    witnesses = read_json(OUT / 'native-evidence/twilight-naga.json')['witnesses']
    def method(owner, name):
        w = next(w for w in witnesses if w['entry'] == 'twilightforest/' + owner + '.class')
        return next(m for m in w['methods'] if m['name'] == name)['instructions']
    segment = method('entity/boss/NagaSegment', 'hurt')
    assert [i['opcode'] for i in segment if 15 <= i['offset'] <= 20] == [
        '0x24', '0xd', '0x6a', '0x12', '0x6e']  # argument * 2F / 3F
    assert next(i for i in segment if i['offset'] == 16)['operand'] == 2.0
    assert next(i for i in segment if i['offset'] == 18)['operand'] == 3.0
    assert 'Naga.hurt(' in next(i for i in segment if i['offset'] == 21)['operand']
    invisible = method('entity/TFPart', 'isInvisible')
    assert [i['operand'] for i in invisible if i['opcode'] == '0xb6'] == [
        'twilightforest/entity/TFPart.getParent()Lnet/minecraft/world/entity/Entity;',
        'net/minecraft/world/entity/Entity.isInvisible()Z']
    part = next(w for w in witnesses if w['entry'].endswith('/NagaSegment.class'))
    assert not any(m['name'] == 'isInvisible' for m in part['methods'])
    admission = method('entity/boss/Naga', 'isInvulnerableTo')
    positions = [next(i['offset'] for i in admission if text in str(i['operand'])) for text in (
        '.getEntity(', '.getDirectEntity(', '.IS_EXPLOSION', 'BaseTFBoss.isInvulnerableTo(')]
    assert positions == sorted(positions)
    hurt = method('entity/boss/Naga', 'hurt')
    assert 'BaseTFBoss.hurt(' in hurt[3]['operand']
    assert any(i['opcode'] == '0x8b' for i in hurt)  # float argument -> integer daze counter
    assert not any('.setHealth(' in str(i['operand']) for i in hurt)
    ledger = read_json(OUT / 'mod-reviews/twilightforest.json')
    if ledger['status'] == 'PARTIAL':
        assert not ledger['effects'] and not ledger['paths']
        assert ledger['draft_mechanic_count'] >= 19 and ledger['draft_path_count'] >= 55
    return dict(schema='tno.external_effects.naga_integrity.v1', status='PASS',
                starting_sha=START, decision=section['subsection_decision'],
                closure_areas=8, reviewed_naga_packages=8, naga_delivery_cases=18,
                classification_totals=classification, review_required=0,
                vanilla_damage_types=['minecraft:mob_attack', 'minecraft:generic'],
                protected_frosted_lich_files=len(protected),
                twilight_reviewed_drafts=19, twilight_delivery_drafts=55,
                accepted_counts_unchanged=prior_integrity['accepted_counts_unchanged'],
                native_admission_offsets=positions, runtime_tests=0,
                promoted_twilight_records=0, **boundary_flags())


if __name__ == '__main__':
    result = validate_naga()
    write_json(OUT / 'twilightforest-naga-integrity.json', result)
    print(json.dumps(result, indent=2))
