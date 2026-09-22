"""Installed Travellers movement, state, packets and bounded ASM witnesses."""
from twilight_evidence import *
from vanilla_reference import MojangNames,CLIENT
from selected_reference import collect as reference_collect
import tomllib
BATCH='twilight-travellers-movement'
T='item/travellers_gear/'
FULL=[T+'TravellersGearLogic']+['components/entity/'+c for c in ['SlimySolesAttachment','TravellersWingsAttachment','TravellersWingsAttachment$WingState','TravellersWingsAnimAttachment']]+['network/'+c for c in ['PerformDoubleJumpPacket','PerformSidestepPacket','GradualGlidePacket','TravellersWingsStatePacket']]
TRANSFORMERS=['WaterWalkTransformer','ResetStuckUnrestrainedTransformer','UnrestrainedBlockSpeedAndJumpFactorTransformer','WaterSprintTransformer','SlimeBlockBounceUpTransformer','SlimeBlockMomentumTransformer','UnrestrainedFrictionTransformer','GetFieldOfViewModifierTransformer']
TOKENS=['WATER_WALK','UNRESTRAINED','SLIMY_SOLES','DOUBLE_JUMP','SIDESTEP','GRADUAL_GLID','GRADUALLY_GLID','STRAIGHT_AHEAD','AGILE_RANGER','STEP_UP_ABILITY','JUMP_AMPLIFIER','SWIFT_SWIM','TRAVELLERS_HIGH_STEP','manualTravellersWingsGradualGlideDefault']

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
    return dict(jar_sha256=target['sha256'],scope='All TF instruction callers of reviewed movement components/state. Leash pathfinder, belt/display/zoom, armor rendering and other ASM remain separately unfinished.',needles=TOKENS,hits=hits)

