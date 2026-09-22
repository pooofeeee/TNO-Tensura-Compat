"""Native portal creation, actual lightning, transport and configured spawn entry."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
import tomllib
BATCH='twilight-portals'
FULL=['block/TFPortalBlock','world/TFTeleporter','world/TFTeleporter$PortalPosition','world/TeleporterCache','world/NoReturnTeleporter','components/entity/TFPortalAttachment','util/iterators/DiagonalSpiralIterator','util/iterators/XZQuadrantIterator']
TOKENS=['TFPortalBlock','TFTeleporter','NoReturnTeleporter','TF_PORTAL_COOLDOWN','BANISHED_TO_TWILIGHT_FOREST','TFBlocks.TWILIGHT_PORTAL','playersNotified']
CONFIG=Path(r'C:\Users\youra\curseforge\minecraft\Instances\new\config\twilightforest-common.toml')
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
    return dict(jar_sha256=target['sha256'],scope='Existing native portal owner/source census: real pool catalyst, lightning, processor/transport, attachments and configured spawn. Static only.',needles=TOKENS,hits=hits)
def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in ['portal','twilight_forest.json'])]
    classes={c:['*'] for c in FULL}
    classes.update({'events/ProgressionEvents':['setup','performProtectionAndPortalChecks','checkForPortalCreation'],'events/CapabilityEvents':['setup','updatePlayerCaps','spawnInTFIfNecessary','playerLogsIn','newSpawnInTwilightForest','dataFixLegacyBanish'],'config/TFConfig':['<clinit>','getPortalLockingAdvancement','rebakeCommonOptions'],'config/TFCommonConfig':['<init>'],'init/TFDimension':['*'],'util/Restriction':['isBiomeSafeFor'],'util/landmarks/LandmarkUtil':['isProgressionEnforced'],'advancements/SimpleAdvancementTrigger':['trigger'],'advancements/SimpleAdvancementTrigger$TriggerInstance':['makeTFPortal'],'util/PlayerHelper':['getAdvancement','doesPlayerHaveRequiredAdvancement']})
    with zipfile.ZipFile(target['path']) as jar:
        for c,ns in list(classes.items()):
            if ns==['*']:continue
            av={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods};assert set(ns)<=av,(c,set(ns)-av);classes[c]=sorted(set(ns)|{m for m in av if any(m.startswith('lambda$'+n+'$') for n in ns)})
        for c,needles in [('init/TFBlocks',['TFPortalBlock']),('init/TFDataAttachments',['TFPortalAttachment','BANISHED_TO_TWILIGHT_FOREST','twilightforest_banished']),('init/TFGameRules',['TF_PORTAL','playersTfPortal']),('init/TFAdvancements',['MADE_TF_PORTAL'])]:
            cl=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=sorted({m['name'] for m in cl.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cl.instructions(m.get('code',b'')))})
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/world/entity/PortalProcessor':['*'],'net/minecraft/world/level/block/Portal':['*'],'net/minecraft/world/entity/Entity':['canUsePortal','handlePortal','setAsInsidePortal','setPortalCooldown','getDimensionChangingDelay','canChangeDimensions','changeDimension','restoreFrom','thunderHit','saveWithoutId','load'],'net/minecraft/world/entity/LivingEntity':['canUsePortal'],'net/minecraft/world/entity/player/Player':['drop','canUsePortal','getDimensionChangingDelay'],'net/minecraft/server/level/ServerPlayer':['changeDimension','setRespawnPosition','canUsePortal'],'net/minecraft/world/entity/item/ItemEntity':['getOwner','setThrower','addAdditionalSaveData','readAdditionalSaveData'],'net/minecraft/world/entity/LightningBolt':['<init>','tick','spawnFire','setVisualOnly','getDamage'],'net/minecraft/world/damagesource/DamageSources':['lightningBolt','<init>'],'net/minecraft/world/level/portal/DimensionTransition':['*'],'net/minecraft/world/level/dimension/DimensionType':['getTeleportationScale'],'net/minecraft/world/level/block/state/BlockBehaviour$BlockStateBase':['getCollisionShape'],'net/minecraft/world/level/block/state/BlockBehaviour$BlockStateBase$Cache':['<init>']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in list(raw.items()):
            cl=ClassFile(jar.read(names.named[c]+'.class'));av={names.member(cl.name,m['name'],m['descriptor']) for m in cl.methods};raw[c]=sorted(av if ms==['*'] else {m for m in av if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)});assert raw[c],c
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            av={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]+(['getDamage'] if c.endswith('/LightningBolt.class') else [])
            loader[c]=sorted({m for m in av if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/event/EventHooks.class':['onEntityStruckByLightning'],'net/neoforged/neoforge/common/CommonHooks.class':['onTravelToDimension','onPlayerTossEvent']}
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    vsp=read_json(OUT/('vanilla-specifications/'+BATCH+'.json'));vsp['resources']=['data/minecraft/damage_type/lightning_bolt.json'];write_json(OUT/('vanilla-specifications/'+BATCH+'.json'),vsp)
    from vanilla_reference import prepare
    write_json(OUT/('vanilla-evidence/'+BATCH+'.json'),prepare(vsp))
    rsp=read_json(OUT/('reference-specifications/'+BATCH+'-244.json'));univ=next(x for x in template['archives'] if x['path'].endswith('universal.jar'))
    archive=next((x for x in rsp['archives'] if x['path']==univ['path']),None)
    if archive is None:
        archive=dict(path=univ['path'],sha256=univ['sha256'],classes={},resources=[]);rsp['archives'].append(archive)
    archive['resources']=['data/neoforge/tags/damage_type/'+n+'.json' for n in ['is_environment','is_magic','is_physical']]+['data/c/tags/item/gems/diamond.json']
    write_json(OUT/('reference-specifications/'+BATCH+'-244.json'),rsp)
    from selected_reference import collect as reference_collect
    write_json(OUT/('reference-evidence/'+BATCH+'-244.json'),reference_collect(rsp,True))
    write_json(OUT/'twilightforest-portals-caller-scan.json',scan_callers(target))
    write_json(OUT/'twilightforest-portals-config-snapshot.json',dict(path=str(CONFIG),sha256=sha256(CONFIG),data=tomllib.loads(CONFIG.read_text(encoding='utf-8')),scope='Static installed common config snapshot; not live world gamerules or proof of executed callbacks.'))
if __name__=='__main__':collect()
