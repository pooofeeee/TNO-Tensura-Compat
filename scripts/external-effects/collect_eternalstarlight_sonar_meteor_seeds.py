from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from collect_eternalstarlight_foundation import ES,targets

CLASSES={
 'common/mixin/ServerLevelMixin':['tickPrecipitation'],
 'common/entity/living/animal/CrystallizedMoth':['<init>','registerGoals','createAttributes','hurt','mobInteract','isFood','wantsToAttack','checkFallDamage'],
 'common/entity/living/animal/CrystallizedMoth$CrystallizedMothAttackGoal':None,
 'common/entity/projectile/SonarBomb':['<init>','onHit'],
 'common/item/combat/SonarBombItem':['use','asProjectile'],
 'common/entity/projectile/AethersentMeteor':['<init>','defineSynchedData','createMeteorShower','setSize','setTarget','setTargetPos','onHit','tick','dropAndDiscard','getDimensions','hurt','isPickable','readAdditionalSaveData','addAdditionalSaveData'],
 'common/item/combat/RageOfStarsItem':['performSpecialAttack','postHurtEnemy','performSwingAttack'],
 'common/item/combat/StarfallLongbowItem':['createProjectile'],
 'common/item/armor/AethersentArmorItem':None,
 'common/weather/MeteorShowerWeather':['tickBlock','serverTick'],
 'common/entity/projectile/ShotSeeds':None,
 'common/item/combat/SeedsLauncherItem':None,
 'common/item/combat/SeedsLauncherAmmoType':None,
 'common/entity/living/monster/Stranghoul':['registerGoals','performRangedAttack','getProjectile'],
 'common/entity/living/monster/Stranghoul$SeedsLauncherAttackGoal':None,
 'common/handler/ESCommonHandler':['onPostLivingHurt','onEntityTick','onProjectileImpact'],
 'common/config/ESConfig$ItemsConfig':['<init>'],
 'common/config/ESConfig$MobsConfig':['<init>'],
 'common/registry/ESAttributes':None,
}

def census():
    t=targets()['eternalstarlight'];rows=[]
    needles=['ESDamageTypes.SONAR','ESDamageTypes.METEOR','ESDamageTypes.SEEDS','AethersentMeteor.createMeteorShower(','SeedsLauncherItem.performShooting(','ESEntities.AETHERSENT_METEOR','METEOR_COUNTERATTACK_CHANCE','starfall','ESItems.SONAR_BOMB','AbstractWeather.tickBlock(']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if (i['opcode']=='0xbb' and any(str(i['operand']).endswith('/'+s) for s in ['AethersentMeteor','ShotSeeds','SonarBomb'])) or any(s in str(i['operand']) for s in needles)]
                if hits:rows.append(dict(entry=n,sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole JAR sonar/meteor/seeds actual source calls, producers, meteor chance and starfall delivery census.',rows=rows)

def save():
    t=targets()['eternalstarlight'];rows=[];c=census()
    for r in c['rows']:
        if any(s in r['entry'] for s in ['ESCommonSetupHandler','/mixin/ServerLevelMixin']):
            CLASSES.setdefault(r['entry'][len(ES):-6],[]).append(r['method'])
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=ES+short+'.class';cl=ClassFile(z.read(n));names=wanted if wanted is not None else sorted({m['name'] for m in cl.methods});names=sorted(set(names)|{m['name'] for m in cl.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='es:sms:'+short,mod_key='eternalstarlight',entry=n,methods=names))
        for n in sorted(z.namelist()):
            if n.endswith('.json') and any(v in n for v in ['vulnerable_to_sonar','seeds_launcher_ammo']):rows.append(dict(id='es:sms:data:'+n,mod_key='eternalstarlight',entry=n))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Native sonar, meteor and seed payloads and actual producers, static only.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/eternalstarlight-sonar-meteor-seeds.json',s);write_json(OUT/'native-evidence/eternalstarlight-sonar-meteor-seeds.json',collect(s));write_json(OUT/'eternalstarlight-sonar-meteor-seeds-census.json',c)
    # Moth wantsToAttack has a failed source decompilation; pin javap branches as an aid.
    cmd=['C:/Program Files/Java/jdk-21/bin/javap.exe','-classpath',t['path'],'-p','-c','cn.leolezury.eternalstarlight.common.entity.living.animal.CrystallizedMoth']
    p=subprocess.run(cmd,capture_output=True,text=True,check=True);s=p.stdout;s=s[s.index('  public boolean wantsToAttack('):s.index('  public boolean removeWhenFarAway(')]
    (OUT/'eternalstarlight-moth-target-javap.txt').write_text('\n'.join(x.rstrip() for x in s.splitlines()).rstrip()+'\n',encoding='utf-8')
    config=MODS.parent/'config/eternal_starlight.json';v=read_json(config);write_json(OUT/'eternalstarlight-meteor-config-snapshot.json',dict(path=str(config),sha256=sha256(config),values=dict(playerAethersentMeteorDamageScale=v['itemsConfig']['playerAethersentMeteorDamageScale'],crystallizedMoth=v['mobsConfig']['crystallizedMoth']),scope='File snapshot only, not loaded runtime configuration.'))
    print('Sonar/meteor/seeds witnesses saved')
if __name__=='__main__':save()
