"""Incremental mounted knights and hostile mounts; no runtime execution."""
from twilight_evidence import *
from vanilla_reference import MojangNames, CLIENT

BATCH='twilight-mounted-mobs'
FULL=['entity/monster/'+c for c in ['UpperGoblinKnight','UpperGoblinKnight$1','LowerGoblinKnight','LowerGoblinKnight$1','PinchBeetle','Yeti','Yeti$1']]+['entity/ai/goal/'+c for c in ['HeavySpearAttackGoal','RiderSpearAttackGoal']]

def scan_callers(target):
    hits=[]
    needles=['TFDamageTypes.CLAMPEDLnet/minecraft/resources/ResourceKey;','Yeti.setAngry(Z)V','UpperGoblinKnight.landHeavySpearAttack()V']
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(n.encode() in b for n in ['CLAMPED','setAngry','landHeavySpearAttack']):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(n in str(i['operand']) for n in needles):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All installed TF classes; CLAMPED and the two selected method callers only.',needles=needles,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    ids=['pinch_beetle','upper_goblin_knight','lower_goblin_knight','yeti']
    selected=[p for p,v in read_json(WORK/'twilightforest/resources.json').items() if '/tags/entity_type/' in p and (any(x in str(v) for x in ids) or p.endswith('/rides_obstruct_snatching.json'))]
    print('native',native(BATCH,{c:['*'] for c in FULL},selected))
    raw={'net/minecraft/world/entity/vehicle/Boat':['tick','canAddPassenger','getMaxPassengers','hasEnoughSpaceFor','push','getBoundingBox','getVariant'],
         'net/minecraft/world/entity/Entity':['kill','startRiding','stopRiding','removeVehicle','canRide','canAddPassenger'],
         'net/minecraft/world/entity/ai/attributes/AttributeInstance':['calculateValue','getValue','addTransientModifier'],
         'net/minecraft/world/entity/ai/goal/Goal':['canContinueToUse','requiresUpdateEveryTick'],
         'net/minecraft/world/entity/ai/goal/GoalSelector':['tick','tickRunningGoals'],
         'net/minecraft/world/entity/Mob':['serverAiStep','aiStep','doHurtTarget'],
         'net/minecraft/world/entity/LivingEntity':['aiStep','knockback'],
         'net/minecraft/world/damagesource/DamageSource':['isCreativePlayer']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=[m for m in ms if m in available]
    print('references',references(BATCH,raw,{c+'.class':ms for c,ms in raw.items()}))
    write_json(OUT/'twilightforest-mounted-mobs-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
