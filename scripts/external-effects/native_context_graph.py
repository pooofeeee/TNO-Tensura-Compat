"""Prove explicit native context graphs from an existing pinned census.

Profiles constrain roots and native operations; unknown dispatch fails closed.
Query proofs reject writes in the selected native bodies. Metadata factories
retain their native API behavior. No profile decides Stage eligibility, and
names or raw hashes alone grant neither equivalence nor coverage.
"""
import argparse
from collections import Counter
from pathlib import Path
import re
import zipfile

from catalog_common import OUT, read_json, write_json, sha256, byte_hash
from collect_combat_census import decode_sites
from classfile import ClassFile
from reconcile_native_census import method_key

ROOTS=('/client/model/', '/client/render/', '/client/particle/')
EXTRA_ROOTS=('/client/sound/', '/client/gui/')
PROFILES=('visual-v1','presentation-audio-ui-v2','native-value-metadata-v3','generation-layout-v4','native-query-context-v5','presentation-access-v6')
GEN_ROOTS=('/server/level/feature/','/server/level/carver/',
    '/server/level/surface/','/server/level/structure/')
GEN_VALUES=('net/minecraft/world/level/levelgen/synth/',
    'net/minecraft/world/level/levelgen/blending/',
    'net/minecraft/world/level/levelgen/feature/configurations/',
    'net/minecraft/world/level/levelgen/feature/stateproviders/',
    'net/minecraft/world/level/levelgen/heightproviders/',
    'net/minecraft/world/level/levelgen/structure/templatesystem/StructurePlaceSettings',
    'net/minecraft/world/level/levelgen/structure/BoundingBox',
    'net/minecraft/world/level/levelgen/Heightmap$',
    'net/minecraft/world/level/levelgen/GenerationStep$',
    'net/minecraft/world/level/levelgen/CarvingMask',
    'net/minecraft/util/valueproviders/', 'net/minecraft/core/SectionPos',
    'net/minecraft/tags/TagKey', 'net/minecraft/world/level/ChunkPos')
GEN_QUERY={
 'net/minecraft/world/level/WorldGenLevel': {'getBlockState','getFluidState','setBlock','isEmptyBlock','getHeight','getMinBuildHeight','getMaxBuildHeight','getRandom','getSeed','getBiome','ensureCanWrite','getLevel','isStateAtPosition','getBlockEntity'},
 'net/minecraft/world/level/LevelAccessor': {'getBlockState','getFluidState','setBlock','isEmptyBlock','getMinBuildHeight','getMaxBuildHeight','getRandom'},
 'net/minecraft/world/level/LevelReader': {'getBlockState','getFluidState','isEmptyBlock','getHeight','getMinBuildHeight','getMaxBuildHeight','getBiome'},
 'net/minecraft/world/level/StructureManager': {'startsForStructure','getStructureWithPieceAt'},
 'net/minecraft/world/level/chunk/ChunkGenerator': {'getBaseHeight','getFirstFreeHeight','getFirstOccupiedHeight','getSeaLevel'},
 'net/minecraft/world/level/levelgen/feature/Feature': {'<init>','setBlock','isReplaceable','isAir','isDirt','isStone','markAboveForPostProcessing'},
 'net/minecraft/world/level/levelgen/feature/FeaturePlaceContext': {'origin','random','level','config','chunkGenerator'},
 'net/minecraft/world/level/levelgen/structure/Structure': {'<init>','onTopOfChunkCenter','simpleCodec','adjustBoundingBox','settings','type'},
 'net/minecraft/world/level/levelgen/structure/StructurePiece': {'<init>','getWorldX','getWorldY','getWorldZ','getWorldPos','placeBlock','isInside','getBoundingBox','setOrientation','getOrientation','getGenDepth','isCloseToChunk','getBlock','generateBox','generateAirBox','fillColumnDown','createTag'},
 'net/minecraft/world/level/levelgen/structure/StructurePieceAccessor': {'addPiece'},
 'net/minecraft/world/level/block/state/BlockState': {'canSurvive','getBlock','isSolid','getDestroySpeed','isFaceSturdy','getTags','hasBlockEntity'},
 'net/minecraft/world/level/block/Block': {'getId'},
 'net/minecraft/world/level/material/FluidState': {'isEmpty'},
}
# These return types describe native metadata/geometry, never damage, effect,
# movement or admission scalars. Read-only bodies remain native API context;
# their callers and any side-effecting supplier stay independently pending.
VALUE_RETURNS=('Lnet/minecraft/world/phys/shapes/VoxelShape;',
    'Lnet/minecraft/world/level/block/RenderShape;',
    'Lcom/mojang/serialization/MapCodec;', 'Lcom/mojang/serialization/Codec;',
    'Lnet/minecraft/network/codec/StreamCodec;',
    'Lnet/minecraft/resources/ResourceLocation;',
    'Lnet/minecraft/world/item/UseAnim;',
    'Lnet/minecraft/world/level/material/MapColor;')
