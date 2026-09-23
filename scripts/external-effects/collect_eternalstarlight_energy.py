from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_eternalstarlight_foundation import ES,targets

CLASSES={
 'common/entity/projectile/EnergySpark':['tick','hurtTarget','onHitEntity','onHitBlock','setTarget','readAdditionalSaveData','addAdditionalSaveData'],
 'common/entity/projectile/BallLightning':['tick','explodeAndDiscard','onHitBlock','setTarget','readAdditionalSaveData','addAdditionalSaveData'],
 'common/entity/attack/EnergizedFlame':['tick','hurt','setOwner','readAdditionalSaveData','addAdditionalSaveData'],
 'common/entity/projectile/ThrownBoomerang':['tick','getItemDamage','onHitEntity','findHitEntity','isAcceptableReturnOwner'],
 'common/entity/projectile/ThrownEnergyBoomerang':['doPostHurtEffects'],
 'common/item/combat/EnergySwordItem':['postHurtEnemy'],
 'common/item/combat/MechanicalCrossbowItem':['createProjectile','shootProjectile'],
 'common/item/combat/GolemSteelGreatswordItem':['performSpecialAttack','performSwingAttack','postHurtEnemy'],
 'common/item/combat/BoomerangItem':['use','isTooDamagedToUse'],
 'common/item/combat/EnergyBoomerangItem':['createBoomerang','asProjectile'],
 'common/util/ESEntityUtil':['raytrace','shouldHarm'],
 'common/util/SpecialItemCooldown':None,
 'common/entity/living/boss/golem/StarlightGolem':['spawnEnergizedFlame'],
 'common/entity/living/boss/golem/StarlightGolemSummonFlamePhase':None,
 'common/entity/living/boss/golem/StarlightGolemLaserBeamPhase':None,
 'common/entity/living/boss/golem/StarlightGolemSmashPhase':None,
 'common/entity/misc/ESFallingBlock':['<init>','tick','hurt','readAdditionalSaveData','addAdditionalSaveData'],
 'common/data/ESEnchantments':['modifyBoomerangCritChance','modifyBoomerangHomingStrength'],
}

def hierarchy():
    a=read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0];rows=[]
    with zipfile.ZipFile(a['path']) as z:
        for n in ['net/minecraft/world/entity/Entity.class','net/minecraft/world/entity/projectile/Projectile.class','net/minecraft/world/entity/projectile/FireworkRocketEntity.class']:
            raw=z.read(n);c=ClassFile(raw);rows.append(dict(entry=n,sha256=byte_hash(raw),superclass=c.super,declared_methods=[dict(name=m['name'],descriptor=m['descriptor']) for m in c.methods],getWeaponItem=[list(c.instructions(m.get('code',b''))) for m in c.methods if m['name']=='getWeaponItem']))
    return dict(archive=a['path'],sha256=a['sha256'],scope='Firework/Projectile have no getWeaponItem override; exact Entity returns null.',classes=rows)

def producer_census():
    t=targets()['eternalstarlight'];rows=[]
    needles=['EnergizedFlame','EnergySpark','BallLightning','ThrownEnergyBoomerang','ESFallingBlock','registerProjectileBehavior','registerBehavior']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if (i['opcode']=='0xbb' and any(str(i['operand']).endswith('/'+x) for x in needles)) or (i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and any(x+'(' in str(i.get('operand','')) for x in ['registerProjectileBehavior','registerBehavior'])) or (i['opcode']=='0xb2' and 'ESEntities.ENERGIZED_FLAME' in str(i.get('operand','')))]
                if hits:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole ES-JAR constructor/flame-factory and dispenser-registration census; client rendering/registry constructor suppliers are not automatic delivery. Other ESFallingBlock producers are later family work.',rows=rows)

def save():
    t=targets()['eternalstarlight'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            entry=ES+short+'.class';c=ClassFile(z.read(entry));methods=wanted if wanted is not None else sorted({m['name'] for m in c.methods})
            methods=sorted(set(methods)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+n+'$') for n in methods)})
            rows.append(dict(id='es:energy:'+short,mod_key='eternalstarlight',entry=entry,methods=methods))
        for n in sorted(z.namelist()):
            if n.startswith('data/eternal_starlight/enchantment/') and any(s in z.read(n).decode() for s in ['boomerang_crit_chance','boomerang_homing_strength']):rows.append(dict(id='es:energy:data:'+n,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Energy Sparks, Ball Lightning, Energized Flame, Energy Boomerang and Starlight Golem smash payload/delivery; boss state/admission follows separately.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-energy.json',s);write_json(OUT/'native-evidence/eternalstarlight-energy.json',collect(s))
    write_json(OUT/'eternalstarlight-energy-producer-census.json',producer_census());write_json(OUT/'eternalstarlight-firework-weapon-hierarchy.json',hierarchy())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    a['classes']={'net/minecraft/world/entity/Entity.class':['getWeaponItem']}
    r=dict(id='eternalstarlight-energy-244',scope='Exact native default null weapon and ordinary falling-block/thrown/melee source identities.',archives=[a])
    write_json(OUT/'reference-specifications/eternalstarlight-energy-244.json',r);write_json(OUT/'reference-evidence/eternalstarlight-energy-244.json',reference_collect(r,source_aids=True))
    raw={'net/minecraft/world/damagesource/DamageSources':['fallingBlock','thrown','playerAttack','mobAttack','source']}
    with zipfile.ZipFile(a['path']) as z:assert not(set(k+'.class' for k in raw)&set(z.namelist()))
    v=dict(classes=raw,resources=[]);write_json(OUT/'vanilla-specifications/eternalstarlight-energy.json',v);write_json(OUT/'vanilla-evidence/eternalstarlight-energy.json',prepare(v))
    write_json(OUT/'reference-routing/eternalstarlight-energy.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    print('Energy witnesses saved')
if __name__=='__main__':save()
