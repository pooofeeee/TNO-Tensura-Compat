"""Native portal producer, lightning mode, transition and persistence guards."""
from catalog_common import *
from classfile import ClassFile
import tomllib

def validate_portals(d,s,old,new,methods,ins,pos,target):
    from collect_twilight_portals import scan_callers,CONFIG
    assert read_json(OUT/'twilightforest-portals-caller-scan.json')==scan_callers(target)
    snap=read_json(OUT/'twilightforest-portals-config-snapshot.json');assert snap['sha256']==sha256(CONFIG) and snap['data']==tomllib.loads(CONFIG.read_text(encoding='utf-8'))
    cfg=snap['data']['Portal Settings'];assert {k:cfg[k] for k in ['originDimension','allowPortalsInOtherDimensions','portalCreationPermission','disablePortalCreation','checkPortalPlacement','destructivePortalLightning','shouldReturnPortalBeUsable','portalUnlockedByAdvancement','maxPortalSize']}==dict(originDimension='minecraft:overworld',allowPortalsInOtherDimensions=False,portalCreationPermission=0,disablePortalCreation=False,checkPortalPlacement=True,destructivePortalLightning=True,shouldReturnPortalBeUsable=True,portalUnlockedByAdvancement='',maxPortalSize=64)
    assert snap['data']['Dimension Settings']=={'newPlayersSpawnInTF':False,'portalForNewPlayer':False}
    P='block/TFPortalBlock';T='world/TFTeleporter';E='events/ProgressionEvents';A='events/CapabilityEvents';V='components/entity/TFPortalAttachment'
    outer=ins(E,'performProtectionAndPortalChecks');assert pos(outer,'disablePortalCreation')<pos(outer,'checkPortalPlacement')<pos(outer,'.getProfilePermissions(')<pos(outer,'.checkForPortalCreation(')
    create=ins(E,'checkForPortalCreation');assert pos(create,'originDimension')<pos(create,'.getEntitiesOfClass(')<pos(create,'PORTAL_ACTIVATOR')<pos(create,'.canFormPortal(')<pos(create,'.getOwner(')<pos(create,'Objects.equals(')<pos(create,'.getPortalLockingAdvancement(')<pos(create,'.tryToCreatePortal(')<pos(create,'MADE_TF_PORTAL')
    pool=ins(P,'recursivelyValidatePortal');assert pos(pool,'.incrementAndGet(')<pos(pool,'maxPortalSize')<pos(pool,'.isFaceSturdy(')<pos(pool,'.recursivelyValidatePortal(')
    assert any(int(x['opcode'],16)==0xa6 for x in pool),'Exact BlockState identity comparison'
    commit=ins(P,'tryToCreatePortal');assert pos(commit,'.canFormPortal(')<pos(commit,'.recursivelyValidatePortal(')<pos(commit,'checkPortalPlacement')<pos(commit,'.isSafeAround(')<pos(commit,'.shrink(')<pos(commit,'.causeLightning(')<pos(commit,'.setBlock(')
    at=next(i for i,x in enumerate(commit) if 'checkPortalPlacement' in str(x['operand']));assert int(commit[at+1]['opcode'],16)==0x9a,'True skips current-level precheck'
    lightning=ins(P,'causeLightning');assert pos(lightning,'LightningBolt.<init>(')<pos(lightning,'.setVisualOnly(')<pos(lightning,'.addFreshEntity(')<pos(lightning,'.getEntitiesOfClass(')<pos(lightning,'.onEntityStruckByLightning(')<pos(lightning,'.thunderHit(')
    at=next(i for i,x in enumerate(lightning) if '.setVisualOnly(' in str(x['operand']));assert int(lightning[at-1]['opcode'],16)==0x1c,'Local2 actual destructive bool passed unchanged'
    at=next(i for i,x in enumerate(lightning) if '.addFreshEntity(' in str(x['operand']));assert int(lightning[at+1]['opcode'],16)==0x57
    assert any(x['operand']==3.0 for x in lightning) and not any('.setCause(' in str(x['operand']) or '.hurt(' in str(x['operand']) for x in lightning)
    contact=ins(P,'entityInside');assert pos(contact,'.defaultBlockState(')<pos(contact,'ServerPlayer')<pos(contact,'.canUsePortal(')<pos(contact,'.setAsInsidePortal(')<pos(contact,'TF_PORTAL_COOLDOWN')<pos(contact,'.setInPortal(')
    assert any(int(x['opcode'],16)==0xa6 for x in contact)
    destination=ins(P,'getPortalDestination');assert pos(destination,'cachedOriginDimension')<pos(destination,'originDimension')<pos(destination,'.getLevel(')<pos(destination,'.getTeleportationScale(')<pos(destination,'.clampToBounds(')<pos(destination,'.createTransition(')
    transition=ins(T,'makeTransition');assert any('Vec3.ZERO' in str(x['operand']) for x in transition) and any('PLACE_PORTAL_TICKET' in str(x['operand']) for x in transition)
    # Exact loading bug is documented, not repaired: the second coordinate reads Y.
    load=ins(T,'loadSurroundingArea');assert pos(load,'Vec3.x(')<pos(load,'Vec3.y(') and not any('Vec3.z(' in str(x['operand']) for x in load)
    build=ins(T,'makePortalAt');assert pos(build,'Blocks.GRASS_BLOCK')<pos(build,'DISALLOW_RETURN')<pos(build,'shouldReturnPortalBeUsable')<pos(build,'.removeBlock(')<pos(build,'.randNatureBlock(')
    assert not any('BreakEvent' in str(x['operand']) or '.hurt(' in str(x['operand']) for x in build)
    safe=ins(T,'isUnsafe');assert pos(safe,'DIMENSION_KEY')<pos(safe,'.isOutsideBorder(')<pos(safe,'.biomeUnsafe(')<pos(safe,'.posOverlapsRestrictedStructureChunk(')
    entry=ins(A,'newSpawnInTwilightForest');assert pos(entry,'newPlayersSpawnInTF')<pos(entry,'.getLevel(')<pos(entry,'portalForNewPlayerSpawn')<pos(entry,'.changeDimension(')<pos(entry,'.setRespawnPosition(')<pos(entry,'BANISHED_TO_TWILIGHT_FOREST')
    at=next(i for i,x in enumerate(entry) if '.changeDimension(' in str(x['operand']));assert int(entry[at+1]['opcode'],16)==0x57
    assert not any('.setHealth(' in str(x['operand']) or '.hurt(' in str(x['operand']) for x in entry)
    assert not any('.makePortalAt(' in str(x['operand']) for m in methods('world/NoReturnTeleporter') for x in m['instructions'])
    overlay=ins(V,'tick');assert any(x['operand']==2 for x in overlay) and not any('PortalProcessor' in str(x['operand']) or '.changeDimension(' in str(x['operand']) for x in overlay)
    refs=[w for p in (OUT/'reference-evidence').glob('*.json') for w in read_json(p).get('witnesses',[]) if w.get('archive_sha256') in ['8e3563a078289f0f07ee6f87f1c8651294387639c8355983ee207cb753f08b7f','d874b2aa4d511919a567ae73f13510e63e16f7318194eb2c03824cd68a59df6f']]
    raw=[c for p in (OUT/'vanilla-evidence').glob('*.json') for c in read_json(p).get('classes',[])]
    def rm(c,n):return [m for w in refs if w['entry']==c+'.class' for m in w.get('methods',[]) if m['name']==n] or [m for w in raw if w['class_name']==c for m in w['methods'] if m['name']==n]
    def ri(c,n):return rm(c,n)[0]['instructions']
    proc=ri('net/minecraft/world/entity/PortalProcessor','processPortalTeleportation');assert pos(proc,'.insidePortalThisTick')<pos(proc,'.portalTime')<pos(proc,'.getPortalTransitionTime(')<pos(proc,'.decayTick(') and any(int(x['opcode'],16)==0xa1 for x in proc)
    decay=ri('net/minecraft/world/entity/PortalProcessor','decayTick');assert any(x['operand']==4 for x in decay) and any('Math.max(' in str(x['operand']) for x in decay)
    living=ri('net/minecraft/world/entity/LivingEntity','canUsePortal');assert pos(living,'Entity.canUsePortal(')<pos(living,'.isSleeping(')
    handle=ri('net/minecraft/world/entity/Entity','handlePortal');assert pos(handle,'.processPortalCooldown(')<pos(handle,'.processPortalTeleportation(')<pos(handle,'.setPortalCooldown(')<pos(handle,'.getPortalDestination(')<pos(handle,'.changeDimension(')
    nativeplayer=ri('net/minecraft/server/level/ServerPlayer','changeDimension');assert pos(nativeplayer,'.onTravelToDimension(')<pos(nativeplayer,'.teleport(') and not any('.setDeltaMovement(' in str(x['operand']) for x in nativeplayer)
    natentity=ri('net/minecraft/world/entity/Entity','changeDimension');assert pos(natentity,'.onTravelToDimension(')<pos(natentity,'.speed(')<pos(natentity,'.setDeltaMovement(')
    thunder=ri('net/minecraft/world/entity/Entity','thunderHit');assert pos(thunder,'.setRemainingFireTicks(')<pos(thunder,'.igniteForSeconds(')<pos(thunder,'.lightningBolt(')<pos(thunder,'.getDamage(')<pos(thunder,'.hurt(')
    bolt=ri('net/minecraft/world/entity/LightningBolt','tick');assert pos(bolt,'.visualOnly')<pos(bolt,'.onEntityStruckByLightning(')<pos(bolt,'.thunderHit(')
    owner=ri('net/minecraft/world/entity/item/ItemEntity','getOwner');assert pos(owner,'.cachedThrower')<pos(owner,'.thrower')<pos(owner,'.getEntity(') and not any('.target' in str(x['operand']) for x in owner)
    collision=ri('net/minecraft/world/level/block/state/BlockBehaviour$BlockStateBase$Cache','<init>');assert any('Block.getCollisionShape(' in str(x['operand']) for x in collision)
    resources=read_json(WORK/'twilightforest/resources.json');assert resources['data/twilightforest/tags/block/portal/fluid.json']['data']['values']==['minecraft:water'] and resources['data/twilightforest/tags/item/portal/activator.json']['data']['values']==['#c:gems/diamond']
    assert len(resources['data/twilightforest/tags/block/portal/generated_decoration.json']['data']['values'])==17
    loader=read_json(OUT/'reference-evidence/twilight-portals-244.json')['witnesses'];env=next(w['data'] for w in loader if w['entry']=='data/neoforge/tags/damage_type/is_environment.json');assert 'minecraft:lightning_bolt' in env['values']
    assert old.get('semantic_corrections')==new.get('semantic_corrections') and not s['damage_profiles'] and d['damage_census']['reviewed_profiles_after']==40