QUERY_RETURNS=('Z','B','C','S','I','J','F','D','Lnet/minecraft/world/phys/Vec3;',
    'Lnet/minecraft/world/phys/AABB;','Lnet/minecraft/world/level/block/state/BlockState;',
    'Lnet/minecraft/core/BlockPos;','Lnet/minecraft/world/item/ItemStack;')
VALUE_QUERY={
 'net/minecraft/world/level/block/Block': {'box','getShape','getCollisionShape','getBlockSupportShape','getVisualShape'},
 'net/minecraft/world/level/block/SnowLayerBlock': {'getCollisionShape'},
 'net/minecraft/world/level/block/state/BlockBehaviour': {'getShape','getCollisionShape','getBlockSupportShape','getVisualShape'},
 'net/minecraft/world/level/block/state/BlockState': {'getShape','getCollisionShape','getBlockSupportShape','getVisualShape'},
 'net/minecraft/world/level/block/state/properties/Property': {'getName','getValueClass'},
 'net/minecraft/world/phys/shapes/EntityCollisionContext': {'getEntity','isAbove','isDescending'},
 'net/minecraft/world/phys/shapes/CollisionContext': {'isAbove','isDescending','isHoldingItem','canStandOnFluid'},
}
VISUAL=('net/minecraft/client/model/', 'net/minecraft/client/renderer/',
        'net/minecraft/client/particle/', 'net/minecraft/client/resources/',
        'net/minecraft/client/gui/Font', 'com/mojang/blaze3d/', 'com/mojang/math/',
        'com/github/alexthe666/citadel/client/model/',
        'com/github/alexthe666/citadel/client/render/',
        'net/neoforged/neoforge/client/', 'org/joml/', 'org/lwjgl/')
VALUES=('java/lang/Math', 'java/lang/StrictMath', 'java/lang/Float',
        'java/lang/Double', 'java/lang/Integer', 'java/lang/Long', 'java/lang/Boolean',
        'java/lang/String', 'java/lang/StringBuilder', 'java/lang/Object',
        'java/lang/Enum', 'java/lang/Record', 'java/util/Objects',
        'java/util/Optional', 'java/util/UUID', 'java/util/ArrayList',
        'java/util/List', 'java/util/Map', 'java/util/Set', 'java/util/Iterator',
        'java/util/HashMap', 'java/util/HashSet', 'java/util/LinkedHashMap',
        'java/util/Collections', 'java/util/Comparator', 'java/util/stream/',
        'com/google/common/collect/', 'com/mojang/serialization/',
        'it/unimi/dsi/fastutil/objects/', 'net/minecraft/util/Mth',
        'net/minecraft/util/FastColor$', 'net/minecraft/util/RandomSource',
        'net/minecraft/resources/', 'net/minecraft/core/BlockPos',
        'net/minecraft/core/Direction', 'net/minecraft/core/Vec3i',
        'net/minecraft/world/phys/', 'net/minecraft/network/chat/',
        'net/minecraft/core/particles/', 'net/minecraft/CrashReport',
        'net/minecraft/ReportedException', 'org/slf4j/Logger')
ENTITY_READ={'getX','getY','getZ','getXRot','getYRot','getYHeadRot','getBbHeight',
    'getBbWidth','getDeltaMovement','getEyePosition','getEyeHeight','getPosition',
    'getType','getUUID','getVehicle','getViewVector','getViewXRot','isAlive',
    'isPassenger','isPassengerOfSameVehicle','onGround','position','shouldRiderSit',
    'blockPosition','getAttackAnim','getItemInHand','getMainArm','getScale',
    'getEffect','hasEffect','isBaby','isUsingItem','level','isCrouching',
    'getMainHandItem','getOffhandItem','distanceTo','distanceToSqr',
    'getBoundingBoxForCulling','getBubbleAngle','getDamage','getHurtDir',
    'getHurtTime','getRowingTime','isUnderWater','getBoundingBox',
    'isInvisible','isInvisibleTo','getId','getTeam','getName','getDisplayName',
    'getCustomName','hasCustomName','getPose','getLightProbePosition'}
