from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_eternalstarlight_foundation import ES,targets

CLASSES={
 'common/entity/living/boss/monstrosity/LunarMonstrosity':['<init>','createAttributes','blockedByShield','doHurtTarget','hurt','addEffect','isAlliedTo','mobInteract','getDefaultDimensions','getNormalStateBoundingBox','canBite','doBiteDamage','knockbackNearbyEntities','ignoreExplosion','aiStep'],
 'common/entity/living/boss/monstrosity/LunarMonstrosity$LunarMonstrosityMeleeAttackGoal':None,
 'common/entity/attack/LunarThorn':['tick','hurt','readAdditionalSaveData','addAdditionalSaveData','setOwner'],
 'common/entity/attack/PoisonousCloud':['tick','hurt','readAdditionalSaveData','addAdditionalSaveData','setOwner'],
 'common/entity/attack/TangledHusk':['tick','hurt','readAdditionalSaveData','addAdditionalSaveData','setOwner'],
 'common/entity/projectile/LunarSpore':['<init>','tick','onHit','explodeAndDiscard','hurt','isPickable'],
 'common/entity/attack/ray/LunarMonstrosityBreath':['getAttackDamage','doHurtTarget','updatePosition'],
 'common/item/combat/MoonringBowItem':['createProjectile','releaseUsing','createThorn'],
 'common/item/combat/PetalScytheItem':['performSpecialAttack','performSwingAttack','postHurtEnemy'],
 'common/item/combat/WandOfTeleportationItem':['use','teleportPlayer','createThornCircle'],
 'neoforge/platform/ESNeoPlatform':['postTeleportEvent'],
 'common/entity/living/monster/TangledSkull':['<init>','registerGoals','createAttributes','tick','tickDeath','getTarget','setDeltaMovement','hurt','isAlliedTo','readAdditionalSaveData','addAdditionalSaveData'],
 'common/entity/living/monster/TangledSkull$TangledSkullChargeAttackGoal':None,
 'common/item/combat/TangledSkullItem':['use'],
 'common/entity/living/monster/Tangled':['<init>','customServerAiStep','doHurtTarget','tickDeath','createAttributes','isAlliedTo'],
 'common/entity/living/phase/MeleeAttackPhase':None,
}
for n in ['Bite','Dig','Emerge','Sneak','Soul','Spore','Stun','Thorn','ToxicBreath']:CLASSES['common/entity/living/boss/monstrosity/LunarMonstrosity'+n+'Phase']=None

def producer_census():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if (i['opcode']=='0xbb' and any(str(i['operand']).endswith('/'+s) for s in ['LunarSpore','LunarThorn','PoisonousCloud','TangledHusk','TangledSkull','LunarMonstrosityBreath'])) or (i['opcode']=='0xb2' and any(s in str(i['operand']) for s in ['ESEntities.TANGLED_HUSK','ESEntities.POISONOUS_CLOUD','ESEntities.LUNAR_THORN'])) or (i['opcode'] in ['0xb6','0xb8'] and ('MoonringBowItem.createThorn(' in str(i['operand']) or 'TangledSkull.setShot(' in str(i['operand'])))]
                if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole ES-JAR lunar hazard/skull producer and shot-state census; registry/render rows are not extra combat paths.',rows=rows)

def save():
    t=targets()['eternalstarlight'];rows=[];census=producer_census()
    for r in census['rows']:
        if 'ESCommonSetupHandler$' in r['entry']:CLASSES[r['entry'][len(ES):-6]]=None
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=ES+short+'.class';c=ClassFile(z.read(n));names=wanted if wanted is not None else sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='es:lunar:'+short,mod_key='eternalstarlight',entry=n,methods=names))
        for n in ['data/eternal_starlight/tags/entity_type/lunar_monstrosity_allies.json','data/eternal_starlight/tags/item/lunar_monstrosity_igniters.json']:
            rows.append(dict(id='es:lunar:data:'+n,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Lunar boss/control, poison damage hazards and weapon producers, Tangled/Skull native HP and explosions; soul transition is not SOUL_ABSORB.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-lunar.json',s);write_json(OUT/'native-evidence/eternalstarlight-lunar.json',collect(s));write_json(OUT/'eternalstarlight-lunar-producer-census.json',census)
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    a['classes']={'net/minecraft/world/level/Explosion.class':['getIndirectSourceEntityInternal','getIndirectSourceEntity','getDirectSourceEntity'],'net/minecraft/world/entity/LivingEntity.class':['hurt','blockUsingShield','blockedByShield','randomTeleport']}
    r=dict(id='eternalstarlight-lunar-244',scope='Shield-block callback and native random teleport admission; skull explosion exact direct/causing resolution.',archives=[a])
    write_json(OUT/'reference-specifications/eternalstarlight-lunar-244.json',r);write_json(OUT/'reference-evidence/eternalstarlight-lunar-244.json',reference_collect(r,source_aids=True))
    print('Lunar combat witnesses saved')
if __name__=='__main__':save()
