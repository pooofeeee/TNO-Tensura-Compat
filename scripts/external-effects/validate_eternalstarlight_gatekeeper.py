from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_gatekeeper import ES,census
from assemble_eternalstarlight_gatekeeper import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_gatekeeper():
    e=read_json(OUT/'native-evidence/eternalstarlight-gatekeeper.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-gatekeeper.json'))==e
    r=read_json(OUT/'reference-evidence/eternalstarlight-gatekeeper-244.json');assert reference_collect(read_json(OUT/'reference-specifications/eternalstarlight-gatekeeper-244.json'))==r
    v=read_json(OUT/'vanilla-evidence/eternalstarlight-gatekeeper.json');assert prepare(read_json(OUT/'vanilla-specifications/eternalstarlight-gatekeeper.json'))==v
    route=read_json(OUT/'reference-routing/eternalstarlight-gatekeeper.json');assert sha256(route['archive'])==route['sha256']
    with zipfile.ZipFile(route['archive']) as z:assert not(set(route['absent_entries'])&set(z.namelist()))
    assert census()==read_json(OUT/'eternalstarlight-gatekeeper-census.json')
    w={x['entry']:x for x in e['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[ES+cl+'.class']['methods'] if m['name']==method and m.get('instructions'))
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    g='common/entity/living/boss/gatekeeper/'
    b=body(g+'TheGatekeeper','hurt')
    assert pos(b,'BYPASSES_INVULNERABILITY')<pos(b,'canAlwaysHurtWhenFighting')<pos(b,'healInterruptedZ')<pos(b,'.isDirect(')<pos(b,'.hurt(')
    assert not any(m['name']=='doHurtTarget' for m in w[ES+g+'TheGatekeeper.class']['methods'])
    b=body(g+'GatekeeperEatPhase','stop');assert pos(b,'healInterruptedIndirect')<pos(b,'.heal(')<pos(b,'.setBehaviorState(') and hit(b,20.0) and hit(b,10.0)
    b=body(g+'GatekeeperTeleportPhase','tick');assert pos(b,'.randomTeleport(')<pos(b,'.equals(')<pos(b,'.setPos(') and not hit(b,'postTeleportEvent')
    b=body(g+'TheGatekeeper','tryTeleportBack');assert pos(b,'.setPos(')<pos(b,'postTeleportEvent')
    b=body('common/entity/projectile/GatekeeperFireball','onHitEntity');assert pos(b,'.fireball(')<pos(b,'.hurt(') and after(b,'.hurt(')['opcode']=='0x57' and hit(b,8.0)
    b=body('common/entity/projectile/GatekeeperFireball','onHit');assert pos(b,'.onHit(')<pos(b,'.explode(')<pos(b,'.discard(') and hit(b,'ExplosionInteraction.NONE')
    b=body('common/handler/ESCommonHandler','onAllowLivingDeath');assert pos(b,'.isStandardFight(')<pos(b,'.abortFight(')<pos(b,'.setHealth(')<pos(b,'.invulnerableTimeI')
    for n in ['GatekeeperBowPhase','GatekeeperBowComboPhase']:
        b=body(g+n,'tick');assert pos(b,'.getMobArrow(')<pos(b,'.setBaseDamage(') and hit(b,0.75) and not hit(b,'.createProjectile(')
    for cl in ['common/entity/living/boss/creeper/SolarCreeper','common/entity/living/boss/creeper/SolarCreeperIntroPhase','common/entity/living/goal/MoveToTargetGoal']:
        for m in w[ES+cl+'.class']['methods']:
            assert not any(hit(m['instructions'],s) for s in ['.doHurtTarget(','.explode(','.hurt(']),(cl,m['name'])
    b=body('common/entity/living/boss/creeper/SolarCreeper','causeFallDamage');assert b[0]['opcode']=='0x3' and b[1]['opcode']=='0xac'
    mob=next(x for x in r['witnesses'] if x['entry'].endswith('/Mob.class'));b=next(m['instructions'] for m in mob['methods'] if m['name']=='doHurtTarget')
    assert pos(b,'.mobAttack(')<pos(b,'.modifyDamage(')<pos(b,'.hurt(')<pos(b,'.doPostAttackEffects(') and not hit(b,'getAttackDamageBonus') and not hit(b,'postHurtEnemy')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==9 and len(d['delivery_paths'])==15
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_gatekeeper_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),loader_witnesses=len(r['witnesses']),raw_fallback_classes=len(v['classes']),reviewed_packages=9,reviewed_paths=15,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_gatekeeper();write_json(OUT/'eternalstarlight-r2h3e-integrity.json',d);print(json.dumps(d,indent=2))