QUERY={
 'net/minecraft/world/item/ItemStack': {'<init>','getCount','getDamageValue','getItem','hasFoil','is','isEmpty'},
 'net/minecraft/world/item/Item': {'getId'},
 'net/minecraft/world/item/ArmorItem': {'getMaterial'},
 'net/minecraft/world/item/ItemDisplayContext': {'firstPerson'},
 'net/minecraft/world/item/enchantment/EnchantmentHelper': {'getItemEnchantmentLevel'},
 'net/minecraft/world/entity/WalkAnimationState': {'position','speed'},
 'net/minecraft/world/effect/MobEffectInstance': {'getAmplifier','getDuration'},
 'net/minecraft/world/level/Level': {'dimensionType','getBiome','getBrightness','getMaxLocalRawBrightness','holderOrThrow','getBlockState','addParticle'},
 'net/minecraft/world/level/BlockGetter': {'getBlockState','getFluidState'},
 'net/minecraft/world/level/block/state/BlockState': {'getFluidState','getRenderShape','getValue','hasProperty','is','isAir','isFaceSturdy','setValue','toString'},
 'net/minecraft/world/level/block/Block': {'asItem','defaultBlockState'},
 'net/minecraft/world/level/material/FluidState': {'getFluidType','getHeight','is'},
 'net/minecraft/world/level/biome/Biome': {'getWaterColor'},
 'net/minecraft/world/level/dimension/DimensionType': {'coordinateScale'},
 'net/minecraft/core/Holder': {'is','unwrapKey','value'},
 'net/minecraft/core/Registry': {'asHolderIdMap'},
 'net/minecraft/core/RegistryAccess': {'registry'},
 'net/minecraft/core/IdMap': {'byId'},
 'net/minecraft/core/DefaultedRegistry': {'getKey','stream'},
 'net/neoforged/neoforge/registries/DeferredHolder': {'get'},
 'net/neoforged/neoforge/common/ModConfigSpec$BooleanValue': {'get'},
 'net/neoforged/neoforge/common/util/TriState': {'isDefault','isTrue'},
 'com/github/alexthe666/citadel/animation/Animation': {'getDuration'},
 'com/github/alexthe666/citadel/animation/LegSolver$Leg': {'getHeight'},
 'net/minecraft/client/Minecraft': {'getInstance','getDeltaTracker','getCameraEntity','getEntityRenderDispatcher','getItemRenderer','getBlockRenderer','getTextureManager','getWindow','isPaused','useShaderTransparency'},
 'net/minecraft/client/Camera': {'getPosition','getXRot','getYRot','getLookVector','getEntity','rotation'},
 'net/minecraft/client/multiplayer/ClientLevel': {'getBlockState','getFluidState','getEntitiesOfClass','getEntity','getGameTime','registryAccess','getLightEngine','addParticle','getShade','getMinBuildHeight','getMaxBuildHeight'},
}

# Additional exact display operations/readers. This version leaves old proofs
# byte-identical. Opaque callbacks, events, inputs, packet sends and entity
# setters are deliberately absent. It is a structural proof, not a classifier.
DISPLAY_QUERY={
 'net/minecraft/client/Minecraft': {'renderBuffers','getTimer','getMainRenderTarget','getSoundManager','getEntityModels','getResourceManager'},
 'net/minecraft/client/DeltaTracker': {'getGameTimeDeltaPartialTick'},
 'net/minecraft/client/Options': {'getCameraType','fov'},
 'net/minecraft/client/CameraType': {'isFirstPerson'},
 'net/minecraft/client/OptionInstance': {'get'},
 'net/minecraft/client/Camera': {'getNearPlane'},
 'net/minecraft/client/Camera$NearPlane': {'getPointOnPlane'},
 'net/minecraft/client/gui/GuiGraphics': {'pose','blit','drawString','renderTooltip','fill','fillGradient','renderItem','renderFakeItem','renderItemDecorations','drawCenteredString','enableScissor','disableScissor','flush','guiWidth','guiHeight','blitSprite','hLine','vLine'},
 'com/github/alexthe666/citadel/client/shader/PostEffectRegistry': {'renderEffectForNextTick','getRenderTargetFor'},
 'net/minecraft/world/level/block/entity/BlockEntity': {'getBlockPos','getBlockState','isRemoved','getLevel'},
 'net/minecraft/world/inventory/AbstractContainerMenu': {'getSlot'},
 'net/minecraft/world/inventory/Slot': {'getItem','hasItem'},
 'net/minecraft/world/item/crafting/Ingredient': {'getItems'},
 'net/neoforged/neoforge/entity/PartEntity': {'getBoundingBoxForCulling'},
 'net/minecraft/world/entity/Entity': {'isVehicle','fillCrashReportCategory'},
 'net/minecraft/world/item/Item': {'getDescriptionId'},
}


