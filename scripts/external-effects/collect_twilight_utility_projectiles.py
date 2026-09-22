"""Real Moonworm/Cube deliveries, resources, shield and terrain contracts."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-utility-projectiles'
FULL=['item/MoonwormQueenItem','entity/projectile/MoonwormShot','item/recipe/MoonwormQueenRepairRecipe','item/CubeOfAnnihilationItem','entity/projectile/CubeOfAnnihilation','dispenser/DamageableStackDispenseBehavior','dispenser/TFDispenserBehaviors$1','block/MoonwormBlock','block/CritterBlock','block/entity/MoonwormBlockEntity']
NEEDLES=['TFDamageTypes.MOONWORM','MoonwormShot.<init>','CubeOfAnnihilation.<init>','TFItems.MOONWORM_QUEEN','TFItems.CUBE_OF_ANNIHILATION','TFDispenserBehaviors.init']

def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.encode() in b for s in ['MOONWORM','MoonwormShot','CubeOfAnnihilation','CUBE_OF_ANNIHILATION','TFDispenserBehaviors']):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in NEEDLES):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
        cube_data=[]
        for entry in jar.namelist():
            if entry.startswith('data/') and entry.endswith('.json'):
                b=jar.read(entry)
                if b'cube_of_annihilation' in b:cube_data.append(dict(entry=entry,sha256=byte_hash(b),data=json.loads(b)))
    return dict(jar_sha256=target['sha256'],scope='All installed-TF instruction callers of Moonworm type, real Moonworm/Cube constructors/item fields and dispenser registration; all data JSON literal Cube item mentions.',needles=NEEDLES,hits=hits,cube_data_mentions=cube_data)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in res.items() if any(x in p for x in ['moonworm','annihilation_inclusions','tags/block/deadrock','dont_kill_bugs']) or '/tags/' in p and any(x in str(v) for x in ['moonworm','cube_of_annihilation'])]
    classes={c:['*'] for c in FULL};classes.update({'dispenser/TFDispenserBehaviors':['init'],'util/WorldUtil':['getAllInBB'],'events/EntityEvents':['onParryProjectile'],'entity/projectile/TFThrowable':['*'],'util/TFItemStackUtils':['hurtButDontBreak'],'init/TFDamageTypes':['getIndirectEntityDamageSource']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,needle in [('init/TFItems','MoonwormQueenItem'),('init/TFItems','CubeOfAnnihilationItem'),('init/TFBlocks','MoonwormBlock'),('init/TFDataComponents','UUIDUtil'),('init/TFRecipes','MoonwormQueenRepairRecipe'),('events/RegistrationEvents','TFDispenserBehaviors.init')]:
            cls=ClassFile(jar.read('twilightforest/'+c+'.class'));names=[m['name'] for m in cls.methods if m['name']=='<clinit>' or any(needle in str(i['operand']) for i in cls.instructions(m.get('code',b'')))];classes[c]=sorted(set(classes.get(c,[])+names))
        c=ClassFile(jar.read('twilightforest/init/TFBlocks.class'))
        extra=[m['name'] for m in c.methods if m['name']=='register' or m['name'].startswith('lambda$register$') or (m['descriptor'].endswith('BlockState;)I') and any(i['operand']==14 for i in c.instructions(m.get('code',b''))))]
        classes['init/TFBlocks']=sorted(set(classes['init/TFBlocks']+extra))
    print('native',native(BATCH,classes,selected))
    raw={'net/minecraft/world/entity/projectile/ThrowableProjectile':['<init>','tick','getDefaultGravity'], 'net/minecraft/world/entity/projectile/Projectile':['tick','canHitEntity','onHit','hitTargetOrDeflectSelf','deflect','getOwner','setOwner','addAdditionalSaveData','readAdditionalSaveData'], 'net/minecraft/world/entity/LivingEntity':['isBlocking','canDisableShield','isDamageSourceBlocked','blockUsingShield','blockedByShield'], 'net/minecraft/world/entity/player/Player':['blockUsingShield','disableShield','hurtCurrentlyUsedShield','attack'], 'net/minecraft/world/entity/Entity':['spawnAtLocation','hurt','isPickable'], 'net/minecraft/world/item/ItemStack':['canBreakBlockInAdventureMode'], 'net/minecraft/world/damagesource/DamageSources':['playerAttack','mobAttack','thrown'], 'net/minecraft/world/level/Level':['removeBlock'], 'net/minecraft/world/item/ArmorItem':['dispenseArmor']}
    raw['net/minecraft/world/entity/Entity'].append('canBeHitByProjectile')
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods};raw[c]=sorted({m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            available={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]];loader[c]=sorted({m for m in available if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/common/extensions/IItemExtension.class':['canPerformAction','canDisableShield'],'net/neoforged/neoforge/common/extensions/IItemStackExtension.class':['canPerformAction','canDisableShield']}
    print('references',references(BATCH,raw,loader,hooks));write_json(OUT/'twilightforest-utility-projectiles-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
