"""Exact native Builder/Antibuilder, cloud controls and associated installed transformers."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
from selected_reference import collect as reference_collect
from collect_twilight_portals import CONFIG
import tomllib
BATCH='twilight-control-blocks'
FULL=['block/'+x for x in ['BuilderBlock','TranslucentBuiltBlock','AntibuilderBlock','CloudBlock','WispyCloudBlock']]+['block/entity/CarminiteBuilderBlockEntity','block/entity/AntibuilderBlockEntity','enums/TowerDeviceVariant','client/event/CloudEvents','client/event/CloudEvents$PrecipitationRenderHelper','world/components/structures/trollcave/CloudComponent','world/components/structures/trollcave/CloudTreeComponent']
TOKENS=['BuilderBlock','CarminiteBuilderBlockEntity','TranslucentBuiltBlock','AntibuilderBlock','CloudBlock','BUILT_BLOCK','ANTIBUILT_BLOCK','ANTIBUILDER','CARMINITE_BUILDER','WISPY_CLOUD','FLUFFY_CLOUD','RAINY_CLOUD','SNOWY_CLOUD','isRainingAt','keepSnowyStateForSnowloggableBlocks','modifySoilDecisionForMushroomBlockSurvivability']
ASM=['twilightforest/asm/transformers/'+x+'.class' for x in ['cloud/IsRainingAtTransformer','snow/KeepGrassSnowyForSnowloggableBlocksTransformer','shroom/ModifySoilDecisionForMushroomBlockSurvivabilityTransformer']]

def scan_callers(target):
    hits=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            if not entry.startswith('twilightforest/') or not entry.endswith('.class'):continue
            b=jar.read(entry)
            if not any(s.encode() in b for s in TOKENS):continue
            c=ClassFile(b)
            for m in c.methods:
                for i in c.instructions(m.get('code',b'')):
                    if any(s in str(i['operand']) for s in TOKENS):hits.append(dict(entry=entry,class_sha256=byte_hash(b),method=m['name'],descriptor=m['descriptor'],instruction=i))
    return dict(jar_sha256=target['sha256'],scope='Installed native control-block source/producer callers; paired exact nested cloud/snow/mushroom transformers, not whole ASM closure.',needles=TOKENS,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest');res=read_json(WORK/'twilightforest/resources.json')
    words=['carminite_builder','antibuilder','built_block','_cloud','cloud_']
    selected=[p for p,v in res.items() if p.startswith('data/') and any(k in p+' '+str(v.get('data','')) for k in words)]
    classes={c:['*'] for c in FULL}
    classes.update({'asmhooks/BlockHooks':['isRainingAt','keepSnowyStateForSnowloggableBlocks','modifySoilDecisionForMushroomBlockSurvivability'],'config/TFConfig':['<clinit>','rebakeCommonOptions'],'config/TFCommonConfig':['<init>'],'events/EntityEvents':['setup','addCloudJumpParticles']})
    scan=scan_callers(target)
    with zipfile.ZipFile(target['path']) as jar:
        # Exact native worldgen producers, registrations and their calling methods remain traceable.
        for hit in scan['hits']:
            c=hit['entry'][len('twilightforest/'):-6]
            if c.startswith('world/components/') or c in ['init/TFBlocks','init/TFBlockEntities','init/TFFeatures','init/TFConfiguredFeatures','init/TFPlacedFeatures']:
                if c not in classes:classes[c]=[]
                if classes[c]!=['*']:classes[c].append(hit['method'])
        for c in ['init/TFBlocks','init/TFBlockEntities']:classes.setdefault(c,[]).append('<clinit>')
        for c,ms in list(classes.items()):
            if ms==['*']:continue
            av={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods};assert set(ms)<=av,(c,set(ms)-av);classes[c]=sorted(set(ms)|{m for m in av if any(m.startswith('lambda$'+n+'$') for n in ms)})
    print('native',native(BATCH,classes,selected),flush=True)
    # Previously protected full service/TFCoreMod registration is reused.
    nested=WORK/'twilightforest/nested-tf-asm.jar'
    with zipfile.ZipFile(target['path']) as jar:assert nested.read_bytes()==jar.read('META-INF/jarjar/s.tf-asm-4.8.3345.jar')
    spec=dict(id=BATCH+'-asm',scope='All methods of exact registered cloud rain, snowy dirt and portal mushroom support transformers.',archives=[dict(path=str(nested),sha256=sha256(nested),classes={c:['*'] for c in ASM},resources=[])])
    write_json(OUT/('reference-specifications/'+BATCH+'-asm.json'),spec);write_json(OUT/('reference-evidence/'+BATCH+'-asm.json'),reference_collect(spec,True))
    raw={'net/minecraft/world/level/EntityGetter':['getNearestPlayer','hasNearbyAlivePlayer'],'net/minecraft/world/entity/EntitySelector':['<clinit>'],'net/minecraft/world/level/block/Block':['updateOrDestroy','handlePrecipitation','fallOn','pushEntitiesUp'],'net/minecraft/world/level/block/state/BlockBehaviour':['getCollisionShape'],'net/minecraft/world/level/Level':['isRainingAt','isRaining','destroyBlock'],'net/minecraft/world/entity/Entity':['causeFallDamage','move','isInRain','isInWaterOrRain','isInWaterRainOrBubble'],'net/minecraft/world/entity/LivingEntity':['causeFallDamage','calculateFallDamage','baseTick','aiStep','isSensitiveToWater','checkAutoSpinAttack','startAutoSpinAttack'],'net/minecraft/world/entity/Mob':['isSunBurnTick'],'net/minecraft/world/entity/monster/Blaze':['isSensitiveToWater'],'net/minecraft/world/entity/monster/EnderMan':['isSensitiveToWater','hurt','teleport'],'net/minecraft/world/entity/monster/Strider':['isSensitiveToWater'],'net/minecraft/world/entity/animal/SnowGolem':['isSensitiveToWater'],'net/minecraft/world/entity/animal/axolotl/Axolotl':['baseTick','handleAirSupply','getMaxAirSupply'],'net/minecraft/world/entity/animal/Dolphin':['tick'],'net/minecraft/world/entity/animal/Wolf':['tick'],'net/minecraft/world/entity/projectile/AbstractArrow':['tick'],'net/minecraft/world/item/TridentItem':['use','releaseUsing','isTooDamagedToUse'],'net/minecraft/world/level/block/entity/ConduitBlockEntity':['serverTick','updateShape','applyEffects','updateDestroyTarget','getDestroyRangeAABB','findDestroyTarget','loadAdditional','saveAdditional'],'net/minecraft/world/entity/projectile/FishingHook':['catchingFish'],'net/minecraft/server/level/ServerLevel':['tickChunk'],'net/minecraft/world/level/block/LeavesBlock':['animateTick'],'net/minecraft/world/level/block/CauldronBlock':['handlePrecipitation','shouldHandlePrecipitation'],'net/minecraft/world/level/block/LayeredCauldronBlock':['handlePrecipitation','entityInside','handleEntityOnFireInside','lowerFillLevel'],'net/minecraft/world/level/block/FarmBlock':['randomTick'],'net/minecraft/world/level/block/FireBlock':['tick','isNearRain','checkBurnOut'],'net/minecraft/world/level/block/SnowyDirtBlock':['isSnowySetting','updateShape','getStateForPlacement'],'net/minecraft/world/level/block/MushroomBlock':['canSurvive'],'net/minecraft/world/damagesource/DamageSources':['fall','drown','magic','dryOut','<init>']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in list(raw.items()):
            cl=ClassFile(jar.read(names.named[c]+'.class'));av={names.member(cl.name,m['name'],m['descriptor']) for m in cl.methods};raw[c]=sorted(m for m in av if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms));assert raw[c],c
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            av={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]+(['checkBurnOut'] if c.endswith('/FireBlock.class') else [])
            loader[c]=sorted(m for m in av if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$')))
    print('references',references(BATCH,raw,loader,{'net/neoforged/neoforge/common/CommonHooks.class':['onLivingFall'],'net/neoforged/neoforge/event/EventHooks.class':['onEnderTeleport']}),flush=True)
    vp=OUT/('vanilla-specifications/'+BATCH+'.json');vs=read_json(vp);vs['resources']=['data/minecraft/damage_type/'+x+'.json' for x in ['fall','drown','magic','dry_out']];write_json(vp,vs)
    from vanilla_reference import prepare
    write_json(OUT/('vanilla-evidence/'+BATCH+'.json'),prepare(vs))
    from twilight_subsection import damage_tags
    tags=damage_tags();loader_tags=[w for w in read_json(OUT/'reference-evidence/twilight-portals-244.json')['witnesses'] if '/tags/damage_type/' in w['entry']]
    declarations={r['entry'].rsplit('/',1)[-1][:-5]:r['data'] for r in read_json(OUT/('vanilla-evidence/'+BATCH+'.json'))['resources']}
    profiles=[]
    for name in ['fall','drown','magic','dry_out']:
        rid='minecraft:'+name;extra=['neoforge:'+w['entry'].rsplit('/',1)[-1][:-5] for w in loader_tags if rid in w['data']['values']]
        profiles.append(dict(type=rid,declaration=declarations[name],tags=sorted(set(tags(rid)+extra)),direct_entity=None,causing_entity=None,source_position=None,native_factory='DamageSources.'+('dryOut' if name=='dry_out' else name)))
    write_json(OUT/'twilightforest-control-blocks-vanilla-sources.json',dict(scope='Vanilla source identities reused by cloud native consumers; dry_out prevented through hydration, not emitted by cloud. Not custom Twilight DamageTypes.',profiles=profiles,loader_tags_evidence='reference-evidence/twilight-portals-244.json'))
    write_json(OUT/'twilightforest-control-blocks-caller-scan.json',scan)
    write_json(OUT/'twilightforest-control-blocks-config-snapshot.json',dict(path=str(CONFIG),sha256=sha256(CONFIG),data=tomllib.loads(CONFIG.read_text(encoding='utf-8')),scope='Static cloud config snapshot; world gamerules unknown.'))
if __name__=='__main__':collect()