def parts(symbol):
    match=re.fullmatch(r'(.+)\.([^.(]+)(\(.*)',symbol)
    return match.groups() if match else None


def external_allowed(symbol, profile='visual-v1'):
    p=parts(symbol)
    if not p:return False
    owner,name,_=p
    if profile=='presentation-access-v6':
        if name in DISPLAY_QUERY.get(owner,set()):return True
        return external_allowed(symbol,'presentation-audio-ui-v2')
    if profile=='native-query-context-v5':
        # Sampling changes RNG state; builders/collection aliases and particle
        # APIs are not read-only, even when their result is a native value.
        if owner.startswith(('net/minecraft/util/RandomSource','java/util/Random','java/lang/StringBuilder')):return False
        if owner in ('java/lang/Math','java/lang/StrictMath') and name=='random':return False
        if owner=='net/minecraft/util/Mth' and name in (
                'randomBetween','randomBetweenInclusive','nextInt','nextFloat','nextDouble','wobble','createInsecureUUID'):
            return False
        if owner=='java/lang/Object' and name not in ('<init>','getClass'):return False
        if owner=='java/util/Objects' and name not in ('requireNonNull','requireNonNullElse','isNull','nonNull'):return False
        if owner=='org/slf4j/Logger':return False
        if owner.startswith(('java/util/','com/google/common/collect/','it/unimi/dsi/fastutil/')) and name in (
                'map','flatMap','filter','collect','orElseGet','equals','hashCode','toString'):
            return False  # Opaque callback/element dispatch is not proven pure.
        if owner=='java/lang/String' and name=='valueOf' and '(Ljava/lang/Object;)' in symbol:return False
        if owner=='net/minecraft/world/phys/Vec3' and name=='offsetRandom':return False
        if owner.startswith('net/minecraft/world/phys/') and owner not in (
                'net/minecraft/world/phys/Vec3','net/minecraft/world/phys/AABB',
                'net/minecraft/world/phys/shapes/Shapes','net/minecraft/world/phys/shapes/VoxelShape',
                'net/minecraft/world/phys/shapes/CollisionContext','net/minecraft/world/phys/shapes/EntityCollisionContext'):
            return False
        if name=='addParticle':return False
        return external_allowed(symbol,'native-value-metadata-v3')
    if profile=='generation-layout-v4':
        if any(owner.startswith(x) for x in GEN_VALUES):return True
        if name in GEN_QUERY.get(owner,set()):return True
        # Generation may write terrain, but not entities, inventories, block
        # entities or opaque native markers. Their exact paths remain pending.
        return external_allowed(symbol,'native-value-metadata-v3')
    if profile=='native-value-metadata-v3':
        # The presentation allow-list includes render mutations. None belongs
        # in a server-side value proof; only values and explicit native queries.
        if owner.startswith(('java/util/','com/google/common/collect/','it/unimi/dsi/fastutil/')):
            return name in {'<init>','get','getOrDefault','size','isEmpty','contains','containsKey','containsValue','iterator','hasNext','next','stream','values','keySet','entrySet','of','copyOf','emptyList','emptyMap','emptySet','singleton','singletonList','singletonMap','unmodifiableList','unmodifiableMap','unmodifiableSet','map','flatMap','filter','findFirst','findAny','collect','toList','orElse','orElseGet','isPresent','isEmpty','ofNullable','empty','comparing','comparingDouble','comparingInt','naturalOrder','reverseOrder','getKey','getValue','equals','hashCode','toString'}
        if any(owner.startswith(x) for x in VALUES):return True
        if owner.startswith('[') and name=='clone':return True
        if owner.startswith('net/minecraft/world/entity/') and name in ENTITY_READ:return True
        return name in QUERY.get(owner,set()) | VALUE_QUERY.get(owner,set())
    if profile=='presentation-audio-ui-v2' and owner.startswith('net/minecraft/client/sounds/'):
        return True
    if any(owner.startswith(x) for x in VISUAL+VALUES):return True
    if owner.startswith('[') and name=='clone':return True
    if owner.startswith('net/minecraft/world/entity/') and name in ENTITY_READ:return True
    return name in QUERY.get(owner,set())


