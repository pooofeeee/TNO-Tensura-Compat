"""Three ownerless mechanical hazards and their genuine terrain/entity producers."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-mechanical-hazards'
FIELDS=['FIRE_JET','REACTOR','SLIDER']
FULL=['block/'+x for x in ['FireJetBlock','EncasedFireJetBlock','CarminiteReactorBlock','ReactorDebrisBlock','SliderBlock','TFSmokerBlock','EncasedSmokerBlock']]+['block/entity/'+x for x in ['FireJetBlockEntity','CarminiteReactorBlockEntity','ReactorDebrisBlockEntity','TFSmokerBlockEntity']]+['entity/SlideBlock','enums/FireJetVariant','world/components/feature/FireJetFeature']
TOKENS=['TFDamageTypes.'+f for f in FIELDS]+['FireJetBlock','CarminiteReactorBlock','ReactorDebrisBlock','SlideBlock','SliderBlock','FIRE_JET','CARMINITE_REACTOR','REACTOR_DEBRIS','TFBlocks.SLIDER','TFEntities.SLIDER']
def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.rsplit('.',1)[-1].encode() in b for s in TOKENS):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in TOKENS):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='Installed TF instruction callers for three mechanical sources, block/entity producers and debris. Static only.',needles=TOKENS,hits=hits)
def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    words=['fire_jet','reactor','slider','smoker','fake_gold','fake_diamond']
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in words)]
    classes={c:['*'] for c in FULL}
    classes.update({'world/components/structures/darktower/DarkTowerMainComponent':['decorateExperiment'],'entity/monster/CarminiteGhastling':['<init>','registerAttributes','makeBossMinion','shouldAttack'],'events/EntityEvents':['reduceFrostedEffectIfOnFire'],'init/TFDamageTypes':['getDamageSource','getEntityDamageSource','getIndirectEntityDamageSource']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,ns in list(classes.items()):
            if ns==['*']:continue
            av={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods};assert set(ns)<=av,(c,set(ns)-av);classes[c]=sorted(set(ns)|{m for m in av if any(m.startswith('lambda$'+n+'$') for n in ns)})
        for c,needles in [('init/TFBlocks',['FireJet','Reactor','Slider','Smoker','FAKE_GOLD','FAKE_DIAMOND']),('init/TFBlockEntities',['FLAME_JET','REACTOR','SMOKER','DEBRIS']),('init/TFEntities',['SLIDER']),('init/TFFeatures',['FireJetFeature']),('init/TFConfiguredFeatures',['FIRE_JET','SMOKER']),('init/TFPlacedFeatures',['FIRE_JET','SMOKER'])]:
            cl=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=sorted({m['name'] for m in cl.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cl.instructions(m.get('code',b'')))})
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/world/level/Explosion':['<init>','makeDamageCalculator','getSeenPercent','explode','finalizeExplosion'],'net/minecraft/world/level/ExplosionDamageCalculator':['getEntityDamageAmount','shouldDamageEntity','getKnockbackMultiplier','getBlockExplosionResistance','shouldBlockExplode'],'net/minecraft/world/level/Level':['explode','isUnobstructed','getEntities'],'net/minecraft/world/level/EntityGetter':['getEntitiesOfClass','getNearestPlayer','isUnobstructed'],'net/minecraft/world/level/CollisionGetter':['isUnobstructed'],'net/minecraft/world/entity/Entity':['hurt','setRemainingFireTicks','baseTick','isInvulnerableTo','move','spawnAtLocation'],'net/minecraft/world/entity/decoration/ArmorStand':['hurt'],'net/minecraft/world/entity/LivingEntity':['hurt','knockback','getDamageAfterArmorAbsorb','getDamageAfterMagicAbsorb','actuallyHurt','isDamageSourceBlocked'],'net/minecraft/world/damagesource/DamageSource':['getSourcePosition','scalesWithDifficulty'],'net/minecraft/world/entity/item/ItemEntity':['hurt'],'net/minecraft/server/level/ServerLevel':['addFreshEntity','addEntity'],'net/minecraft/world/level/block/state/BlockBehaviour':['onExplosionHit'],'net/minecraft/world/level/block/entity/BlockEntity':['saveAdditional','loadAdditional']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in list(raw.items()):
            cl=ClassFile(jar.read(names.named[c]+'.class'));av={names.member(cl.name,m['name'],m['descriptor']) for m in cl.methods};raw[c]=sorted({m for m in av if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)});assert raw[c],c
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            av={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]
            loader[c]=sorted({m for m in av if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/event/EventHooks.class':['onExplosionStart','onExplosionDetonate','getExplosionKnockback'],'net/neoforged/neoforge/common/CommonHooks.class':['onLivingKnockBack','isEntityInvulnerableTo']}
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    write_json(OUT/'twilightforest-mechanical-hazards-caller-scan.json',scan_callers(target))
if __name__=='__main__':collect()
