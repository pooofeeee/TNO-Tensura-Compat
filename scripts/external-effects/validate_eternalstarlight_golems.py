from catalog_common import *
from native_evidence import collect
from classfile import ClassFile
from collect_eternalstarlight_golems import ES,targets,producer_census
from assemble_eternalstarlight_golems import CP,STEM,FACTS
from eternalstarlight_combat_common import preserve_section

def validate_golems():
    e=read_json(OUT/'native-evidence/eternalstarlight-golems.json');assert collect(read_json(OUT/'native-specifications/eternalstarlight-golems.json'))==e
    assert producer_census()==read_json(OUT/'eternalstarlight-golems-producer-census.json')
    w={x['entry']:x for x in e['witnesses']}
    def body(cl,method):return next(m['instructions'] for m in w[ES+cl+'.class']['methods'] if m['name']==method)
    def hit(b,s):return [i for i in b if str(s) in str(i.get('operand',''))]
    def pos(b,s):return hit(b,s)[0]['offset']
    def after(b,s):return b[b.index(hit(b,s)[0])+1]
    go='common/entity/living/boss/golem/'
    hurt=body(go+'StarlightGolem','hurt');assert pos(hurt,'BYPASSES_INVULNERABILITY')<pos(hurt,'.hasProtection(')<pos(hurt,'.chargeHurtAmountF')<pos(hurt,'ESBoss.hurt(')<pos(hurt,'.setPhase(')
    inv=body(go+'StarlightGolem','isInvulnerableTo');assert hit(inv,'DamageTypes.FALLING_BLOCK') and hit(inv,'.getEntity(')
    tick=body(go+'StarlightGolem','aiStep');assert pos(tick,'BehaviorManager.tick(')<pos(tick,'.getNearbyEnergyBlocks(')<pos(tick,'.hasProtectionZ')
    assert hit(tick,'.generic(') and pos(tick,'.hurt(')<pos(tick,'.invulnerableTimeI')
    charge=body(go+'StarlightGolemChargePhase','canContinue');assert hit(charge,'.getChargeHurtCount(') and hit(charge,'.getChargeHurtAmount(') and hit(charge,'1.5')
    for cl,amount in [('StarlightGolemChargeStartPhase',.04),('StarlightGolemChargePhase',.02),('StarlightGolemChargeEndPhase',.02)]:
        b=body(go+cl,'tick');assert pos(b,'.hasProtection(')<pos(b,'.heal(') and any(i['operand']==amount or (isinstance(i['operand'],float) and abs(i['operand']-amount)<1e-6) for i in b)
    block=body('common/block/EnergyBlock','onProjectileHit');assert pos(block,'.setBlockAndUpdate(')<pos(block,'.getOwner(') and not hit(block,'.hurt(')
    melee=body(go+'Permafrost','doHurtTarget');assert pos(melee,'.doHurtTarget(')<pos(melee,'.canFreeze(')<pos(melee,'.setTicksFrozen(')
    with zipfile.ZipFile(targets()['eternalstarlight']['path']) as z:
        c=ClassFile(z.read(ES+go+'Permafrost.class'));assert not {'hurt','isInvulnerableTo'}&{m['name'] for m in c.methods}
    tube=body('common/entity/projectile/FrozenTube','onHitEntity');assert pos(tube,'LivingEntity')<pos(tube,'.shouldHarm(')<pos(tube,'ESDamageTypes.FREEZE')<pos(tube,'typeSwitch')<pos(tube,'.hurt(') and after(tube,'.hurt(')['opcode']=='0x57'
    assert hit(tube,'Attributes.ATTACK_DAMAGE') and not hit(tube,'Attributes.ATTACK_SPEED') and not hit(tube,'.canFreeze(')
    splash=body('common/entity/projectile/FrozenTube','onHit');assert pos(splash,'.onHit(')<pos(splash,'.canFreeze(')<pos(splash,'ServerPlayer')<pos(splash,'.setAttackEnergy(') and hit(splash,'common/entity/attack/EnergizedFlame')
    ray=body('common/entity/attack/ray/RayAttack','tick');assert len(hit(ray,'ESEntityUtil.raytrace('))==2 and hit(ray,'blockHitResult(')
    payload=body('common/entity/attack/ray/RayAttack','lambda$doHurtTarget$0');assert pos(payload,'.shouldHarm(')<pos(payload,'ESDamageTypes.LASER')<pos(payload,'.hurt(')<pos(payload,'.setRemainingFireTicks(') and after(payload,'.hurt(')['opcode']=='0x99'
    beam=body('common/entity/attack/ray/GolemLaserBeam','getAttackDamage');assert hit(beam,'StarlightGolem') and hit(beam,'SpellCaster') and hit(beam,'.strength(') and hit(beam,.5)
    orb=body('common/item/magic/OrbOfProphecyItem','use');assert pos(orb,'Pose.STANDING')<pos(orb,'CURRENT_CREST')<pos(orb,'.canCast(')<pos(orb,'SPELL_SOURCE')<pos(orb,'.start(')
    assert ES+'common/entity/interfaces/SpellCaster' in w[ES+'common/mixin/PlayerMixin.class']['interfaces']
    spell=body('common/util/ESSpellUtil','tickSpells');assert pos(spell,'.stop(')<pos(spell,'.tick(')
    assert w['data/eternal_starlight/eternal_starlight/crest/blazing_beam.json']['data']['spell']=='eternal_starlight:laser_beam'
    tags={x['id']:set(x['tags']) for x in read_json(OUT/'eternalstarlight-damage-tags.json')['declarations']}
    assert not tags['eternal_starlight:laser']&{'minecraft:is_fire','minecraft:bypasses_armor','minecraft:bypasses_shield','minecraft:bypasses_enchantments'}
    a=read_json(OUT/'annotation-evidence/eternalstarlight-frozen-tube-javap.json');assert sha256(a['tool'])==a['tool_sha256'] and sha256(OUT/a['output_file'])==a['output_sha256']
    s=(OUT/a['output_file']).read_text(encoding='utf-8');assert all(k in s for k in ['typeSwitch','double 6.0d','double 0.4d','Attributes.ATTACK_DAMAGE','double 3.0d'])
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==6 and len(d['delivery_paths'])==13
    assert all(v in (OUT/(STEM+'-review.md')).read_text(encoding='utf-8') for v in FACTS.values())
    return dict(schema='tno.external_effects.es_golems_integrity.v1',checkpoint=CP,status='PASS',native_witnesses=len(e['witnesses']),reviewed_packages=6,reviewed_paths=13,semantic_order_source_admission_checks='PASS',accepted_counts_preserved=preserve_section(d),promoted_records=0,whole_eternalstarlight_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_golems();write_json(OUT/'eternalstarlight-r2h3b-integrity.json',d);print(json.dumps(d,indent=2))