def visual_entry(entry, profile='visual-v1'):
    return any(root in entry for root in ROOTS + (EXTRA_ROOTS if profile in ('presentation-audio-ui-v2','presentation-access-v6') else ()))


def typed_presentation_return(method):
    # A sound value carries no native combat contribution. The same strict
    # side-effect/API graph checks still apply; a getter name proves nothing.
    return method['descriptor'].endswith(')Lnet/minecraft/sounds/SoundEvent;')


def opcode_read_only(code):
    """Decode complete bytecode, not a byte substring or sparse field index."""
    parser=object.__new__(ClassFile);parser.resolve=lambda index:None
    ops={int(i['opcode'],16) for i in parser.instructions(code)}
    return not (ops & (set(range(0x4f,0x57)) | {0xb3,0xb5,0xc2,0xc3,0xa8,0xa9,0xc9}))


def opcode_no_alias_writes(code):
    parser=object.__new__(ClassFile);parser.resolve=lambda index:None
    ops={int(i['opcode'],16) for i in parser.instructions(code)}
    return not (ops & (set(range(0x4f,0x57)) | {0xc2,0xc3,0xa8,0xa9,0xc9}))


def prove(census, profile='visual-v1', bytecodes=None, selection=None):
    assert profile in PROFILES
    classes={c['name']:c for c in census['classes']}
    native={method_key(m):m for m in census['methods']}
    boot={(b['entry'],b['index']):b for b in census.get('registration_bootstraps',[])}
    dependencies={}; locally_valid=set()

    def resolve(owner,name,desc):
        seen=set()
        while owner in classes and owner not in seen:
            seen.add(owner);key=(owner+'.class',name,desc)
            if key in native:return key
            owner=classes[owner]['superclass']
        return None,owner

    def call(symbol, deps):
        p=parts(symbol)
        if not p:return False
        owner,name,desc=p
        r=resolve(owner,name,desc)
        if len(r)==3:
            deps.add(r)
            return True
        return external_allowed(r[1]+'.'+name+desc,profile)

    for key,m in native.items():
        entry=m['entry'];is_visual=profile not in ('native-value-metadata-v3','generation-layout-v4','native-query-context-v5') and visual_entry(entry,profile);deps=set()
        valid=not m['access'] & (0x100|0x400)
        if profile=='native-query-context-v5':
            raw=(bytecodes or {}).get(key)
            valid=valid and not m['access'] & 0x20 and raw is not None and byte_hash(raw)==m['code_sha256'] and opcode_read_only(raw)
        if profile=='presentation-access-v6':
            raw=(bytecodes or {}).get(key)
            valid=valid and not m['access'] & 0x20 and raw is not None and byte_hash(raw)==m['code_sha256'] and opcode_no_alias_writes(raw)
        for hit in decode_sites(census,m,'hits'):
            op=hit['opcode'];symbol=str(hit['operand'])
            if op in ('0xb3','0xb5'):
                owner=symbol.rsplit('.',1)[0]
                if profile=='generation-layout-v4' and any(root in entry for root in GEN_ROOTS) and any(root in owner for root in GEN_ROOTS):continue
                if not is_visual or not (visual_entry(owner,profile) or any(owner.startswith(x) for x in VISUAL)):
                    valid=False;break
        for hit in decode_sites(census,m,'calls'):
            symbol=str(hit['operand'])
            if hit['opcode']=='0xba':
                n=int(re.match(r'bootstrap#(\d+):',symbol).group(1))
                b=boot.get((entry,n))
                if not b:valid=False;break
                if 'StringConcatFactory.' in b['handle'] or 'ObjectMethods.bootstrap' in b['handle']:continue
                if 'LambdaMetafactory.' not in b['handle']:valid=False;break
                targets=[s for s in b['arguments'] if isinstance(s,str) and parts(s)]
                if not targets or not all(call(s,deps) for s in targets):valid=False;break
            elif not call(symbol,deps):valid=False;break
        dependencies[key]=deps
        if valid:locally_valid.add(key)
    # Greatest fixed point: every member of an SCC must independently meet
    # the field/API constraints. A cycle cannot hide a rejected member.
    safe=set(locally_valid)
    while True:
        rejected={k for k in safe if not dependencies[k] <= safe}
        if not rejected:break
        safe-=rejected
    roots=({k for k in native if k in set(selection or ()) and
             native[k]['descriptor'].split(')')[1] in QUERY_RETURNS} if profile=='native-query-context-v5' else
           {k for k in native if any(root in k[0] for root in GEN_ROOTS)} if profile=='generation-layout-v4' else
           {k for k in native if any(native[k]['descriptor'].endswith(')'+t) for t in VALUE_RETURNS)}
           if profile=='native-value-metadata-v3' else
           {k for k in native if visual_entry(k[0],profile) or (profile in ('presentation-audio-ui-v2','presentation-access-v6') and typed_presentation_return(native[k]))})
    if selection is not None:
        assert set(selection)<=set(native),'Unknown finite context selection'
        roots &= set(selection)
    accepted=roots & safe
    rows=[dict(entry=k[0],method=k[1],descriptor=k[2],code_sha256=native[k]['code_sha256'],
               entry_sha256=classes[k[0][:-6]]['entry_sha256'],
               disposition='TYPED_PRESENTATION_CALL_GRAPH',
               reason='Exact typed visual body and transitive calls write only presentation '
                      'state. Game readers are side-effect checked but not dispositioned.')
          for k in sorted(accepted)]
    result=dict(schema='tno.external_effects.native_context_graph.v1',mod_key=census['mod_key'],
        jar_sha256=census['jar_sha256'],scope='Typed presentation roots only; unknown/native '
        'dispatch, game writes, inputs/network and mixed consumers stay pending. '
        'External Citadel model/render APIs are visual dependencies, not proof of time-controller semantics.',
        rows=rows,summary=dict(methods=len(rows),remaining_presentation_methods=len(roots)-len(rows)))
    if profile=='native-value-metadata-v3':
        result['scope']='Exact typed native geometry/metadata values with a transitive no-game-write proof. Original geometry/state reads retained; caller admission, scalar inputs and side-effecting suppliers remain pending.'
        for row in rows:
            row.update(disposition='TYPED_NATIVE_VALUE_API_CONTEXT',reason='Read-only exact native geometry/metadata API body; no independent runtime scalar contribution. Native callers remain separately covered or pending.')
        result['summary']={'methods':len(rows),'remaining_value_methods':len(roots)-len(rows)}
    if profile=='generation-layout-v4':
        result['scope']='Exact finite world-generation layout graph only: native terrain placement/data allowed, actor/spawner/blockentity/inventory mutation and unknown dispatch rejected. Combat producers and runtime block semantics remain independently reviewed.'
        for row in rows:
            row.update(disposition='NATIVE_GENERATION_LAYOUT_CONTEXT',reason='Bounded world-generation geometry/terrain layout; transitive graph contains no actor or blockentity mutation. Native runtime block mechanics and encounter producers remain separate.')
        result['summary']={'methods':len(rows),'remaining_generation_methods':len(roots)-len(rows)}
    if profile=='native-query-context-v5':
        result['scope']='Exact finite selected native read-only query/formula context. Complete bytecodes and transitive call graph reject RNG, heap/array writes, monitor operations and unknown dispatch. Original values and gates are retained; caller contributions and eligibility are not inferred.'
        for row in rows:
            row.update(disposition='NATIVE_QUERY_FORMULA_CONTEXT',reason='Original query/formula and native gates retained as exact context; no new payload or Stage policy inferred. Side-effecting consumers remain independently dispositioned.')
        result['selection']=[dict(entry=k[0],method=k[1],descriptor=k[2]) for k in sorted(selection or ())]
        result['bytecodes']=[dict(entry=k[0],method=k[1],descriptor=k[2],code_hex=v.hex()) for k,v in sorted((bytecodes or {}).items())]
        result['summary']={'methods':len(rows),'remaining_query_methods':len(roots)-len(rows)}
    if profile=='presentation-access-v6':
        result['scope']='Selected typed display operations/native readers, complete transitive native bodies with no array alias writes. Native game writes, packets, events and opaque callbacks rejected; actor semantics remain independently canonical.'
        result['bytecodes']=[dict(entry=k[0],method=k[1],descriptor=k[2],code_hex=v.hex()) for k,v in sorted((bytecodes or {}).items())]
    if selection is not None:
        result['selection']=[dict(entry=k[0],method=k[1],descriptor=k[2]) for k in sorted(selection)]
    if profile!='visual-v1':
        result['context_profile']=profile
    return result


