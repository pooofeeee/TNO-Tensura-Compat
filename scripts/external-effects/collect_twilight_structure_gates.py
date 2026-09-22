"""Structure protection, genuine hint production and static barrier mechanics."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
BATCH='twilight-structure-gates'
FULL=['block/StrongholdShieldBlock','block/TrophyPedestalBlock','block/ForceFieldBlock','world/components/structures/util/ProgressionStructure','world/components/structures/util/AdvancementLockedStructure','world/components/structures/util/AdvancementLockedStructure$AdvancementLockConfig','world/components/structures/util/ProgressionPiece','world/components/structures/util/StructureHints','world/components/structures/util/StructureHints$HintConfig','world/components/structures/type/ProgressionWrappedStructure']
TOKENS=['isComponentProtected','isAreaProtected','trySpawnHintMonster','didSpawnHintMonster','TFBlocks.STRONGHOLD_SHIELD','TFBlocks.TROPHY_PEDESTAL','ForceFieldBlock','_FORCE_FIELD','getForceFieldColor']
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
    return dict(jar_sha256=target['sha256'],scope='Existing installed structure/barrier source census: protection dispatch, hint spawning, actual shield/pedestal/force-field producers. No broad discovery restart.',needles=TOKENS,hits=hits)
def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json');scan=scan_callers(target)
    words=['stronghold_shield','trophy_pedestal','force_field','progression_allow_breaking','structure_banned_interactions','hint_creature','advancements_required','/tags/worldgen/structure/landmark.json','progress_lich.json']
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in words)]
    classes={c:['*'] for c in FULL}
    classes.update({'advancements/SimpleAdvancementTrigger':['trigger'],'advancements/SimpleAdvancementTrigger$TriggerInstance':['activatedPedestal','<clinit>'],'block/AbstractTrophyBlock':['getComparatorValue'],'init/TFAdvancements':['<clinit>']})
    classes.update({'events/ProgressionEvents':['setup','preventLockedAreaBlockBreaking','preventLockedAreaBlockPlacing','preventLockedAreaBlockInteracting','preventLockedAreaMultiblocks','isAreaProtected','preventLockedAreaEntityDamage','performProtectionAndPortalChecks','checkForLockedStructuresSendPacket','isPieceProtected','isBlockProtectedFromInteraction','isBlockProtectedFromBreaking','sendAreaProtectionPacket','sendStructureProtectionPacket','sendAllClearPacket'],'util/PlayerHelper':['playerHasRequiredAdvancements','doesPlayerHaveRequiredAdvancements'],'util/landmarks/LandmarkUtil':['locateNearestLandmarkStart','locateNearestMatchingLandmark','isProgressionEnforced'],'util/entities/EntityUtil':['rayTrace'],'util/Enforcement':['enforceBiomeProgression'],'init/TFEntities':['makeBuilder','make','build'],'init/TFBlocks':['<clinit>']})
    providers={}
    for x in scan['hits']:
        if x['entry'].startswith('twilightforest/world/') and x['entry'][15:-6] not in FULL:
            c=x['entry'][15:-6];providers.setdefault(c,set()).add(x['method'])
    for c,ms in providers.items():classes[c]=sorted(set(classes.get(c,[]))|ms)
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/world/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if b'isComponentProtected' not in b:continue
            if any(m['name']=='isComponentProtected' for m in ClassFile(b).methods):
                c=entry[15:-6]
                if c not in FULL:classes[c]=sorted(set(classes.get(c,[]))|{'isComponentProtected'})
    with zipfile.ZipFile(target['path']) as jar:
        for c,ns in list(classes.items()):
            if ns==['*']:continue
            av={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods};assert set(ns)<=av,(c,set(ns)-av);classes[c]=sorted(set(ns)|{m for m in av if any(m.startswith('lambda$'+n+'$') for n in ns)})
        c='init/TFBlocks';cl=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=sorted({m['name'] for m in cl.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in ['StrongholdShieldBlock','TrophyPedestalBlock','ForceFieldBlock']) for i in cl.instructions(m.get('code',b'')))})
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/world/entity/EntityType':['getBaseClass','create'],'net/minecraft/world/entity/player/Player':['getDestroySpeed'],'net/minecraft/world/level/block/state/BlockBehaviour':['getDestroyProgress','getCollisionShape'],'net/minecraft/server/level/ServerPlayerGameMode':['destroyBlock','useItemOn'],'net/minecraft/world/entity/LivingEntity':['hurt'],'net/minecraft/world/level/EntityGetter':['getEntitiesOfClass'],'net/minecraft/world/level/Level':['setBlock','destroyBlock'],'net/minecraft/server/level/ServerLevel':['addFreshEntity','addEntity'],'net/minecraft/world/entity/Mob':['checkSpawnObstruction','setDropChance'],'net/minecraft/advancements/critereon/SimpleCriterionTrigger':['trigger']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in list(raw.items()):
            cl=ClassFile(jar.read(names.named[c]+'.class'));av={names.member(cl.name,m['name'],m['descriptor']) for m in cl.methods};raw[c]=sorted({m for m in av if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)});assert raw[c],c
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            av={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]+(['getBaseClass'] if c.endswith('/EntityType.class') else [])+(['getDigSpeed'] if c.endswith('/Player.class') else [])
            loader[c]=sorted({m for m in av if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/common/CommonHooks.class':['onRightClickBlock','fireBlockBreak','onPlaceItemIntoWorld','onEntityIncomingDamage'],'net/neoforged/neoforge/event/EventHooks.class':['onBlockPlace','onMultiBlockPlace'],'net/neoforged/neoforge/common/extensions/IBlockExtension.class':['canEntityDestroy']}
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    write_json(OUT/'twilightforest-structure-gates-caller-scan.json',scan)
    write_json(OUT/'twilightforest-structure-gates-source-providers.json',dict(jar_sha256=target['sha256'],scope='Exact runtime structure methods selected from existing family caller scan; geometry layout itself is not a new combat effect.',classes={c:sorted(ms) for c,ms in providers.items()}))
if __name__=='__main__':collect()
