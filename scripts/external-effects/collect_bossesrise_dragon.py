from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_foundation import targets,KEY,PKG

DRAGON='entity/boss/dragon/boss/InfernalDragonEntity'
GUARDS=['DragonGuardSword','FlamingSkeletonGuardSword','FlamingSkeletonGuardFireball']
CLASSES={DRAGON:None,'entity/projectile/BlazingFireBallEntity':None,'entity/FireAreaEntity':None,'entity/boss/yeti/IceSpikeProjectileEntity':['onHitEntity'], 'init/BossesRiseEntities':['<clinit>'],'configuration/ServerConfiguration':['<clinit>'],**{'entity/boss/dragon/guardians/'+s+'Entity':None for s in GUARDS},**{'procedures/'+s+'OnEntityTickUpdateProcedure':None for s in GUARDS},**{'procedures/BlazingFireBall'+s+'Procedure':None for s in ['ProjectileHitsLivingEntity','ProjectileHitsBlock','WhileProjectileFlyingTick']}}

def census():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if i['opcode'] in ['0xbb','0xb2','0xb3','0xb6','0xb7','0xb8','0xb9'] and str(i.get('operand','')).startswith(PKG) and any(v in str(i.get('operand','')) for v in ['BlazingFireBallEntity','FireAreaEntity','.FIRE_AREA','.DRAGON_ATK','DragonGuardSwordEntity','FlamingSkeletonGuardSwordEntity','FlamingSkeletonGuardFireballEntity','.DATA_HIT_ANIMTIME','.DATA_SPAWN_ANIMTIME'])]
                if hits:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Actual native instructions for fireball/hazard/guardian construction, dormant Dragon damage config and legacy admission counters. Registry method references separately pinned.',rows=rows)

def profiles():
    source=read_json(OUT/'bossesrise-damage-tags.json');table={}
    for r in source['resources']:
        n=r['entry'];tag=n.split('/')[1]+':'+n.split('/tags/damage_type/')[1][:-5];d=r['data']
        if d.get('replace'):table[tag]=[]
        table.setdefault(tag,[]).extend(d.get('values',[]))
    def members(tag,seen=()):
        if tag in seen:return set()
        result=set()
        for v in table.get(tag,[]):
            v=v['id'] if isinstance(v,dict) else v
            result|=members(v[1:],seen+(tag,)) if v.startswith('#') else {v}
        return result
    return dict(scope=source['scope'],reference_file='bossesrise-damage-tags.json',reference_sha256=sha256(OUT/'bossesrise-damage-tags.json'),profiles=[dict(id='minecraft:'+n,tags=sorted(t for t in table if 'minecraft:'+n in members(t))) for n in ['mob_attack','arrow','magic','in_fire','on_fire','explosion','player_attack','indirect_magic']])

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        selected=dict(CLASSES)
        for n in z.namelist():
            if n.endswith('.class') and any(n.startswith(PKG+k+'$') for k in CLASSES):selected[n[len(PKG):-6]]=None
        for short,wanted in sorted(selected.items()):
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='br:dragon:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Infernal Dragon defense, attacks, Blazing Fireball/Fire Area and three guardians; Ice Spike witness only resolves Dragon causing-entity predicate. Equipment producer reserved for equipment family.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-dragon.json',s);write_json(OUT/'native-evidence/bossesrise-dragon.json',collect(s));write_json(OUT/'bossesrise-dragon-census.json',census());write_json(OUT/'bossesrise-dragon-source-profiles.json',profiles())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={}
    wanted={'net/minecraft/world/level/Explosion':['<init>','explode','finalizeExplosion','makeDamageCalculator','getIndirectSourceEntity','getIndirectSourceEntityInternal','getSeenPercent'],'net/minecraft/world/level/ExplosionDamageCalculator':['getEntityDamageAmount','shouldDamageEntity','getKnockbackMultiplier'],'net/minecraft/world/level/Level':['explode'],'net/minecraft/server/level/ServerLevel':['explode'],'net/minecraft/world/entity/Entity':['igniteForSeconds','igniteForTicks','baseTick','setRemainingFireTicks'],'net/minecraft/world/entity/LivingEntity':['hurt','getDamageAfterMagicAbsorb'],'net/minecraft/world/level/block/BaseFireBlock':['entityInside'],'net/minecraft/world/level/block/FireBlock':['<init>'],'net/minecraft/world/damagesource/DamageSources':['explosion','inFire','onFire','magic']}
    raw={}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():
                c=ClassFile(z.read(k+'.class'));a['classes'][k+'.class']=v+[m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+n+'$') for n in v)]
            else:raw[k]=v
    r=dict(id='bossesrise-dragon-244',scope='Installed fire/ignition/HP admission and Fire Area explosion source/formula; no runtime certification.',archives=[a]);write_json(OUT/'reference-specifications/bossesrise-dragon-244.json',r);write_json(OUT/'reference-evidence/bossesrise-dragon-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=['data/minecraft/damage_type/'+n+'.json' for n in ['arrow','magic','mob_attack','in_fire','on_fire','explosion','player_attack']]);write_json(OUT/'vanilla-specifications/bossesrise-dragon.json',s);write_json(OUT/'vanilla-evidence/bossesrise-dragon.json',prepare(s));write_json(OUT/'reference-routing/bossesrise-dragon.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]))
    print('Dragon native/reference evidence pinned')

if __name__=='__main__':save()
