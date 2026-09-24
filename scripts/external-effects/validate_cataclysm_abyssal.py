from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_cataclysm_abyssal import usages,PKG
from assemble_cataclysm_abyssal import CP,STEM,FACTS
from cataclysm_combat_common import preserve_section

def validate_abyssal():
    e=read_json(OUT/'native-evidence/cataclysm-abyssal.json');assert collect(read_json(OUT/'native-specifications/cataclysm-abyssal.json'))==e and len(e['witnesses'])==15
    r=read_json(OUT/'reference-evidence/cataclysm-abyssal-244.json');assert reference_collect(read_json(OUT/'reference-specifications/cataclysm-abyssal-244.json'))==r and len(r['witnesses'])==3
    u=read_json(OUT/'cataclysm-abyssal-usages.json');assert usages()==u and len(u['rows'])==13 and len(u['damage_callers'])==2
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(path,name):return next(m['instructions'] for m in w[path+'.class']['methods'] if m['name']==name)
    def b(short,name):return body(PKG+short,name)
    def hits(ins,s):return [i for i in ins if s in str(i.get('operand',''))]
    def offset(ins,s):return hits(ins,s)[0]['offset']
    for short in ['effects/EffectAbyssal_Burn','effects/EffectAbyssal_Curse']:
        ins=b(short,'applyEffectTick');assert offset(ins,'CMDamageTypes.ABYSSAL_BURN')<offset(ins,'DamageSources.source(Lnet/minecraft/resources/ResourceKey;)')<offset(ins,'.hurt(') and any(i.get('operand')==1.0 for i in ins)
        ins=b(short,'shouldApplyEffectTickThisTick');assert any(i.get('operand')==40 for i in ins) and any(i['opcode']=='0x7a' for i in ins)
    ins=b('effects/EffectAbyssal_Curse','applyEffectTick');assert not hits(ins,'.randomTeleport') and ins[next(i for i,x in enumerate(ins) if '.hurt(' in str(x.get('operand','')))+1]['opcode']=='0x57'
    ins=b('effects/EffectAbyssal_Burn','applyEffectTick');assert offset(ins,'.hurt(')<offset(ins,'.nextFloat(')<offset(ins,'.getHealth(')<offset(ins,'.isClientSide')<offset(ins,'.stopRiding(')<offset(ins,'.gameEvent(')<offset(ins,'ChorusFruit.<init>')<offset(ins,'.randomTeleportInwater(')
    assert any(i.get('operand')==.75 for i in ins) and any(i.get('operand')==8 for i in ins) and not hits(ins,'.post(') and not hits(ins,'.isCanceled(')
    ins=b('effects/EffectAbyssal_Burn','randomTeleportInwater');assert offset(ins,'.hasChunkAt(')<offset(ins,'.blocksMotion(')<offset(ins,'.teleportTo(')<offset(ins,'.noCollision(')<hits(ins,'.teleportTo(')[1]['offset']<offset(ins,'.broadcastEntityEvent(')<offset(ins,'.getNavigation(')
    assert not any(hits(ins,s) for s in ['.containsAnyLiquid(','.getFluidState(','.randomTeleport('])
    filters=[x for x in u['rows'] if x['method']=='canBeAffected'];assert len(filters)==9
    for row in filters:
        ins=body(row['entry'][:-6],'canBeAffected');assert hits(ins,'DeferredHolder.get(') and any(i['opcode']=='0xa5' for i in ins)
    for n in ['Abyss_Blast_Entity','Portal_Abyss_Blast_Entity']:
        ins=b('entity/AnimationMonster/BossMonsters/The_Leviathan/'+n,'tick');assert offset(ins,'.causeDeathLaserDamage(')<offset(ins,'.hurt(')<offset(ins,'EFFECTABYSSAL_BURN')<offset(ins,'.removeEffectNoUpdate(')<offset(ins,'.addEffect(')
    ins=b('entity/projectile/Tidal_Tentacle_Entity','tick');assert offset(ins,'.mobProjectile(')<offset(ins,'.hurt(')<offset(ins,'EFFECTABYSSAL_CURSE')<offset(ins,'.removeEffectNoUpdate(')<offset(ins,'.addEffect(')
    tag=next(x for x in read_json(OUT/'cataclysm-damage-tags.json')['declarations'] if x['id']=='cataclysm:abyssal_burn');assert tag['data']==dict(exhaustion=.1,message_id='cataclysm.abyssal_burn',scaling='never') and len(tag['tags'])==5 and 'minecraft:bypasses_cooldown' not in tag['tags']
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==3 and len(d['delivery_paths'])==9 and sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==1
    assert len(d['reference_dispositions'])==13 and d['damage_types_reviewed'][0]['disposition']=='USED' and not d['remaining_subsection_native_ambiguities'];preserved=preserve_section(d);assert preserved==dict(effects=669,sources=1620,paths=1620,comparisons=669,primitives=882)
    return dict(schema='tno.external_effects.cataclysm_abyssal_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=15,reference_witnesses=3,status_reference_methods=13,damage_type_callers=2,mechanic_packages=3,delivery_paths=9,numeric_scaling_points=1,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_abyssal();write_json(OUT/'cataclysm-r2k2d-integrity.json',d);print(json.dumps(d,indent=2))
