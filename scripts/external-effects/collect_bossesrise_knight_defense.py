from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_bossesrise_foundation import targets,KEY,PKG
import gzip
import struct

KNIGHT='entity/boss/knight/UnderworldKnightEntity'
CLASSES={KNIGHT:['<init>','<clinit>','defineSynchedData','getImmuneStacks','setImmuneStacks','removeOneImmuneStack','isInvulnerable','isCinematic','canBeSeenAsEnemy','hurt','processHurt','canFreeze','shouldCancelDeath','tick','setState','doAttack','placeMark','positionRider','cleanNearbyPests','isPushable','fireImmune','addAdditionalSaveData','readAdditionalSaveData','onAddedToLevel','finalizeSpawn','createAttributes','baseTick','getAnimTransitionTime'], 'entity/boss/knight/KnightMarkEntity':None,'init/BossesRiseEntities':['<clinit>'],'configuration/ServerConfiguration':['<clinit>'],'procedures/UnderworldKnightOnEntityTickUpdateProcedure':['execute','attackCombo1']}

def census():
    t=targets()[KEY];rows=[]
    needles=['.placeMark(','.processHurt(','.removeOneImmuneStack(','.setImmuneStacks(','.DATA_IMMUNE_STACKS','.DATA_CINEMATIC','.DATA_SPAWN_ANIMTIME','.DATA_UNDEAD_CINEMATIC','UnderworldKnightOnEntityTickUpdateProcedure.execute(']
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(x for x in z.namelist() if x.endswith('.class')):
            raw=z.read(n);c=ClassFile(raw)
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if i['opcode'] in ['0xb2','0xb5','0xb6','0xb7','0xb8','0xb9'] and str(i.get('operand','')).startswith(PKG) and any(s in str(i.get('operand','')) for s in needles)]
                if hits:rows.append(dict(entry=n,entry_sha256=byte_hash(raw),method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(jar_sha256=t['sha256'],scope='Actual stack, mark, cinematic and processHurt references; cosmetic DATA_CINEMATIC_BLACK_SCREEN names also indexed, not new defense claims.',rows=rows)

def arena_entity():
    # Read only native structure entity combat initialization, not blocks/worldgen semantics.
    t=targets()[KEY];entry='data/block_factorys_bosses/structure/underworld_arena_1.nbt'
    with zipfile.ZipFile(t['path']) as z:raw=z.read(entry)
    data=gzip.decompress(raw);offset=0
    def take(n):
        nonlocal offset
        assert n>=0 and offset+n<=len(data)
        v=data[offset:offset+n];offset+=n;return v
    def number(fmt):return struct.unpack('>'+fmt,take(struct.calcsize('>'+fmt)))[0]
    def string():return take(number('H')).decode('utf-8')
    def payload(tag):
        if tag in [1,2,3,4,5,6]:return number({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[tag])
        if tag==7:return list(take(number('i')))
        if tag==8:return string()
        if tag==9:
            kind=number('B');count=number('i');assert count>=0
            return [payload(kind) for _ in range(count)]
        if tag==10:
            result={}
            while True:
                kind=number('B')
                if kind==0:return result
                name=string();assert name not in result;result[name]=payload(kind)
        if tag in [11,12]:
            count=number('i');assert count>=0
            return [number('i' if tag==11 else 'q') for _ in range(count)]
        raise ValueError(tag)
    assert number('B')==10;root_name=string();root=payload(10);assert offset==len(data)
    keys=['id','Health','BossPhase','SpawnAnimtime','UndeadCinematic','ImmuneStacks','ImmuneStackMax','State','Timer','HpGate75','HpGate50','HpGate25','Transformed','IsStuck','LightCounter','HeavyCounter','Attributes','CinematicBlack']
    entities=[{k:x['nbt'][k] for k in keys if k in x['nbt']} for x in root['entities'] if x['nbt'].get('id')==KEY+':underworld_knight']
    return dict(jar_sha256=t['sha256'],entry=entry,entry_sha256=byte_hash(raw),decompressed_sha256=byte_hash(data),root_name=root_name,entities=entities,scope='Only native Knight entity combat initialization extracted; no structure acquisition/worldgen review.')

def save():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for short,wanted in CLASSES.items():
            n=PKG+short+'.class';c=ClassFile(z.read(n));names=wanted or sorted({m['name'] for m in c.methods});names=sorted(set(names)|{m['name'] for m in c.methods if any(m['name'].startswith('lambda$'+v+'$') for v in names)})
            rows.append(dict(id='br:knight_defense:'+short,mod_key=KEY,entry=n,methods=names))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Knight defense/phase/mark semantics only. Shared tick witness includes offensive branches which remain pending R2i3b.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/bossesrise-knight-defense.json',s);write_json(OUT/'native-evidence/bossesrise-knight-defense.json',collect(s));write_json(OUT/'bossesrise-knight-defense-census.json',census())
    write_json(OUT/'bossesrise-knight-arena-initialization.json',arena_entity())
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/entity/Entity.class':['isInvulnerable','isInvulnerableTo','startRiding'],'net/minecraft/world/entity/LivingEntity.class':['hurt']}
    r=dict(id='bossesrise-knight-defense-244',scope='Entity backing invulnerable field versus Knight override, native damage/mount admission; no fabricated route.',archives=[a]);write_json(OUT/'reference-specifications/bossesrise-knight-defense-244.json',r);write_json(OUT/'reference-evidence/bossesrise-knight-defense-244.json',reference_collect(r,source_aids=True))
    print('Knight defense pinned; offensive tick branches remain next')

if __name__=='__main__':save()
