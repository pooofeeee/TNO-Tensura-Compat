from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bomd_foundation import targets,KEY,PKG

CLASSES={
 **{'entity/custom/lich/'+n:None for n in ['LichEntity','LichActions','LichMoveLogic','VolleyAction','VolleyRageAction','CometAction','CometRageAction','MinionAction','MinionRageAction','TeleportAction']},
 'entity/ai/action/CooldownAction':None,'entity/ai/action/ThrowProjectileAction':None,'entity/ai/goals/ActionGoal':None,'entity/ai/goals/FindTargetGoal':None,
 'entity/util/ProjectileThrower':None,'projectile/BaseThrownItemProjectile':None,'projectile/MagicMissileProjectile':None,'projectile/comet/CometProjectile':None,'projectile/util/ExemptEntities':None,
 **{'entity/spawn/'+n:None for n in ['MobPlacementLogic','MobEntitySpawnPredicate','RangedSpawnPosition','SimpleMobSpawner','CompoundTagEntityProvider']},
 'entity/custom/lich/LichUtils':['timeToNighttime'],
 'entity/BMDEntities':['<clinit>'], 'util/VanillaCopiesServer':['hasDirectLineOfSight'],
}

def source_tags():
    from collect_bomd_foundation import tags
    table={}
    for r in tags()['resources']:
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
    return dict(scope='Same pinned Minecraft/NeoForge/BOMD closure as R2j1; other pack tags not certified.',types={n:sorted(k for k in table if n in members(k)) for n in ['minecraft:thrown','minecraft:player_explosion','minecraft:mob_attack','minecraft:generic_kill']})

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods})
            if short=='entity/BMDEntities':names+=sorted(m['name'] for m in c.methods if m['name'].startswith('lambda$static$'))
            rows.append(dict(id='bomd:lich:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Native Lich combat, projectile ownership/callbacks, minion and teleport placement; rendering-only methods are excluded semantically.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bomd-lich.json',s);write_json(OUT/'native-evidence/bomd-lich.json',collect(s))
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None)
    a['classes']={'net/minecraft/world/entity/projectile/Projectile.class':['setOwner','getOwner','canHitEntity','onHit','hitTargetOrDeflectSelf','deflect'], 'net/minecraft/world/entity/projectile/ThrowableProjectile.class':['<init>','tick'],'net/minecraft/world/level/Explosion.class':['<init>','getIndirectSourceEntity','getIndirectSourceEntityInternal','getDirectSourceEntity','explode'],'net/minecraft/world/entity/LivingEntity.class':['readAdditionalSaveData','kill'],'net/minecraft/world/entity/Mob.class':['doHurtTarget'],'net/minecraft/world/level/Level.class':['explode']}
    dep=MODS/'CerbonsAPI-NeoForge-1.21-1.3.0.jar';prefix='com/cerbon/cerbons_api/'
    b=dict(path=str(dep),sha256=sha256(dep),classes={prefix+'api/static_utilities/RandomUtils.class':['randVec'],prefix+'api/static_utilities/MathUtils.class':['consecutiveSum','facingSameDirection','lineCallback','circleCallback'],prefix+'api/static_utilities/MobUtils.class':['preventDespawnExceptPeaceful']})
    r=dict(id='bomd-lich-244',scope='Exact installed projectile/owner and native explosion, summon load, melee and placement helpers.',archives=[a,b]);write_json(OUT/'reference-specifications/bomd-lich-244.json',r);write_json(OUT/'reference-evidence/bomd-lich-244.json',reference_collect(r,source_aids=True))
    v=dict(classes={'net/minecraft/world/entity/monster/Phantom':['readAdditionalSaveData','finalizeSpawn','setPhantomSize','updatePhantomSizeInfo','getPhantomSize','onSyncedDataUpdated','aiStep'], 'net/minecraft/world/entity/monster/Phantom$PhantomSweepAttackGoal':['tick'],'net/minecraft/world/level/ExplosionDamageCalculator':['getEntityDamageAmount','shouldDamageEntity','getKnockbackMultiplier'],'net/minecraft/world/entity/projectile/ThrowableItemProjectile':['<init>'],'net/minecraft/world/damagesource/DamageSources':['thrown','explosion','mobAttack','genericKill','source']},resources=['data/minecraft/damage_type/'+n+'.json' for n in ['thrown','player_explosion','mob_attack','generic_kill']])
    write_json(OUT/'vanilla-specifications/bomd-lich.json',v);write_json(OUT/'vanilla-evidence/bomd-lich.json',prepare(v))
    write_json(OUT/'bomd-lich-source-tags.json',source_tags())
    print('Lich native witnesses',len(rows))

if __name__=='__main__':save()
