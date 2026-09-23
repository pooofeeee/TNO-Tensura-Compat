from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_bossesrise_roll import census
from collect_bossesrise_foundation import PKG
from assemble_bossesrise_roll import FACTS,CP,STEM
from bossesrise_combat_common import preserve_section

def validate_roll():
    e=read_json(OUT/'native-evidence/bossesrise-roll.json');assert collect(read_json(OUT/'native-specifications/bossesrise-roll.json'))==e
    ref=read_json(OUT/'reference-evidence/bossesrise-roll-244.json');assert reference_collect(read_json(OUT/'reference-specifications/bossesrise-roll-244.json'))==ref
    c=read_json(OUT/'bossesrise-roll-census.json');assert census()==c
    w={x['entry']:x for x in e['witnesses']};rw={x['entry']:x for x in ref['witnesses']}
    def b(short,method):return next(m['instructions'] for m in w[PKG+short+'.class']['methods'] if m['name']==method)
    def rb(entry,method):return next(m['instructions'] for m in rw[entry+'.class']['methods'] if m['name']==method)
    def h(body,s):return [i for i in body if s in str(i.get('operand',''))]
    roll='attachment/entity/RollAttachment';network='network/DodgeRollMessage'
    v=b(roll,'isInvulnerable');assert v[2]['operand']==7 and v[3]['opcode']=='0xa4'
    v=b(roll,'isRolling');assert v[2]['opcode']=='0x9e'
    v=b(roll,'startRoll');assert any(i['operand']==-5 for i in v) and any(i['operand']==14 for i in v) and h(v,'.onGround(') and h(v,'.setForcedPose(')
    v=b(network,'pressAction');assert h(v,'.CAN_USE_ROLL') and h(v,'.isSwimming(') and h(v,'.getCooldown(')
    assert h(v,'.startRoll(')[0]['offset']<h(v,'.startCooldown(')[0]['offset']
    assert h(b(network,'handleData'),'SERVERBOUND') and h(b(network,'handleData'),'.enqueueWork(')
    v=b(roll,'tick');assert h(v,'.ROLL_COOLDOWN') and h(v,'.DEFAULT_ROLL_COUNT') and h(v,'.ROLL_COUNT') and h(v,'.removeLast(') and any(i['opcode']=='0x6e' for i in v)
    assert not any('ROLL_COOLDOWN_MORE' in str(r['hits']) for r in c['rows'])
    for method in ['preDamage','preEffect','preImpact']:
        v=b(roll,method);assert h(v,'.isInvulnerable(') and h(v,'net/minecraft/world/entity/player/Player')
        assert not h(v,'DamageTypeTags')
    assert h(b(roll,'preEffect'),'DO_NOT_APPLY')
    # This event carries the projectile itself; the mod tests that subject against Player.
    v=b(roll,'preImpact');assert h(v,'ProjectileImpactEvent.getEntity(') and not h(v,'getRayTraceResult')
    n='net/neoforged/neoforge/event/entity/ProjectileImpactEvent';v=rb(n,'<init>')
    assert [i['opcode'] for i in v[:3]]==['0x2a','0x2b','0xb7'] and 'EntityEvent.<init>' in v[2]['operand']
    assert h(rb('net/neoforged/neoforge/event/entity/EntityEvent','getEntity'),'.entityLnet/minecraft/world/entity/Entity;')
    hooks='net/neoforged/neoforge/common/CommonHooks'
    assert h(rb(hooks,'onEntityIncomingDamage'),'.post(') and h(rb(hooks,'onEntityIncomingDamage'),'.isCanceled(')
    v=rb('net/minecraft/world/entity/LivingEntity','hurt');assert h(v,'onEntityIncomingDamage(')[0]['offset']<h(v,'onDamageBlock(')[0]['offset']
    effect='net/neoforged/neoforge/event/entity/living/MobEffectEvent$Applicable';assert h(rb(effect,'getApplicationResult'),'.DEFAULT') and h(rb(effect,'getApplicationResult'),'.APPLY') and h(rb(effect,'getApplicationResult'),'.canBeAffected(')
    v=b('mixins/RollMixin','freshNeverFrozen');assert h(v,'.isInvulnerable(') and h(v,'.cancel(') and not h(v,'.setTicksFrozen(')
    assert h(b('mixins/ControlMixin','isImmobileMixin'),'.isRolling(')
    for method in w[PKG+roll+'.class']['methods']:
        assert not any(s in str(method['instructions']) for s in ['.hurt(','.heal(','.setHealth(','.removeEffect('])
    a=read_json(OUT/'annotation-evidence/bossesrise-roll-javap.json');assert sha256(a['tool'])==a['tool_sha256'] and sha256(OUT/a['output_file'])==a['output_sha256']
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==4 and len(d['delivery_paths'])==9 and not d['remaining_subsection_native_ambiguities']
    assert all(not m['stage_scaling_needed'] for m in d['mechanic_packages'])
    preserved=preserve_section(d);assert preserved==dict(effects=543,sources=1303,paths=1303,comparisons=543,primitives=717)
    return dict(schema='tno.external_effects.bossesrise_roll_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reference_witnesses=len(ref['witnesses']),mechanic_packages=4,native_paths=9,roll_threshold='14..8',native_projectile_subject_cannot_be_player=True,accepted_counts_preserved=preserved,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_roll();write_json(OUT/'bossesrise-r2i2a-integrity.json',d);print(json.dumps(d,indent=2))
