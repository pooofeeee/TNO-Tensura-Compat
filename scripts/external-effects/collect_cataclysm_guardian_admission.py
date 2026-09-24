from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_cataclysm_foundation import targets,KEY,PKG

G='entity/AnimationMonster/BossMonsters/Ender_Guardian_Entity'
MAIN=['<init>','defineSynchedData','registerGoals','ender_guardian','addAdditionalSaveData','readAdditionalSaveData','setIsHelmetless','getIsHelmetless','setUsedMassDestruction','getUsedMassDestruction','setTeleportPos','getTeleportPos','hurt','DamageCap','DpsCap','RangeLimit','NatureRegen','isInvulnerableTo','tick','isHelmetless','BrokenHelmet','teleport','ProperTeleport']
ALL=[G+'$1',G+'$HugmeGoal',G+'$TeleportStrikeGoal','entity/AnimationMonster/AI/AnimationGoal','entity/AnimationMonster/AI/SimpleAnimationGoal','entity/AnimationMonster/AI/AttackAnimationGoal2','blockentities/AltarOfVoid_Block_Entity','config/CMCommonConfig$EnderGuardian']

def setter_calls():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(z.namelist()):
            if not n.endswith('.class'):continue
            c=ClassFile(z.read(n))
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and any(PKG+G+'.'+s in str(i.get('operand','')) for s in ['setIsHelmetless(','setUsedMassDestruction('])]
                if hits:rows.append(dict(entry=n,method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(schema='tno.external_effects.cataclysm_guardian_state_callers.v1',jar_sha256=t['sha256'],rows=rows,scope='All installed Cataclysm bytecode callers of the two concrete state setters; external mods/NBT inputs are not excluded.')

def save():
    t=targets()[KEY];wanted={G:MAIN,'blocks/Altar_Of_Void_Block':['getTicker'],'init/ModEntities':['initializeAttributes']}
    with zipfile.ZipFile(t['path']) as z:
        for s in ALL:wanted[s]=sorted({m['name'] for m in ClassFile(z.read(PKG+s+'.class')).methods})
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Ender Guardian incoming admission, persistent helmet/mass state, native altar prerequisite, phase burst and two attack teleports. Attack payloads remain pending.',evidence_specifications=[dict(id='cataclysm:guardian-admission:'+k,mod_key=KEY,entry=PKG+k+'.class',methods=v) for k,v in wanted.items()])
    write_json(OUT/'native-specifications/cataclysm-guardian-admission.json',s);write_json(OUT/'native-evidence/cataclysm-guardian-admission.json',collect(s));write_json(OUT/'cataclysm-guardian-state-callers.json',setter_calls())
    originals=read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'];a=dict(originals[0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/level/Explosion.class':['makeDamageCalculator'],'net/minecraft/world/level/Level$ExplosionInteraction.class':['*']}
    b=dict(originals[1]);b.pop('semantic_review',None);b['classes']={'net/neoforged/neoforge/event/EventHooks.class':['onEnderTeleport'],'net/neoforged/neoforge/event/entity/EntityTeleportEvent$EnderEntity.class':['*']}
    r=dict(id='cataclysm-guardian-admission-244',scope='Actual posted Ender teleport event and native explosion calculator/interaction dispatch; reuse protected explosion and source witnesses.',archives=[a,b]);write_json(OUT/'reference-specifications/cataclysm-guardian-admission-244.json',r);write_json(OUT/'reference-evidence/cataclysm-guardian-admission-244.json',reference_collect(r,source_aids=True))
    v=dict(classes={'net/minecraft/world/level/EntityBasedExplosionDamageCalculator':['<init>','getBlockExplosionResistance','shouldBlockExplode']});write_json(OUT/'vanilla-specifications/cataclysm-guardian-admission.json',v);write_json(OUT/'vanilla-evidence/cataclysm-guardian-admission.json',prepare(v));print('Guardian witnesses',len(wanted),'setter caller methods',len(setter_calls()['rows']))

if __name__=='__main__':save()
