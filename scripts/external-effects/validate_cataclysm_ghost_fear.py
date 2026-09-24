from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_cataclysm_ghost_fear import usages,PKG
from assemble_cataclysm_ghost_fear import CP,STEM,FACTS
from cataclysm_combat_common import preserve_section

def validate_ghost_fear():
    e=read_json(OUT/'native-evidence/cataclysm-ghost-fear.json');assert collect(read_json(OUT/'native-specifications/cataclysm-ghost-fear.json'))==e and len(e['witnesses'])==9
    r=read_json(OUT/'reference-evidence/cataclysm-ghost-fear-244.json');assert reference_collect(read_json(OUT/'reference-specifications/cataclysm-ghost-fear-244.json'))==r and len(r['witnesses'])==3
    u=read_json(OUT/'cataclysm-ghost-fear-usages.json');assert usages()==u and len(u['rows'])==12
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(path,name):return next(m['instructions'] for m in w[path+'.class']['methods'] if m['name']==name)
    def b(short,name):return body(PKG+short,name)
    def hits(ins,s):return [i for i in ins if s in str(i.get('operand',''))]
    def offset(ins,s):return hits(ins,s)[0]['offset']
    ins=b('event/ServerEventHandler','DeathEvent');assert offset(ins,'BYPASSES_INVULNERABILITY')<offset(ins,'.tryCursiumPlateRebirth(')<offset(ins,'.setCanceled(')
    ins=b('event/ServerEventHandler','tryCursiumPlateRebirth');assert offset(ins,'ServerLevel')<offset(ins,'EFFECTGHOST_SICKNESS')<offset(ins,'EFFECTGHOST_FORM')<offset(ins,'.setHealth(')<offset(ins,'.addEffect(')
    assert any(i.get('operand')==5.0 for i in ins) and not hits(ins,'.heal(') and len(hits(ins,'.addEffect('))==2
    # Both native addEffect results are discarded, not gates on revival success.
    for pos,i in enumerate(ins):
        if '.addEffect(' in str(i.get('operand','')):assert ins[pos+1]['opcode']=='0x57'
    ins=b('effects/EffectGhostForm','applyEffectTick');assert offset(ins,'.lastDuration')<offset(ins,'EFFECTGHOST_SICKNESS')<offset(ins,'.addEffect(') and any(i.get('operand')==7200 for i in ins)
    ins=b('effects/EffectGhost_Sickness','fillEffectCures');assert len(ins)==1 and ins[0]['opcode']=='0xb1'
    ins=b('event/ServerEventHandler','preventEffectRemoval');assert offset(ins,'.getEffect(')<offset(ins,'EFFECTGHOST_SICKNESS')<offset(ins,'DeferredHolder.get(')<offset(ins,'.setCanceled(') and any(i['opcode']=='0xa6' for i in ins)
    ins=body('net/minecraft/world/entity/LivingEntity','removeEffectsCuredBy');assert offset(ins,'.getCures(')<offset(ins,'.contains(')<offset(ins,'EventHooks.onEffectRemoved(')
    ins=body('net/minecraft/world/entity/LivingEntity','removeEffect');assert hits(ins,'EventHooks.onEffectRemoved(') and not hits(ins,'.getCures(')
    ins=body('net/minecraft/world/entity/LivingEntity','setHealth');assert hits(ins,'Mth.clamp(') and not hits(ins,'onLivingHeal')
    ins=b('event/ServerEventHandler','BlockHeal');assert offset(ins,'EFFECTABYSSAL_FEAR')<offset(ins,'.setCanceled(')
    ins=b('effects/EffectBlessing_Of_Amethyst','applyEffectTick');assert len(hits(ins,'.removeEffect('))==3 and offset(ins,'EFFECTABYSSAL_BURN')<offset(ins,'EFFECTABYSSAL_FEAR')<offset(ins,'DARKNESS')
    ins=b('entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Mine_Entity','explode');assert len(hits(ins,'.explode('))==2 and len(hits(ins,'.addEffect('))==2 and not hits(ins,'.hurt(')
    ins=b('entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Orb_Entity','onHitEntity');assert hits(ins,'.mobProjectile(') and hits(ins,'.magic(') and offset(ins,'.hurt(')<offset(ins,'.addEffect(')<offset(ins,'.explode(')<offset(ins,'.discard(')
    ins=b('init/ModItems','lambda$static$226');assert hits(ins,'REGENERATION') and hits(ins,'EFFECTBLESSING_OF_AMETHYST') and any(i.get('operand')==1800 for i in ins)
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==6 and len(d['delivery_paths'])==13 and sum(m['stage_scaling_needed'] for m in d['mechanic_packages'])==1
    assert len(d['reference_dispositions'])==12 and not d['remaining_subsection_native_ambiguities'];preserved=preserve_section(d);assert preserved==dict(effects=669,sources=1620,paths=1620,comparisons=669,primitives=882)
    return dict(schema='tno.external_effects.cataclysm_ghost_fear_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=9,reference_witnesses=3,reference_methods=12,mechanic_packages=6,delivery_paths=13,numeric_scaling_points=1,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_ghost_fear();write_json(OUT/'cataclysm-r2k2c-integrity.json',d);print(json.dumps(d,indent=2))
