"""Native death/respawn/retention contracts; Curios is an exact API dependency only."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
from selected_reference import collect as reference_collect
BATCH='twilight-charms'
FULL=['events/CharmEvents','item/KeepsakeCasketItem','block/KeepsakeCasketBlock','block/SkullChestBlock','block/entity/SkullChestBlockEntity','block/entity/KeepsakeCasketBlockEntity','entity/CharmEffect','network/SpawnCharmPacket','network/SpawnCharmPacket$1']
TOKENS=['CharmEvents.','CHARM_OF_LIFE_','CHARM_OF_KEEPING_','KEPT_ON_DEATH','TFCharmInventory','CharmStack','CasketDamage','KEEPSAKE_CASKET','findAndConsumeCurio','keepCurios']
CURIO=Path(r'C:\Users\youra\curseforge\minecraft\Instances\new\mods\curios-neoforge-9.5.1+1.21.1.jar')

def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.replace('CharmEvents.','CharmEvents').encode() in b for s in TOKENS):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in TOKENS):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='All installed Twilight callers of life/keeping/casket and persisted retention tokens, actual Curios bridge only.',needles=TOKENS,hits=hits,dependency=dict(path=str(CURIO),sha256=sha256(CURIO),role='Selected exact Curios9.5.1 API/retention dependency; no Curios family review or runtime matrix.'))

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    selected=[p for p,v in res.items() if p.startswith('data/') and any(x in p+' '+str(v) for x in ['charm_of_life','charm_of_keeping','keepsake_casket','skull_chest','kept_on_death','phantom_helmet','phantom_chestplate'])]
    classes={c:['*'] for c in FULL};classes.update({'util/TFItemStackUtils':['consumeInventoryItem','sortArmorForCasket','sortInvForCasket','loadNoClear'],'events/EntityEvents':['setup','onCasketBreak'],'TwilightForestMod':['commonSetup','loadCuriosCompat'],'config/TFConfig':['loadCommonConfig']})
    with zipfile.ZipFile(target['path']) as jar:
        for c in ['TwilightForestMod','config/TFConfig']:
            cls=ClassFile(jar.read('twilightforest/'+c+'.class'))
            needles=['loadCuriosCompat','casketUUIDLocking']
            classes[c]=[m['name'] for m in cls.methods if any(any(n in str(i['operand']) for n in needles) for i in cls.instructions(m.get('code',b'')))]
            if c=='TwilightForestMod':classes[c].append('loadCuriosCompat')
        for c,needles in [('init/TFItems',TOKENS+['KeepsakeCasketItem']),('init/TFBlocks',['KeepsakeCasketBlock','SkullChestBlock']),('init/TFBlockEntities',['KeepsakeCasketBlockEntity','SkullChestBlockEntity']),('init/TFDataComponents',['casket_damage']),('events/RegistrationEvents',['SpawnCharmPacket']),('compat/curios/CuriosCompat',['CharmStack','TFCharmInventory','findAndConsumeCurio','keepCurios','registerCuriosCapabilities']),('enums/BlockLoggingEnum',['getFromFluid'])]:
            cls=ClassFile(jar.read('twilightforest/'+c+'.class'));classes[c]=[m['name'] for m in cls.methods if m['name']=='<clinit>' or any(any(n in str(i['operand']) for n in needles) for i in cls.instructions(m.get('code',b''))) or m['name'] in ['registerCuriosCapabilities','findAndConsumeCurio','keepCurios','getFromFluid','getBlock','getFluid'] or (c=='compat/curios/CuriosCompat' and m['name'].startswith(('lambda$keepCurios','lambda$findAndConsumeCurio','lambda$registerCuriosCapabilities')))]
    print('native',native(BATCH,classes,selected),flush=True)
    raw={'net/minecraft/core/NonNullList':['of','clear','withSize'],'net/minecraft/world/entity/player/Inventory':['save','load','add','addResource','getFreeSlot','getSlotWithRemainingSpace','hasAnyMatching','isEmpty','dropAll'],'net/minecraft/world/entity/LivingEntity':['hurt','die','checkTotemDeathProtection','setHealth','addEffect'],'net/minecraft/server/level/ServerPlayer':['die','restoreFrom'],'net/minecraft/world/entity/player/Player':['dropEquipment'],'net/minecraft/world/item/ItemStack':['save','saveOptional','shrink','consume'],'net/minecraft/world/level/block/entity/BaseContainerBlockEntity':['canOpen','createMenu','stillValid'],'net/minecraft/world/effect/RegenerationMobEffect':['applyEffectTick','shouldApplyEffectTickThisTick'],'net/minecraft/world/Container':['stillValidBlockEntity','hasAnyMatching']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods};raw[c]=sorted({m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            available={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]
            loader[c]=sorted({m for m in available if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/common/CommonHooks.class':['onLivingDeath','onLivingUseTotem'],'net/neoforged/neoforge/event/EventHooks.class':['onPlayerClone','firePlayerRespawnEvent'],'net/neoforged/neoforge/event/entity/player/PlayerEvent$PlayerRespawnEvent.class':['<init>','isEndConquered']}
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    root='top/theillusivec4/curios/'
    classes={root+'api/CuriosApi.class':['getCuriosInventory'],root+'mixin/core/MixinCuriosApi.class':['curios$getCuriosInventory'],root+'mixin/CuriosImplMixinHooks.class':['getCuriosInventory'],root+'api/event/DropRulesEvent.class':['*'],root+'common/capability/CurioInventoryCapability.class':['<init>','getSlots','getCurios','getEquippedCurios','findFirstCurio','readTag','writeTag'],root+'common/event/CuriosEventHandler.class':['playerDrops','handleDrops','playerClone'],root+'common/capability/CurioInventory.class':['serializeNBT','deserializeNBT']}
    with zipfile.ZipFile(CURIO) as jar:
        for c,wanted in classes.items():
            if wanted==['*']:continue
            allnames={m['name'] for m in ClassFile(jar.read(c)).methods};classes[c]=sorted(m for m in allnames if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted))
        resources=[n for n in jar.namelist() if n.endswith('.mixins.json') or n=='META-INF/neoforge.mods.toml']
    spec=dict(id=BATCH+'-curios',scope='Selected installed Curios9.5.1 dependency methods for actual Twilight charm consumption/drop/clone calls. Other API effects/mod mechanics excluded; no runtime matrix.',archives=[dict(path=str(CURIO),sha256=sha256(CURIO),classes=classes,resources=resources)])
    write_json(OUT/'reference-specifications'/f'{BATCH}-curios.json',spec);write_json(OUT/'reference-evidence'/f'{BATCH}-curios.json',reference_collect(spec,source_aids=True))
    write_json(OUT/'twilightforest-charms-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