def collect():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    classes={c:['*'] for c in FULL}
    classes.update({'events/TravellersGearEvents':['setup','reduceSlimySolesFallDamage','calculateFallDamage','cancelSlimySolesJump','tickMovementModifiers','disableHighStepWhileSneaking','updateOtherModifiers','keepAttachmentsOnDeath','<clinit>'],'client/event/TravellersClientEvents':['setup','handleAgileRanger','handleStraightAhead','speedUpControlledWhileSneaking','handleSidestep','handleDoubleJump','updateGradualGlideState','ignoreKeyEvent'],'asmhooks/EntityHooks':['processWaterWalking','unrestrainedSprintingInWater','unrestrainedSwimPredicate','resetFactorWithUnrestrained','resetStuckUnrestrained'],'asmhooks/BlockHooks':['resetBlockFrictionWithUnrestrained','resetSlimeMomentumWithUnrestrained','stopBouncing'],'asmhooks/PlayerHooks':['straightAheadNullify','straightAheadRestore'],'init/TFAttributeModifiers':['<clinit>'],'init/TFDataComponents':['*'],'init/TFDataAttachments':['*'],'config/TFClientConfig':['<init>']})
    with zipfile.ZipFile(target['path']) as jar:
        cfg=ClassFile(jar.read('twilightforest/config/TFConfig.class'))
        classes['config/TFConfig']=[m['name'] for m in cfg.methods if any('manualTravellersWingsGradualGlideDefault' in str(i['operand']) for i in cfg.instructions(m.get('code',b'')))]
        for c,wanted in list(classes.items()):
            if wanted==['*']:continue
            available={m['name'] for m in ClassFile(jar.read('twilightforest/'+c+'.class')).methods}
            classes[c]=sorted(set(wanted)|{m for m in available if any(m.startswith('lambda$'+n+'$') for n in wanted)})
    print('native',native(BATCH,classes),flush=True)
    raw={'net/minecraft/world/entity/LivingEntity':['canStandOnFluid','travel','getWaterSlowDown','getJumpPower','getJumpBoostPower','jumpFromGround','causeFallDamage','calculateFallDamage','collectEquipmentChanges','handleEquipmentChanges'], 'net/minecraft/world/entity/Entity':['move','getBlockSpeedFactor','getBlockJumpFactor','push','resetFallDistance','getGravity'], 'net/minecraft/world/entity/player/Player':['jumpFromGround'], 'net/minecraft/client/player/LocalPlayer':['aiStep'], 'net/minecraft/client/player/AbstractClientPlayer':['getFieldOfViewModifier'], 'net/minecraft/world/level/block/LiquidBlock':['getCollisionShape','<clinit>'], 'net/minecraft/world/phys/shapes/EntityCollisionContext':['<init>','isAbove','canStandOnFluid'], 'net/minecraft/world/level/block/SlimeBlock':['stepOn','bounceUp','fallOn'], 'net/minecraft/world/entity/ai/attributes/AttributeInstance':['addPermanentModifier','addTransientModifier','addOrUpdateTransientModifier','removeModifier','save','load'], 'net/minecraft/world/entity/ai/attributes/Attributes':['<clinit>'], 'net/minecraft/world/effect/MobEffects':['<clinit>'], 'net/minecraft/world/effect/MobEffect':['addAttributeModifiers'], 'net/minecraft/world/effect/MobEffect$AttributeTemplate':['create']}
    names=MojangNames()
    with zipfile.ZipFile(CLIENT) as jar:
        names.jar=jar
        for c,ms in raw.items():
            cls=ClassFile(jar.read(names.named[c]+'.class'));available={names.member(cls.name,m['name'],m['descriptor']) for m in cls.methods}
            raw[c]=sorted({m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
    loader={c+'.class':list(ms) for c,ms in raw.items()};template=read_json(OUT/'reference-specifications/vv-loader-244.json');a=next(a for a in template['archives'] if a['path'].endswith('client.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c in loader:
            if c not in jar.namelist():continue
            available={m['name'] for m in ClassFile(jar.read(c)).methods};wanted=raw[c[:-6]]
            loader[c]=sorted({m for m in available if m in wanted or any(m.startswith('lambda$'+n+'$') for n in wanted if not n.startswith('lambda$'))})
    hooks={'net/neoforged/neoforge/event/entity/living/LivingFallEvent.class':['*'],'net/neoforged/neoforge/common/CommonHooks.class':['onLivingFall','onLivingJump'],'net/neoforged/neoforge/client/ClientHooks.class':['onMovementInputUpdate'],'net/neoforged/neoforge/common/extensions/IBlockExtension.class':['getFriction'],'net/neoforged/neoforge/attachment/AttachmentType$Builder.class':['serialize','copyOnDeath','build'],'net/neoforged/neoforge/attachment/AttachmentInternals.class':['copyEntityAttachments'],'net/neoforged/neoforge/common/extensions/IEntityExtension.class':['getFluidTypeHeight']}
    a=next(a for a in template['archives'] if a['path'].endswith('universal.jar'))
    with zipfile.ZipFile(a['path']) as jar:
        for c,ms in hooks.items():
            available={m['name'] for m in ClassFile(jar.read(c)).methods}
            hooks[c]=sorted(available if ms==['*'] else {m for m in available if m in ms or any(m.startswith('lambda$'+n+'$') for n in ms)})
            assert hooks[c],(c,ms,available)
    print('references',references(BATCH,raw,loader,hooks),flush=True)
    nestedpath=WORK/'twilightforest/nested-tf-asm.jar'
    with zipfile.ZipFile(nestedpath) as jar:asmclasses={n:['*'] for n in jar.namelist() if n.endswith('.class') and n.rsplit('/',1)[-1][:-6] in TRANSFORMERS}
    assert len(asmclasses)==8,asmclasses
    spec=dict(id=BATCH+'-asm',scope='Eight installed service-registered movement transformers. Leash pathfinder is a separate structure mechanic, explicitly pending.',archives=[dict(path=str(nestedpath),sha256=sha256(nestedpath),classes=asmclasses,resources=[])])
    write_json(OUT/'reference-specifications'/f'{BATCH}-asm.json',spec);write_json(OUT/'reference-evidence'/f'{BATCH}-asm.json',reference_collect(spec,source_aids=True))
    config=Path(target['path']).parent.parent/'config/twilightforest-client.toml';text=config.read_bytes().decode('utf-8')
    write_json(OUT/'config-evidence/twilightforest-client.json',dict(baseline=BASELINE,path=str(config),sha256=sha256(config),text=text,values=tomllib.loads(text)))
    write_json(OUT/'twilightforest-travellers-movement-caller-scan.json',scan_callers(target))

if __name__=='__main__':collect()