def validate(doc,census):
    profile=doc.get('context_profile','visual-v1')
    codes={method_key(r):bytes.fromhex(r['code_hex']) for r in doc.get('bytecodes',[])}
    selection={method_key(r) for r in doc['selection']} if 'selection' in doc else None
    assert doc==prove(census,profile,codes,selection),'Context graph differs from independent finite call/field facts'
    return doc['rows']


def collect_queries(census,selection,jar,profile='native-query-context-v5'):
    """Read only selected context roots and exact internal call dependencies."""
    assert sha256(jar)==census['jar_sha256']
    native={method_key(m):m for m in census['methods']}
    assert selection <= set(native)
    classes={c['name']:c for c in census['classes']}
    boot={(b['entry'],b['index']):b for b in census.get('registration_bootstraps',[])}
    roots=({k for k in selection if native[k]['descriptor'].split(')')[1] in QUERY_RETURNS}
           if profile=='native-query-context-v5' else set(selection))
    todo=list(roots);needed=set()
    while todo:
        key=todo.pop()
        if key in needed:continue
        needed.add(key)
        symbols=[]
        for hit in decode_sites(census,native[key],'calls'):
            symbol=str(hit['operand'])
            if hit['opcode']=='0xba':
                number=int(re.match(r'bootstrap#(\d+):',symbol).group(1))
                b=boot.get((key[0],number),{})
                symbols += [s for s in b.get('arguments',[]) if isinstance(s,str)]
            else:symbols.append(symbol)
        for symbol in symbols:
            p=parts(symbol)
            if not p:continue
            owner,name,desc=p;seen=set()
            while owner in classes and owner not in seen:
                seen.add(owner);target=(owner+'.class',name,desc)
                if target in native:todo.append(target);break
                owner=classes[owner]['superclass']
    codes={}
    with zipfile.ZipFile(jar) as z:
        for entry in sorted({k[0] for k in needed}):
            raw=z.read(entry);assert byte_hash(raw)==classes[entry[:-6]]['entry_sha256']
            c=ClassFile(raw)
            for m in c.methods:
                key=(entry,m['name'],m['descriptor'])
                if key in needed:
                    code=m.get('code',b'');assert byte_hash(code)==native[key]['code_sha256'];codes[key]=code
    assert set(codes)==needed
    return prove(census,profile,codes,roots)


