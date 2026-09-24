from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_cataclysm_remaining_status import usages,PKG
from assemble_cataclysm_remaining_status import CP,STEM,FACTS,status_coverage
from cataclysm_combat_common import preserve_section

def validate_remaining_status():
    e=read_json(OUT/'native-evidence/cataclysm-remaining-status.json');assert collect(read_json(OUT/'native-specifications/cataclysm-remaining-status.json'))==e and len(e['witnesses'])==25
    r=read_json(OUT/'reference-evidence/cataclysm-remaining-status-244.json');assert reference_collect(read_json(OUT/'reference-specifications/cataclysm-remaining-status-244.json'))==r and len(r['witnesses'])==3
    u=read_json(OUT/'cataclysm-remaining-status-usages.json');assert usages()==u and len(u['rows'])==26
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(path,name):return next(m['instructions'] for m in w[path+'.class']['methods'] if m['name']==name)
    def b(short,name):return body(PKG+short,name)
    def hits(ins,s):return [i for i in ins if s in str(i.get('operand',''))]
    def offset(ins,s):return hits(ins,s)[0]['offset']
    ins=b('effects/EffectMonstrous','applyEffectTick');assert offset(ins,'.getHealth(')<offset(ins,'.getMaxHealth(')<offset(ins,'.heal(') and any(i.get('operand')==1.0 for i in ins) and not hits(ins,'Mth.clamp(')
    ins=b('items/Monstrous_Helm','inventoryTick');assert offset(ins,'MONSTROUS_HELM')<offset(ins,'.isOnCooldown(')<offset(ins,'.mobAttack(')<offset(ins,'.hurt(')<offset(ins,'.push(')<offset(ins,'.addCooldown(')<offset(ins,'EFFECTMONSTROUS')
    assert any(i.get('operand')==350 for i in ins) and not hits(ins,'.isClientSide')
    for short in ['effects/EffectBlazing_Brand','effects/EffectBone_Fracture']:
        assert not any(hits(b(short,'applyEffectTick'),s) for s in ['.hurt(','.heal(','.setHealth('])
    ins=b('effects/EffectWetness','applyEffectTick');assert offset(ins,'.isSensitiveToWater(')<offset(ins,'.magic(')<offset(ins,'.hurt(')
    ins=b('event/ServerEventHandler','onLivingAttack');assert offset(ins,'IS_LIGHTNING')<offset(ins,'EFFECTWETNESS')<offset(ins,'Math.min(')<offset(ins,'.setAmount(')
    ins=b('client/event/ClientEvent','MovementInput');assert all(hits(ins,s) for s in ['EFFECTCURSE_OF_DESERT','keyDown','keyUp','keyLeft','keyRight','.forwardImpulse','.leftImpulse']) and any(i.get('operand')==2.0 for i in ins)
    assert hits(b('client/event/ClientEvent','ClientEvent'),'IEventBus.addListener(')
    ins=b('event/ServerEventHandler','onLivingDamage');assert hits(ins,'.getDirectEntity(') and hits(ins,'.getEntity(') and hits(ins,'EFFECTBLAZING_BRAND')
    ins=b('event/ServerEventHandler','onCriticalAttack');assert offset(ins,'THE_IMMOLATOR')<offset(ins,'EFFECTBLAZING_BRAND')<offset(ins,'.setCriticalHit(')
    for n in ['Ignis_Fireball_Entity','Ignis_Abyss_Fireball_Entity']:
        ins=b('entity/projectile/'+n,'onHitEntity');assert offset(ins,'.getFired(')<offset(ins,'.hurt(')<offset(ins,'IgnisExplosion.<init>')<offset(ins,'.discard(')<offset(ins,'EFFECTBLAZING_BRAND')<offset(ins,'.removeEffectNoUpdate(')<offset(ins,'.addEffect(')
    for short,name,field in [('items/Ignitium_Armor','onKeyPacket','EFFECTBLAZING_BRAND'),('entity/projectile/Water_Spear_Entity','onHitEntity','EFFECTWETNESS'),('entity/effect/Wave_Entity','attackEntities','EFFECTWETNESS')]:
        ins=b(short,name);assert offset(ins,field)<offset(ins,'.removeEffectNoUpdate(')<offset(ins,'.addEffect(')
    ins=body('net/minecraft/world/entity/LivingEntity','removeEffectNoUpdate');assert hits(ins,'Map.remove(') and not hits(ins,'.onEffectRemoved(')
    ins=body('net/minecraft/world/entity/LivingEntity','onEffectRemoved');assert hits(ins,'.removeAttributeModifiers(')
    ins=b('entity/projectile/Storm_Serpent_Entity','damage');assert offset(ins,'.magic(')<offset(ins,'.indirectMagic(')<offset(ins,'EFFECTWETNESS') and len(hits(ins,'.addEffect('))==1
    ins=b('entity/projectile/Cursed_Sandstorm_Entity','onHitEntity');assert offset(ins,'.causeMaledictioSagittaDamage(')<offset(ins,'.magic(')<offset(ins,'EFFECTCURSE_OF_DESERT') and len(hits(ins,'.hurt('))==2
    coverage=read_json(OUT/'cataclysm-status-coverage.json');assert status_coverage()==coverage and coverage['field_reference_methods']==74 and len(coverage['effect_ids'])==12
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==6 and len(d['delivery_paths'])==30 and sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==3
    assert len(d['reference_dispositions'])==26 and d['status_cores_reviewed_total']==12 and not d['remaining_subsection_native_ambiguities'];preserved=preserve_section(d);assert preserved==dict(effects=669,sources=1620,paths=1620,comparisons=669,primitives=882)
    return dict(schema='tno.external_effects.cataclysm_remaining_status_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=25,reference_witnesses=3,reference_methods=26,status_cores_reviewed=12,all_custom_effect_reader_methods=74,mechanic_packages=6,delivery_paths=30,numeric_scaling_points=3,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_remaining_status();write_json(OUT/'cataclysm-r2k2e-integrity.json',d);print(json.dumps(d,indent=2))
