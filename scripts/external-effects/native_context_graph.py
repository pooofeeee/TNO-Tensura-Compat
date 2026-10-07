"""Prove visual-only call graphs from an existing pinned census, fail closed.

Only typed presentation roots are dispositioned. Read-only game dependencies
are checked for side effects but remain independently pending; neither names nor
raw code hashes grant semantic equivalence or Stage eligibility.
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
PROFILES=('visual-v1','presentation-audio-ui-v2')
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


def parts(symbol):
    match=re.fullmatch(r'(.+)\.([^.(]+)(\(.*)',symbol)
    return match.groups() if match else None


def external_allowed(symbol, profile='visual-v1'):
    p=parts(symbol)
    if not p:return False
    owner,name,_=p
    if profile=='presentation-audio-ui-v2' and owner.startswith('net/minecraft/client/sounds/'):
        return True
    if any(owner.startswith(x) for x in VISUAL+VALUES):return True
    if owner.startswith('[') and name=='clone':return True
    if owner.startswith('net/minecraft/world/entity/') and name in ENTITY_READ:return True
    return name in QUERY.get(owner,set())


def visual_entry(entry, profile='visual-v1'):
    return any(root in entry for root in ROOTS + (EXTRA_ROOTS if profile=='presentation-audio-ui-v2' else ()))


def typed_presentation_return(method):
    # A sound value carries no native combat contribution. The same strict
    # side-effect/API graph checks still apply; a getter name proves nothing.
    return method['descriptor'].endswith(')Lnet/minecraft/sounds/SoundEvent;')


def prove(census, profile='visual-v1'):
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
        entry=m['entry'];is_visual=visual_entry(entry,profile);deps=set()
        valid=not m['access'] & (0x100|0x400)
        for hit in decode_sites(census,m,'hits'):
            op=hit['opcode'];symbol=str(hit['operand'])
            if op in ('0xb3','0xb5'):
                owner=symbol.rsplit('.',1)[0]
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
    roots={k for k in native if visual_entry(k[0],profile) or (profile=='presentation-audio-ui-v2' and typed_presentation_return(native[k]))}
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
    if profile!='visual-v1':
        result['context_profile']=profile
    return result


def validate(doc,census):
    assert doc==prove(census,doc.get('context_profile','visual-v1')),'Context graph differs from independent finite call/field facts'
    return doc['rows']


def reproduce(doc,census,jar):
    assert sha256(jar)==census['jar_sha256']
    classes={c['entry']:c for c in census['classes']};parsed={}
    with zipfile.ZipFile(jar) as z:
        for row in doc['rows']:
            if row['entry'] not in parsed:
                raw=z.read(row['entry']);assert byte_hash(raw)==classes[row['entry']]['entry_sha256']
                parsed[row['entry']]=ClassFile(raw)
            c=parsed[row['entry']]
            m=next(m for m in c.methods if (m['name'],m['descriptor'])==(row['method'],row['descriptor']))
            assert byte_hash(m.get('code',b''))==row['code_sha256']
    return len(doc['rows'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mod_key')
    p.add_argument('--output',type=Path,required=True);p.add_argument('--jar',type=Path)
    p.add_argument('--profile',choices=PROFILES,default='visual-v1')
    a=p.parse_args();c=read_json(OUT/f'{a.mod_key}-combat-census.json');d=prove(c,a.profile)
    if a.jar:reproduce(d,c,a.jar)
    write_json(a.output,d);print(d['summary'])