def reproduce(doc,census,jar):
    assert sha256(jar)==census['jar_sha256']
    classes={c['entry']:c for c in census['classes']};parsed={}
    with zipfile.ZipFile(jar) as z:
        for row in doc['rows']+doc.get('bytecodes',[]):
            if row['entry'] not in parsed:
                raw=z.read(row['entry']);assert byte_hash(raw)==classes[row['entry']]['entry_sha256']
                parsed[row['entry']]=ClassFile(raw)
            c=parsed[row['entry']]
            m=next(m for m in c.methods if (m['name'],m['descriptor'])==(row['method'],row['descriptor']))
            code=m.get('code',b'')
            if 'code_hex' in row:assert code.hex()==row['code_hex']
            else:assert byte_hash(code)==row['code_sha256']
    return len(doc['rows'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mod_key')
    p.add_argument('--output',type=Path,required=True);p.add_argument('--jar',type=Path)
    p.add_argument('--profile',choices=PROFILES,default='visual-v1')
    p.add_argument('--selection',type=Path)
    a=p.parse_args();c=read_json(OUT/f'{a.mod_key}-combat-census.json')
    if a.profile in ('native-query-context-v5','presentation-access-v6'):
        assert a.jar and a.selection,'Query context requires an exact finite selection and pinned JAR'
        selected={method_key(r) for r in read_json(a.selection)['methods']}
        d=collect_queries(c,selected,a.jar,a.profile)
    else:d=prove(c,a.profile,selection={method_key(r) for r in read_json(a.selection)['methods']} if a.selection else None)
    if a.jar:reproduce(d,c,a.jar)
    write_json(a.output,d);print(d['summary'])
