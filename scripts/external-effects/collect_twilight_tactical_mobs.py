"""Native Redcap/Kobold/Boggard/Troll control and native TNT/rock delivery."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-tactical-mobs'
FULL=['entity/monster/'+c for c in ['Redcap','RedcapSapper','Kobold','Kobold$1','Kobold$KoboldAttackPlayerTarget','Kobold$RunAwayWhileHoldingBreadGoal','Kobold$SeekBreadGoal','Boggard','Troll']]+['entity/ai/goal/'+c for c in ['RedcapBaseGoal','RedcapShyGoal','RedcapLightTNTGoal','RedcapPlantTNTGoal','AvoidAnyEntityGoal','AvoidAnyEntityGoal$1','FlockToSameKindGoal','PanicOnFlockDeathGoal','ChargeAttackGoal']]+['entity/projectile/ThrownBlock']

def scan_callers(target):
    needles=['TFDamageTypes.THROWN_BLOCKL','ThrownBlock.<init>','RedcapPlantTNTGoal.<init>','RedcapLightTNTGoal.<init>','PanicOnFlockDeathGoal.<init>','FlockToSameKindGoal.<init>']
    hits=[];boggard_references=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if b'twilightforest/entity/monster/Boggard' in b or b'twilightforest.entity.monster.Boggard' in b:boggard_references.append(dict(entry=entry,class_sha256=byte_hash(b)))
            if not any(n.encode() in b for n in ['THROWN_BLOCK','ThrownBlock','RedcapPlantTNTGoal','RedcapLightTNTGoal','PanicOnFlockDeathGoal','FlockToSameKindGoal']):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(n in str(i['operand']) for n in needles):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All installed TF class instructions; touched custom damage/rock producers and shared tactical AI constructors. Also all TF class bytes for internal/dotted Boggard class references.',needles=needles,hits=hits,boggard_class_references=boggard_references)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    resources=read_json(WORK/'twilightforest/resources.json');ids=['redcap','kobold','boggard','troll','thrown_block','ironwood_boots','ironwood_pickaxe']
    selected=[p for p,v in resources.items() if ('/tags/' in p and (any(n in str(v) for n in ids) or 'kobold_pacification' in p)) or p=='data/twilightforest/damage_type/thrown_block.json']
    classes={c:['*'] for c in FULL};classes['util/WorldUtil']=['getAllAround'];classes['init/TFEntities']=['*']
    # Keep registry evidence scoped to the actual equipment lambdas and material body.
    with zipfile.ZipFile(target['path']) as jar:
        c=ClassFile(jar.read('twilightforest/init/TFItems.class'))
        classes['init/TFItems']=[m['name'] for m in c.methods if m['name']=='<clinit>' or (any('IRONWOOD' in str(i['operand']) for i in c.instructions(m.get('code',b''))) and any(n in str(c.instructions(m.get('code',b''))) for n in ['PickaxeItem','Type.BOOTS']))]
    classes['init/TFArmorMaterials']=['*']
    print('native',native(BATCH,classes,selected))
    fullraw=['net/minecraft/world/level/block/TntBlock','net/minecraft/world/entity/item/PrimedTnt','net/minecraft/world/entity/item/PrimedTnt$1']
    raw={'net/minecraft/world/entity/Mob':['aiStep','pickUpItem','canHoldItem','canTakeItem','equipItemIfPossible','wantsToPickUp','getPickupReach'],
         'net/minecraft/world/entity/LivingEntity':['eat','addEatEffect'],
         'net/minecraft/world/item/Item':['finishUsingItem'],
         'net/minecraft/world/item/ItemStack':['finishUsingItem','consume'],
         'net/minecraft/world/entity/Entity':['rideTick'],
         'net/minecraft/nbt/NbtUtils':['readBlockState'],
         'net/minecraft/world/level/Level':['removeBlock','destroyBlock'],
         'net/minecraft/world/damagesource/DamageSources':['explosion'],
         'net/minecraft/world/entity/ai/goal/Goal':['canContinueToUse','requiresUpdateEveryTick'],
         'net/minecraft/world/food/Foods':['<clinit>']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c in fullraw:raw[c]=[]
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=sorted(available) if c in fullraw else [m for m in ms if m in available]
    loader={c+'.class':list(ms) for c,ms in raw.items()}
    template=read_json(OUT/'reference-specifications/vv-loader-244.json')
    a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c[:-6] in fullraw and c in jar.namelist():loader[c]=sorted({m['name'] for m in ClassFile(jar.read(c)).methods})
    print('references',references(BATCH,raw,loader,{'net/neoforged/neoforge/event/EventHooks.class':['canEntityGrief']}))
    spec=dict(classes={},resources=['data/minecraft/tags/block/base_stone_overworld.json']);write_json(OUT/'vanilla-specifications/twilight-tactical-tags.json',spec);write_json(OUT/'vanilla-evidence/twilight-tactical-tags.json',prepare(spec))
    archive=next(a for a in template['archives'] if a['path'].endswith('universal.jar'))
    with zipfile.ZipFile(archive['path']) as jar:tags=[p for p in jar.namelist() if p in ['data/c/tags/item/foods/bread.json','data/c/tags/item/foods/breads.json']]
    spec=dict(id='twilight-tactical-tags-244',scope='Exact installed loader bread tag expansion.',archives=[dict(path=archive['path'],sha256=archive['sha256'],classes={},resources=tags)])
    write_json(OUT/'reference-specifications/twilight-tactical-tags-244.json',spec);write_json(OUT/'reference-evidence/twilight-tactical-tags-244.json',collect_reference(spec))
    write_json(OUT/'twilightforest-tactical-mobs-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
