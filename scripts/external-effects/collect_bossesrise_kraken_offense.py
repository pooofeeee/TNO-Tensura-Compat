from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_bossesrise_foundation import targets,KEY,PKG
from collect_bossesrise_kraken_defense import TENTACLE
CLASSES={s:None for s in [TENTACLE,TENTACLE+'$AttackTarget','entity/boss/kraken/goals/KrakenTentacleAttackGoal','entity/boss/kraken/goals/KrakenTentacleCrateGoal','entity/boss/kraken/goals/KrakenTentacleRunawayGoal','entity/decoration/CannonEntity','entity/decoration/CannonEntity$Listener','entity/projectile/CannonballEntity','entity/projectile/ThrownCrateEntity','entity/boss/kraken/summons/PirateRookEntity','entity/boss/kraken/summons/PirateRookEntity$1','entity/boss/kraken/summons/PirateCaptainEntity','entity/boss/kraken/summons/PirateCaptainEntity$1','entity/boss/kraken/summons/CrossbowPirateEntity']}

def census():
    t=targets()[KEY];rows=[];ends=['/CannonballEntity','/ThrownCrateEntity','/GhostTentacleEntity']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if (i['opcode']=='0xbb' and any(str(i.get('operand','')).endswith(s) for s in ends)) or (i['opcode'] in ['0xb6','0xb7','0xb8','0xb9'] and any(s in str(i.get('operand','')) for s in ['.attackEntitiesCollidingPlane(','.attackEntitiesCollidingBox(','.spawnPirates(']))]
                if hits:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Whole-JAR actual cannon/crate/tentacle-smash producers; Ghost Tentacle provenance checked to avoid attributing equipment summons to Kraken.',rows=rows)

def profiles():
    source=read_json(OUT/'bossesrise-damage-tags.json');table={}
    for r in source['resources']:
        n=r['entry'];tag=n.split('/')[1]+':'+n.split('/tags/damage_type/')[1][:-5];d=r['data']
        if d.get('replace'):table[tag]=[]
        table.setdefault(tag,[]).extend(d.get('values',[]))
    def members(tag,seen=()):
        if tag in seen:return set()
        out=set()
        for v in table.get(tag,[]):
            v=v['id'] if isinstance(v,dict) else v
            out|=members(v[1:],seen+(tag,)) if v.startswith('#') else {v}
        return out
    return dict(scope=source['scope'],reference_file='bossesrise-damage-tags.json',reference_sha256=sha256(OUT/'bossesrise-damage-tags.json'),profiles=[dict(id=s,tags=sorted(t for t in table if s in members(t))) for s in ['block_factorys_bosses:cannonball_hit','block_factorys_bosses:kraken_tentacle_smash','minecraft:mob_attack','minecraft:arrow','minecraft:magic','minecraft:explosion','minecraft:player_explosion']])

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});rows.append(dict(id='br:kraken_offense:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Kraken real attack goals, collision sources, cannon rider delivery and pirate payloads; cosmetics excluded semantically.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-kraken-offense.json',s);write_json(OUT/'native-evidence/bossesrise-kraken-offense.json',collect(s));write_json(OUT/'bossesrise-kraken-offense-census.json',census());write_json(OUT/'bossesrise-kraken-source-profiles.json',profiles())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={};raw={}
    wanted={'net/minecraft/world/entity/ai/goal/RangedCrossbowAttackGoal':['canUse','tick'],'net/minecraft/world/item/ProjectileWeaponItem':['shoot','createProjectile'],'net/minecraft/world/entity/ai/goal/Goal':['requiresUpdateEveryTick','adjustedTickDelay','reducedTickDelay'],'net/minecraft/world/entity/ai/goal/GoalSelector':['tick','tickRunningGoals'],'net/minecraft/world/entity/Mob':['serverAiStep'],'net/minecraft/world/entity/monster/Monster':['getProjectile'],'net/minecraft/world/entity/monster/CrossbowAttackMob':['performCrossbowAttack'],'net/minecraft/world/item/CrossbowItem':['performShooting','shootProjectile','createProjectile'],'net/minecraft/world/level/Explosion':['getIndirectSourceEntityInternal','explode'],'net/minecraft/world/damagesource/DamageSources':['explosion']}
    with zipfile.ZipFile(a['path']) as z:
        for k,v in wanted.items():
            if k+'.class' in z.namelist():a['classes'][k+'.class']=v
            else:raw[k]=v
    r=dict(id='bossesrise-kraken-offense-244',scope='Exact adjusted goal timing, native crossbow source and Living-owned explosion identity; protected projectile and explosion references reused.',archives=[a]);write_json(OUT/'reference-specifications/bossesrise-kraken-offense-244.json',r);write_json(OUT/'reference-evidence/bossesrise-kraken-offense-244.json',reference_collect(r,source_aids=True))
    s=dict(classes=raw,resources=['data/minecraft/damage_type/player_explosion.json']);write_json(OUT/'vanilla-specifications/bossesrise-kraken-offense.json',s);write_json(OUT/'vanilla-evidence/bossesrise-kraken-offense.json',prepare(s));write_json(OUT/'reference-routing/bossesrise-kraken-offense.json',dict(archive=a['path'],sha256=a['sha256'],absent_entries=[k+'.class' for k in raw]));print('Kraken offense pinned')
if __name__=='__main__':save()
