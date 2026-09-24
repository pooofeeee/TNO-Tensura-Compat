from catalog_common import *
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_cataclysm_stun import usages,PKG
from assemble_cataclysm_stun import CP,STEM,FACTS
from cataclysm_combat_common import preserve_section

def validate_stun():
    e=read_json(OUT/'native-evidence/cataclysm-stun.json');assert collect(read_json(OUT/'native-specifications/cataclysm-stun.json'))==e and len(e['witnesses'])==22
    r=read_json(OUT/'reference-evidence/cataclysm-stun-244.json');assert reference_collect(read_json(OUT/'reference-specifications/cataclysm-stun-244.json'))==r and len(r['witnesses'])==10
    assert prepare(read_json(OUT/'vanilla-specifications/cataclysm-stun.json'))==read_json(OUT/'vanilla-evidence/cataclysm-stun.json')
    u=read_json(OUT/'cataclysm-stun-usages.json');assert usages()==u and len(u['rows'])==34
    w={x['entry']:x for x in e['witnesses']+r['witnesses']}
    def body(path,name):return next(m['instructions'] for m in w[path+'.class']['methods'] if m['name']==name)
    def b(short,name):return body(PKG+short,name)
    def hits(ins,s):return [i for i in ins if s in str(i.get('operand',''))]
    def offset(ins,s):return hits(ins,s)[0]['offset']
    ins=b('effects/EffectStun','<init>');assert hits(ins,'MOVEMENT_SPEED') and hits(ins,'ADD_VALUE') and any(i.get('operand')==-.5 for i in ins)
    assert not any(hits(b('effects/EffectStun','applyEffectTick'),s) for s in ['.hurt(','.setHealth(','.setDeltaMovement('])
    ins=b('mixin/LivingEntityMixin','dev1_21_1$handleStunEffectLogic');assert offset(ins,'Holder.equals(')<offset(ins,'.isEquipped(')<offset(ins,'.isOnCooldown(')<offset(ins,'.addCooldown(')<offset(ins,'.setReturnValue(') and any(i.get('operand')==900 for i in ins)
    for name in ['onAddEffect','onAddEffectWithSource']:assert hits(b('mixin/LivingEntityMixin',name),'handleStunEffectLogic')
    ins=b('util/EntityUtil','isEquipped');assert hits(ins,'CuriosApi.getCuriosInventory(')
    assert any(hits(m['instructions'],'.findFirstCurio(') for m in w[PKG+'util/EntityUtil.class']['methods'])
    ins=b('event/ServerEventHandler','onLivingDamage');assert offset(ins,'.getHealth(')<offset(ins,'.getNewDamage(')<offset(ins,'EFFECTSTUN')<offset(ins,'.removeEffect(')
    for path in ['net/minecraft/world/entity/LivingEntity','net/minecraft/world/entity/player/Player']:
        ins=body(path,'actuallyHurt');assert offset(ins,'.setHealth(')<offset(ins,'CommonHooks.onLivingDamagePost(')
    for name in ['onPlayerAttack','onPlayerLeftClick','onPlaceBlock','onBreakBlock','onPlayerInteract3','onPlayerInteract4','onPlayerInteract5','onPlayerInteract']:
        ins=b('event/ServerEventHandler',name);assert offset(ins,'EFFECTSTUN')<offset(ins,'.setCanceled(')
    ins=b('event/ServerEventHandler','onUseItem');assert hits(ins,'.setDuration(') and not hits(ins,'.setCanceled(')
    ins=b('message/MessageSwingArm','lambda$handle$0');assert hits(ins,'.onLeftClick(') and not hits(ins,'EFFECTSTUN')
    filters=[x for x in u['rows'] if x['method']=='canBeAffected'];assert len(filters)==7
    for row in filters:
        ins=body(row['entry'][:-6],'canBeAffected');assert any(i['opcode']=='0xa5' for i in ins) and hits(ins,'EFFECTSTUN') and not hits(ins,'.equals(')
    # Post-admission status calls retain actual native hurt-success gates in the pinned methods.
    for short,name in [('entity/projectile/Accretion_Entity','onHitEntity'),('entity/effect/Wall_Watcher_Entity','tick')]:
        ins=b(short,name);assert offset(ins,'.hurt(')<offset(ins,'EFFECTSTUN')<offset(ins,'.addEffect(')
    ins=b('entity/projectile/Accretion_Entity','onHitEntity');assert hits(ins,'.mobProjectile(') and hits(ins,'.inWall(') and hits(ins,'.getEffectSource(')
    ins=b('entity/effect/Wall_Watcher_Entity','tick');assert offset(ins,'.horizontalCollision')<offset(ins,'.invulnerableTime')<offset(ins,'.hurt(')
    ins=b('entity/InternalAnimationMonster/AcropolisMonsters/Hippocamtus_Entity','hurt');assert offset(ins,'.getDirectEntity(')<offset(ins,'BYPASSES_SHIELD')<offset(ins,'EFFECTSTUN')
    d=read_json(OUT/(STEM+'.json'));assert d['facts']==FACTS and len(d['mechanic_packages'])==3 and len(d['delivery_paths'])==18 and not any(m['stage_scaling_needed'] for m in d['mechanic_packages'])
    assert {(r['entry'],r['method'],r['descriptor']) for r in d['stun_reference_dispositions']}=={(r['entry'],r['method'],r['descriptor']) for r in u['rows']}
    assert not d['remaining_subsection_native_ambiguities'];preserved=preserve_section(d);assert preserved==dict(effects=669,sources=1620,paths=1620,comparisons=669,primitives=882)
    return dict(schema='tno.external_effects.cataclysm_stun_integrity.v1',baseline=BASELINE,checkpoint=CP,status='PASS',native_witnesses=22,reference_witnesses=10,stun_reference_methods=34,mechanic_packages=3,delivery_paths=18,numeric_scaling_points=0,accepted_counts_preserved=preserved,promoted_records=0,whole_mod_complete=False,runtime_tests=0,**boundary_flags())

if __name__=='__main__':
    d=validate_stun();write_json(OUT/'cataclysm-r2k2b-integrity.json',d);print(json.dumps(d,indent=2))
