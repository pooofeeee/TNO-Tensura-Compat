"""R2f5 integrity, complete selected-class coverage and prior subsection protection."""
from collections import Counter
from catalog_common import *
from classfile import ClassFile
from assemble_twilight_pair import START, DECISION, BATCH
from validate_twilight_naga import validate_naga


def validate_pair():
    previous = validate_naga()
    prefix = 'docs/benchmarks/external-effects-catalog/'
    tracked = git('ls-tree', '-r', '--name-only', START, '--', prefix).splitlines()
    protected = [p for p in tracked if any(x in p for x in (
        'frosted', 'lich', 'naga', 'twilightforest-r2f2-partial',
        'twilightforest-r2f3-partial', 'twilightforest-r2f4-partial'))]
    for p in protected:
        old = subprocess.check_output(['git', 'show', START + ':' + p], cwd=ROOT)
        assert (ROOT/p).read_bytes().replace(b'\r\n', b'\n') == old.replace(b'\r\n', b'\n'), p
    section = read_json(OUT/'semantic-sections/twilightforest-minoshroom-knight.json')
    assert section['subsection_decision'] == DECISION
    assert set(section['boss_states'].values()) == {'SEMANTIC_REVIEW_COMPLETE'}
    assert len(section['closure_checklist']) == 9 and all(section['closure_checklist'].values())
    assert len(section['effects']) == 10 and len(section['paths']) == 28
    assert section['counts']['per_boss'] == {
        'minoshroom': {'packages':4, 'paths':11}, 'knight_phantom': {'packages':6, 'paths':17}}
    counts = dict(Counter(e['primary_classification'] for e in section['effects']))
    assert counts == {'VANILLA_LIKE_EXTENDED':3, 'CUSTOM_DAMAGE':2, 'CUSTOM_CONTROL':4, 'BINARY_MECHANIC':1}
    assert section['counts']['classification_totals'] == counts
    assert section['counts']['review_required'] == 0
    assert all(e['primary_test_source'] and e['alternate_sources'] for e in section['effects'])
    assert all(p['setup'] and p['future_controls'] for p in section['paths'])
    profiles = {p['type']:p for p in section['damage_profiles']}
    assert set(profiles) == {'twilightforest:'+x for x in ['axing','slam','haunt','thrown_axe','thrown_pickaxe']}
    assert all(p['status'] == 'USED' for p in profiles.values())
    assert 'minecraft:bypasses_shield' in profiles['twilightforest:slam']['tags']
    assert 'minecraft:bypasses_armor' not in profiles['twilightforest:haunt']['tags']
    assert section['damage_census']['reviewed_profiles_after'] == 9
    assert section['damage_census']['remaining_profiles'] == 31
    old = read_json(OUT/'partial-drafts/twilightforest-r2f4-partial.json')
    new = read_json(OUT/'partial-drafts/twilightforest-r2f5-partial.json')
    assert new['effects'] == old['effects'] + section['effects'] and len(new['effects']) == 29
    assert new['paths'] == old['paths'] + section['paths'] and len(new['paths']) == 83
    witnesses = {}
    for p in (OUT/'native-evidence').glob('*.json'):
        for w in read_json(p).get('witnesses',[]):
            if w.get('mod_key') == 'twilightforest' and w['entry'].endswith('.class'):
                witnesses.setdefault(w['entry'], []).extend(w['methods'])
    def methods(owner): return witnesses['twilightforest/'+owner+'.class']
    def ins(owner,name): return next(m['instructions'] for m in methods(owner) if m['name']==name)
    def pos(instructions,text): return next(i['offset'] for i in instructions if text in str(i['operand']))
    # Full declared-method coverage supports negative claims about absent hurt/load overrides.
    target = next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    assert sha256(target['path']) == target['sha256']
    complete_classes = ['entity/boss/Minoshroom','entity/boss/KnightPhantom','entity/projectile/ThrownWep',
                        'entity/ai/goal/GroundAttackGoal','entity/ai/goal/ChargeAttackGoal',
                        'entity/ai/goal/PhantomUpdateFormationAndMoveGoal','entity/ai/goal/PhantomThrowWeaponGoal',
                        'entity/ai/goal/PhantomWatchAndAttackGoal','entity/ai/goal/PhantomAttackStartGoal']
    with zipfile.ZipFile(target['path']) as jar:
        for c in complete_classes:
            actual = {(m['name'],m['descriptor']) for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
            saved = {(m['name'],m['descriptor']) for m in methods(c)}
            assert actual == saved, c
    assert not {'hurt','isInvulnerableTo','addAdditionalSaveData','readAdditionalSaveData'} & {m['name'] for m in methods('entity/boss/Minoshroom')}
    assert not {'hurt','addAdditionalSaveData','readAdditionalSaveData'} & {m['name'] for m in methods('entity/projectile/ThrownWep')}
    hit = ins('entity/projectile/ThrownWep','onHitEntity')
    factory = pos(hit,'TFDamageTypes.getDamageSource(')
    hurt = pos(hit,'Entity.hurt(')
    assert factory < hurt and next(i for i in hit if i['offset']>hurt)['opcode'] == '0x57'
    assert not any('getIndirectEntityDamageSource(' in str(i['operand']) for i in hit)
    slam = ins('entity/ai/goal/GroundAttackGoal','tick')
    assert pos(slam,'Entity.push(') < pos(slam,'Entity.hurt(')
    guard = ins('entity/boss/KnightPhantom','hurt')
    assert pos(guard,'.isDamageSourceBlocked(') < pos(guard,'BaseTFBoss.hurt(')
    assert any(i['opcode']=='0xac' and i['offset']<pos(guard,'BaseTFBoss.hurt(') for i in guard)
    load = ins('entity/boss/KnightPhantom','readAdditionalSaveData')
    assert any('switchToFormationByNumber(' in str(i['operand']) for i in load)
    assert not any('setChargingAtPlayer(' in str(i['operand']) for i in load)
    switch = ins('entity/boss/KnightPhantom','switchToFormation')
    assert pos(switch,'.updateMyNumber(') < pos(switch,'.setChargingAtPlayer(')
    # The melee helper really loads attacker (local0), not victim (local1), for both discrepancies.
    helper = ins('util/entities/EntityUtil','properlyApplyCustomDamageSource')
    last = next(n for n,i in enumerate(helper) if '.setLastHurtMob(' in str(i['operand']))
    assert [i['opcode'] for i in helper[last-2:last]] == ['0x2a','0x2a']
    enchant = next(n for n,i in enumerate(helper) if '.modifyDamage(' in str(i['operand']))
    assert helper[enchant-3]['opcode'] == '0x2a'
    ledger = read_json(OUT/'mod-reviews/twilightforest.json')
    assert ledger['status'] in {'PARTIAL','COMPLETE'}
    if ledger['status']=='PARTIAL':
        assert not ledger['effects'] and not ledger['paths']
    else:
        assert ledger['decision']=='TWILIGHT_FOREST_SEMANTIC_REVIEW_COMPLETE' and ledger['effects'] and ledger['paths']
    assert ledger['draft_mechanic_count']>=29 and ledger['draft_path_count']>=83
    return dict(schema='tno.external_effects.minoshroom_knight_integrity.v1',status='PASS',starting_sha=START,
                decision=DECISION,boss_states=section['boss_states'],counts=section['counts'],
                protected_prior_files=len(protected),full_declared_class_coverage=len(complete_classes),
                twilight_reviewed_drafts=29,twilight_delivery_drafts=83,
                accepted_counts_unchanged=previous['accepted_counts_unchanged'],
                damage_profiles_reviewed=9,damage_profiles_remaining=31,
                runtime_tests=0,promoted_twilight_records=0,hydra_urghast_started=False,**boundary_flags())


if __name__=='__main__':
    result=validate_pair()
    write_json(OUT/'twilightforest-minoshroom-knight-integrity.json',result)
    print(json.dumps(result,indent=2))
