"""Promote explicitly reviewed native contracts; never infer semantics or policy."""
import argparse
import re
from collections import Counter
from copy import deepcopy

from catalog_common import OUT,read_json,write_json
from audit_catalog_integrity import EvidenceIndex,audit_review
from refresh_catalog_views import refresh


def effect_holder_binding(method,offset):
    """Read the holder argument of this allocation, not a nearby effect query."""
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert 'MobEffectInstance.<init>(' in str(body[at]['operand'])
    start=max(n for n,i in enumerate(body[:at]) if i['opcode']=='0xbb' and
              i['operand']=='net/minecraft/world/effect/MobEffectInstance')
    holder=next(i for i in body[start:at] if i['opcode']=='0xb2' and
                ('/MobEffects.' in str(i['operand']) or '/ArphexModMobEffects.' in str(i['operand'])))
    return holder['operand'],body[start]['offset'],holder['offset']


def literal_effect_arguments(method, offset):
    """Bind literal status arguments; refuse computed values or nearby literals."""
    body = method['instructions']
    at = next(n for n, i in enumerate(body) if i['offset'] == offset)
    match = re.fullmatch(
        r'net/minecraft/world/effect/MobEffectInstance\.<init>\(Lnet/minecraft/core/Holder;(II(?:ZZ|ZZZ)?)\)V',
        str(body[at]['operand']))
    assert match, ('unsupported literal status constructor', offset)
    count = len(match.group(1))
    arguments = body[at-count:at]
    assert len(arguments) == count and all(
        i['opcode'] in ('0x2', '0x3', '0x4', '0x5', '0x6', '0x7', '0x8', '0x10', '0x11', '0x12', '0x13')
        and type(i['operand']) is int for i in arguments), ('computed status arguments', offset)
    holder, _, load = effect_holder_binding(method, offset)
    assert load < arguments[0]['offset']
    flags = [i['operand'] for i in arguments[2:]]
    assert all(v in (0, 1) for v in flags), ('invalid literal status flags', offset)
    return dict(holder=holder, duration=arguments[0]['operand'],
                amplifier=arguments[1]['operand'], explicit_flags=flags)


def rounded_tag_quotient_binding(method, offset):
    """Prove round(entity.rawTag / literal), without conflating display copies."""
    body = method['instructions']
    at = next(n for n, i in enumerate(body) if i['offset'] == offset)
    assert body[at]['operand'] == 'java/lang/Math.round(D)J'
    source = body[at-6:at]
    assert len(source) == 6 and source[0]['opcode'] in ('0x19', '0x2a', '0x2b', '0x2c', '0x2d')
    assert source[1]['operand'] == 'net/minecraft/world/entity/Entity.getPersistentData()Lnet/minecraft/nbt/CompoundTag;'
    assert source[2]['opcode'] in ('0x12', '0x13') and type(source[2]['operand']) is str
    assert source[3]['operand'] == 'net/minecraft/nbt/CompoundTag.getDouble(Ljava/lang/String;)D'
    assert source[4]['opcode'] in ('0xe', '0xf', '0x14') and type(source[4]['operand']) is float
    assert source[5]['opcode'] == '0x6f' and source[4]['operand'] != 0.
    local = source[0].get('local_index')
    if local is None:
        local = int(source[0]['opcode'], 16) - 0x2a
    assert local >= 0
    return dict(tag_key=source[2]['operand'], divisor=source[4]['operand'],
                entity_local_index=local, conversion='JAVA_MATH_ROUND_DOUBLE_TO_LONG')


def literal_food_component_binding(method, offset):
    """Read only the exact literal builder passed to Item.Properties.food."""
    body = method['instructions']
    at = next(n for n, i in enumerate(body) if i['offset'] == offset)
    assert body[at]['operand'] == 'net/minecraft/world/item/Item$Properties.food(Lnet/minecraft/world/food/FoodProperties;)Lnet/minecraft/world/item/Item$Properties;'
    prefix = 'net/minecraft/world/food/FoodProperties$Builder'
    start = max(n for n, i in enumerate(body[:at]) if i['opcode'] == '0xbb' and i['operand'] == prefix)
    chain = body[start:at]
    assert len(chain) in (8, 9)
    assert [i['opcode'] for i in chain[:3]] == ['0xbb', '0x59', '0xb7']
    assert chain[2]['operand'] == prefix + '.<init>()V'
    nutrition, saturation = chain[3], chain[5]
    assert nutrition['opcode'] in ('0x2', '0x3', '0x4', '0x5', '0x6', '0x7', '0x8', '0x10', '0x11', '0x12', '0x13') and type(nutrition['operand']) is int
    assert saturation['opcode'] in ('0xb', '0xc', '0xd', '0x12', '0x13') and type(saturation['operand']) is float
    assert chain[4]['operand'] == prefix + '.nutrition(I)L' + prefix + ';'
    assert chain[6]['operand'] == prefix + '.saturationModifier(F)L' + prefix + ';'
    if len(chain) == 9:
        assert chain[7]['operand'] == prefix + '.alwaysEdible()L' + prefix + ';'
    assert chain[-1]['operand'] == prefix + '.build()Lnet/minecraft/world/food/FoodProperties;'
    return dict(nutrition=nutrition['operand'], saturation_modifier=saturation['operand'],
                always_edible=len(chain) == 9, builder_allocation_offset=chain[0]['offset'])


def damage_source_binding(method,offset):
    """Bind an explicitly allocated native source to its following hurt call.

    This helper supports direct allocation sites only. It does not infer the
    provenance of a source local, field, factory result or an inherited source.
    """
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert '.hurt(' in str(body[at]['operand'])
    start=max(n for n,i in enumerate(body[:at]) if i['opcode']=='0xbb' and
              i['operand']=='net/minecraft/world/damagesource/DamageSource')
    ctor=next(i for i in body[start:at] if 'DamageSource.<init>(' in str(i['operand']))
    holder=next((i for i in body[start:at] if i['opcode']=='0xb2' and
                 '/DamageTypes.' in str(i['operand'])),None)
    if holder is None:
        # Custom keys must use the exact contiguous DAMAGE_TYPE/literal/parse/
        # ResourceKey.create/holderOrThrow chain, rather than a nearby string.
        key_at=next(n for n in range(start,at) if body[n]['operand']==
                    'net/minecraft/core/registries/Registries.DAMAGE_TYPELnet/minecraft/resources/ResourceKey;')
        key=body[key_at+1]
        assert key['opcode'] in ('0x12','0x13') and isinstance(key['operand'],str)
        assert [i['operand'] for i in body[key_at+2:key_at+5]]==[
            'net/minecraft/resources/ResourceLocation.parse(Ljava/lang/String;)Lnet/minecraft/resources/ResourceLocation;',
            'net/minecraft/resources/ResourceKey.create(Lnet/minecraft/resources/ResourceKey;Lnet/minecraft/resources/ResourceLocation;)Lnet/minecraft/resources/ResourceKey;',
            'net/minecraft/world/level/LevelAccessor.holderOrThrow(Lnet/minecraft/resources/ResourceKey;)Lnet/minecraft/core/Holder;']
        symbol='RESOURCE_LOCATION:'+key['operand']
    else:
        symbol=holder['operand']
    assert not any('.hurt(' in str(i['operand']) for i in body[start:at])
    return symbol,body[start]['offset'],ctor['offset'],ctor['operand']


def direct_damage_actor_local(method, offset):
    """Prove the direct Entity argument slot of an explicit source allocation."""
    _, _, ctor, descriptor = damage_source_binding(method, offset)
    assert descriptor.endswith('(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/Entity;)V')
    body = method['instructions']
    at = next(n for n, instruction in enumerate(body) if instruction['offset'] == ctor)
    load = body[at - 1]
    assert load['opcode'] in ('0x19', '0x2a', '0x2b', '0x2c', '0x2d')
    return load['local_index']


def literal_attribute_binding(method,offset):
    """Bind a direct native attribute-builder literal; decline expressions."""
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert body[at]['operand']=='net/minecraft/world/entity/ai/attributes/AttributeSupplier$Builder.add(Lnet/minecraft/core/Holder;D)Lnet/minecraft/world/entity/ai/attributes/AttributeSupplier$Builder;'
    holder,value=body[at-2:at]
    assert holder['opcode']=='0xb2' and '/Attributes.' in str(holder['operand'])
    assert value['opcode'] in ('0xe','0xf','0x14') and isinstance(value['operand'],(int,float))
    return dict(attribute_symbol=holder['operand'],holder_offset=holder['offset'],
                value_offset=value['offset'],native_value=value['operand'])


def literal_block_factor_binding(method, offset):
    """Bind a declared block motion property, without inferring its consumers."""
    body = method['instructions']
    at = next(n for n, i in enumerate(body) if i['offset'] == offset)
    factors = {f'net/minecraft/world/level/block/state/BlockBehaviour$Properties.{name}(F)Lnet/minecraft/world/level/block/state/BlockBehaviour$Properties;': name
               for name in ('speedFactor', 'jumpFactor', 'friction')}
    assert at > 0 and body[at]['operand'] in factors
    value = body[at-1]
    assert value['opcode'] in ('0xb', '0xc', '0xd', '0x12', '0x13')
    assert type(value['operand']) in (int, float)
    return dict(property=factors[body[at]['operand']], native_value=value['operand'],
                value_offset=value['offset'])


def literal_rng_bounds_binding(method, offset):
    """Pin two literal inclusive Mth.nextInt bounds; prove no reachability claim."""
    body = method['instructions']
    at = next(n for n, i in enumerate(body) if i['offset'] == offset)
    assert body[at]['operand'] == 'net/minecraft/util/Mth.nextInt(Lnet/minecraft/util/RandomSource;II)I'
    assert at >= 2
    low, high = body[at-2:at]
    integer_ops = {'0x2', '0x3', '0x4', '0x5', '0x6', '0x7', '0x8',
                   '0x10', '0x11', '0x12', '0x13'}
    assert all(i['opcode'] in integer_ops and type(i['operand']) is int
               for i in (low, high))
    assert low['operand'] <= high['operand']
    return dict(minimum=low['operand'], maximum=high['operand'],
                minimum_offset=low['offset'], maximum_offset=high['offset'])


def literal_numeric_input_binding(method, offset):
    """Pin a literal scalar input to arithmetic or a subsequently read local.

    This proves the input bytes, not reachability, combat meaning or eligibility.
    Computed operands and unused scratch locals fail closed. Callers must still
    supply the reviewed native consumer and its control/formula context.
    """
    body = method['instructions']
    at = next(n for n, i in enumerate(body) if i['offset'] == offset)
    assert at > 0
    value, hit = body[at-1:at+1]
    assert type(value['operand']) in (int, float)
    assert value['opcode'] in ('0x2', '0x3', '0x4', '0x5', '0x6', '0x7',
                               '0x8', '0x9', '0xa', '0xb', '0xc', '0xd',
                               '0xe', '0xf', '0x10', '0x11', '0x12', '0x13', '0x14')
    op = int(hit['opcode'], 16)
    result = dict(native_value=value['operand'], value_offset=value['offset'])
    if 0x60 <= op <= 0x73:  # Typed add/subtract/multiply/divide/remainder.
        return dict(kind='LITERAL_ARITHMETIC_INPUT', operation=hit['opcode'], **result)
    stores = {0x36: ('I', 0x15, range(0x1a, 0x1e), range(0x3b, 0x3f)),
              0x37: ('J', 0x16, range(0x1e, 0x22), range(0x3f, 0x43)),
              0x38: ('F', 0x17, range(0x22, 0x26), range(0x43, 0x47)),
              0x39: ('D', 0x18, range(0x26, 0x2a), range(0x47, 0x4b))}
    selection = next(((k, v) for k, v in stores.items() if op == k or op in v[3]), None)
    assert selection is not None, ('not a literal arithmetic/local input', hit)
    store_op, (kind, load_op, compact_loads, compact_stores) = selection
    local = hit.get('local_index')
    assert type(local) is int
    reads = []
    for instruction in body[at+1:]:
        other = int(instruction['opcode'], 16)
        if instruction.get('local_index') != local:
            continue
        if other in compact_stores or other == store_op:
            break
        if other == load_op or other in compact_loads:
            reads.append(instruction['offset'])
    assert reads, ('unused or overwritten native scratch local', hit)
    return dict(kind='READ_LOCAL_LITERAL_INPUT', local_type=kind,
                local_index=local, read_offsets=reads, **result)


def literal_item_attribute_binding(method, offset):
    """Bind exact item-modifier literals or native DiggerItem/SwordItem arguments.

    No tier bonus, inherited base value or final attack damage is inferred.
    The tier declaration/consumer must be supplied separately when relevant.
    """
    body = method['instructions']
    at = next(n for n, i in enumerate(body) if i['offset'] == offset)
    operand = body[at]['operand']
    if operand == 'net/minecraft/world/entity/ai/attributes/AttributeModifier.<init>(Lnet/minecraft/resources/ResourceLocation;DLnet/minecraft/world/entity/ai/attributes/AttributeModifier$Operation;)V':
        holder, allocation, duplicate, identifier, value, operation = body[at-6:at]
        slot, consumer = body[at+1:at+3]
        assert holder['opcode'] == '0xb2' and '/Attributes.' in str(holder['operand'])
        assert allocation['opcode'] == '0xbb' and allocation['operand'] == 'net/minecraft/world/entity/ai/attributes/AttributeModifier'
        assert duplicate['opcode'] == '0x59' and identifier['opcode'] == '0xb2'
        assert value['opcode'] in ('0xe', '0xf', '0x14') and type(value['operand']) in (int, float)
        assert operation['opcode'] == '0xb2' and '/AttributeModifier$Operation.' in str(operation['operand'])
        assert slot['opcode'] == '0xb2' and '/EquipmentSlotGroup.' in str(slot['operand'])
        assert consumer['operand'] == 'net/minecraft/world/item/component/ItemAttributeModifiers$Builder.add(Lnet/minecraft/core/Holder;Lnet/minecraft/world/entity/ai/attributes/AttributeModifier;Lnet/minecraft/world/entity/EquipmentSlotGroup;)Lnet/minecraft/world/item/component/ItemAttributeModifiers$Builder;'
        return dict(kind='ITEM_ATTRIBUTE_MODIFIER', attribute_symbol=holder['operand'],
                    modifier_id_symbol=identifier['operand'], native_value=value['operand'],
                    operation_symbol=operation['operand'], slot_symbol=slot['operand'],
                    value_offset=value['offset'], builder_offset=consumer['offset'])
    builders = {
        'net/minecraft/world/item/DiggerItem': 'DIGGER_ATTRIBUTE_ARGUMENTS',
        'net/minecraft/world/item/SwordItem': 'SWORD_ATTRIBUTE_ARGUMENTS',
    }
    kind = next((kind for owner, kind in builders.items() if operand == owner +
                 '.createAttributes(Lnet/minecraft/world/item/Tier;FF)Lnet/minecraft/world/item/component/ItemAttributeModifiers;'), None)
    assert kind is not None, ('unsupported native item attribute builder', operand)
    tier, damage, speed = body[at-3:at]
    assert tier['opcode'] == '0xb2' and tier['operand'].endswith('Lnet/minecraft/world/item/Tier;')
    for value in (damage, speed):
        assert value['opcode'] in ('0xb', '0xc', '0xd', '0x12', '0x13') and type(value['operand']) in (int, float)
    return dict(kind=kind, tier_symbol=tier['operand'],
                attack_bonus=damage['operand'], attack_speed=speed['operand'],
                damage_offset=damage['offset'], speed_offset=speed['offset'])


def registered_armor_material_binding(witness, census):
    """Read a pinned literal material registration, including its actual lambdas."""
    assert witness['superclass'] == 'net/minecraft/world/item/ArmorItem'
    methods = {m['name']: m for m in witness['methods']}
    registration = methods['registerArmorMaterial']
    assert any(a['descriptor'].endswith('/SubscribeEvent;') for a in registration['annotations'])
    assert any(a['descriptor'].endswith('/EventBusSubscriber;') and
               a['values']['bus']['constant'] == 'MOD' for a in witness['annotations'])
    bootstraps = {r['index']: r for r in census['registration_bootstraps'] if r['entry'] == witness['entry']}

    def lambda_target(instruction):
        assert instruction['opcode'] == '0xba'
        index = int(instruction['operand'].split('#')[1].split(':')[0])
        bootstrap = bootstraps[index]
        assert 'LambdaMetafactory.metafactory(' in bootstrap['handle']
        targets = [arg for arg in bootstrap['arguments'] if arg.startswith(witness['class_name'] + '.lambda$')]
        assert len(targets) == 1
        return targets[0].split('.')[-1].split('(')[0]

    body = registration['instructions']
    assert body[1]['operand'] == 'net/minecraft/core/registries/Registries.ARMOR_MATERIALLnet/minecraft/resources/ResourceKey;'
    factory = methods[lambda_target(body[2])]
    body = factory['instructions']
    assert body[0]['opcode'] == '0xbb' and body[0]['operand'] == 'net/minecraft/world/item/ArmorMaterial'
    map_method = methods[lambda_target(body[6])]
    values = {}; map_body = map_method['instructions']
    assert len(map_body) == 31 and map_body[-1]['opcode'] == '0xb1'
    for at in range(0, 30, 6):
        load, key, value, box, put, pop = map_body[at:at+6]
        assert load['opcode'] == '0x2a' and key['opcode'] == '0xb2'
        match = re.fullmatch(r'net/minecraft/world/item/ArmorItem\$Type\.(\w+)Lnet/minecraft/world/item/ArmorItem\$Type;', key['operand'])
        assert match and type(value['operand']) is int
        assert box['operand'] == 'java/lang/Integer.valueOf(I)Ljava/lang/Integer;'
        assert put['operand'] == 'java/util/EnumMap.put(Ljava/lang/Enum;Ljava/lang/Object;)Ljava/lang/Object;'
        assert pop['opcode'] == '0x57' and match[1] not in values
        values[match[1]] = value['operand']
    assert set(values) == {'BOOTS', 'LEGGINGS', 'CHESTPLATE', 'HELMET', 'BODY'}
    ctor = next(n for n, i in enumerate(body) if str(i['operand']).startswith('net/minecraft/world/item/ArmorMaterial.<init>('))
    toughness, knockback = body[ctor-2:ctor]
    assert all(i['opcode'] in ('0xb', '0xc', '0xd', '0x12', '0x13') and type(i['operand']) is float for i in (toughness, knockback))
    enchantment = body[9]; assert type(enchantment['operand']) is int
    register = next(n for n, i in enumerate(body) if 'RegisterEvent$RegisterHelper.register(' in str(i['operand']))
    registry_key = body[register-3]
    assert registry_key['opcode'] in ('0x12', '0x13') and isinstance(registry_key['operand'], str)
    holder = next(i['operand'] for i in body if i['opcode'] == '0xb3' and '.ARMOR_MATERIAL' in str(i['operand']))
    assert holder.startswith(witness['class_name'] + '.')
    assert holder in [i['operand'] for i in methods['<init>']['instructions'] if i['opcode'] == '0xb2']
    return dict(registry_key=registry_key['operand'], holder_symbol=holder,
                defense_by_native_type=dict(sorted(values.items())),
                enchantment_value=enchantment['operand'], toughness=toughness['operand'],
                knockback_resistance=knockback['operand'],
                registration_method=registration['name'], factory_method=factory['name'],
                defense_map_method=map_method['name'])


def literal_command_binding(method,offset):
    """Bind a directly authored command argument; decline computed strings."""
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert body[at]['operand']=='net/minecraft/commands/Commands.performPrefixedCommand(Lnet/minecraft/commands/CommandSourceStack;Ljava/lang/String;)V'
    argument=body[at-1]
    assert argument['opcode'] in ('0x12','0x13') and isinstance(argument['operand'],str)
    return dict(command=argument['operand'],argument_offset=argument['offset'])


def concat_command_binding(method,offset,census,entry):
    """Bind a direct StringConcatFactory command recipe to its native call.

    The finite census carries the pinned bootstrap arguments. This proves the
    authored template and dynamic argument descriptor, not command success or
    the runtime value of an interpolated argument.
    """
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert body[at]['operand']=='net/minecraft/commands/Commands.performPrefixedCommand(Lnet/minecraft/commands/CommandSourceStack;Ljava/lang/String;)V'
    argument=body[at-1]
    assert argument['opcode']=='0xba'
    match=re.fullmatch(r'bootstrap#(\d+):makeConcatWithConstants(\([^)]*\)Ljava/lang/String;)',argument['operand'])
    assert match,('not a direct native string concatenation',argument)
    bootstrap=next(b for b in census['registration_bootstraps'] if b['entry']==entry and b['index']==int(match[1]))
    assert bootstrap['handle'].startswith('java/lang/invoke/StringConcatFactory.makeConcatWithConstants(')
    assert len(bootstrap['arguments'])==1 and isinstance(bootstrap['arguments'][0],str)
    return dict(template=bootstrap['arguments'][0],argument_offset=argument['offset'],
                bootstrap_index=int(match[1]),descriptor=match[2])


def effect_receiver_binding(method,offset):
    """Trace a simple generated LivingEntity cast/local used by addEffect.

    Complex expression recipients require their own exact evidence; this helper
    deliberately refuses to infer them from a decompiler variable name.
    """
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert 'LivingEntity.addEffect(Lnet/minecraft/world/effect/MobEffectInstance;)Z' in str(body[at+1]['operand'])
    start=max(n for n,i in enumerate(body[:at]) if i['opcode']=='0xbb' and
              i['operand']=='net/minecraft/world/effect/MobEffectInstance')
    def local(i,store=False):
        op=int(i['opcode'],16)
        if op==(0x3a if store else 0x19):return i['local_index']
        low=0x4b if store else 0x2a
        assert low<=op<=low+3,('not an object local operation',i)
        return op-low
    receiver=body[start-1];receiver_local=local(receiver)
    stores=[n for n,i in enumerate(body[:start]) if
            (i['opcode']=='0x3a' or 0x4b<=int(i['opcode'],16)<=0x4e) and local(i,True)==receiver_local]
    assert stores,('recipient has no simple cast binding',receiver)
    store=stores[-1];cast=body[store-1];origin=body[store-2]
    assert cast['opcode']=='0xc0' and cast['operand'] in (
        'net/minecraft/world/entity/LivingEntity','net/minecraft/server/level/ServerPlayer')
    # Parameter expressions may branch after the recipient is already loaded
    # on the operand stack (for example, an existing amplifier plus one).
    # Entry into the guarded cast/load itself is still unsafe to infer.
    assert not any(origin['offset']<i.get('branch_target',-1)<=receiver['offset'] for i in body),('recipient cast/load is not a closed straight-line binding',origin)
    return dict(origin_local_index=local(origin),origin_load_offset=origin['offset'],
                cast_offset=cast['offset'],cast_type=cast['operand'],
                receiver_local_index=receiver_local,store_offset=body[store]['offset'],
                receiver_load_offset=receiver['offset'])


def literal_synched_int_binding(method, offset):
    """Bind only a direct boxed integer literal to its exact data accessor."""
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert body[at]['operand']=='net/minecraft/network/syncher/SynchedEntityData.set(Lnet/minecraft/network/syncher/EntityDataAccessor;Ljava/lang/Object;)V'
    accessor,value,box=body[at-3:at]
    assert accessor['opcode']=='0xb2' and accessor['operand'].endswith('Lnet/minecraft/network/syncher/EntityDataAccessor;')
    assert box['operand']=='java/lang/Integer.valueOf(I)Ljava/lang/Integer;'
    assert value['opcode'] in ('0x2','0x3','0x4','0x5','0x6','0x7','0x8','0x10','0x11','0x12','0x13') and type(value['operand']) is int
    return dict(accessor_symbol=accessor['operand'],accessor_offset=accessor['offset'],
                value_offset=value['offset'],boxing_offset=box['offset'],native_value=value['operand'])


def synched_int_distribution_binding(method, offset):
    """Bind a direct inclusive native RNG result to its exact integer accessor."""
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert body[at]['operand']=='net/minecraft/network/syncher/SynchedEntityData.set(Lnet/minecraft/network/syncher/EntityDataAccessor;Ljava/lang/Object;)V'
    accessor,source,minimum,maximum,rng,box=body[at-6:at]
    assert accessor['opcode']=='0xb2' and accessor['operand'].endswith('Lnet/minecraft/network/syncher/EntityDataAccessor;')
    assert source['operand']=='net/minecraft/util/RandomSource.create()Lnet/minecraft/util/RandomSource;'
    assert rng['operand']=='net/minecraft/util/Mth.nextInt(Lnet/minecraft/util/RandomSource;II)I'
    assert box['operand']=='java/lang/Integer.valueOf(I)Ljava/lang/Integer;'
    for value in (minimum,maximum):
        assert value['opcode'] in ('0x2','0x3','0x4','0x5','0x6','0x7','0x8','0x10','0x11','0x12','0x13') and type(value['operand']) is int
    return dict(accessor_symbol=accessor['operand'],accessor_offset=accessor['offset'],
                rng_offset=rng['offset'],boxing_offset=box['offset'],
                native_minimum=minimum['operand'],native_maximum=maximum['operand'])


def literal_vector_scale_binding(method, offset):
    """Bind one direct double coefficient, without inferring vector semantics."""
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert body[at]['operand']=='net/minecraft/world/phys/Vec3.scale(D)Lnet/minecraft/world/phys/Vec3;'
    value=body[at-1]
    assert value['opcode'] in ('0xe','0xf','0x14') and type(value['operand']) is float
    return dict(value_offset=value['offset'],native_value=value['operand'])


def subtract_tag_vector_scale_binding(method, offset):
    """Prove exactly literal - Entity persistent double; decline other formulas."""
    body = method['instructions']
    at = next(n for n, instruction in enumerate(body) if instruction['offset'] == offset)
    assert body[at]['operand'] == 'net/minecraft/world/phys/Vec3.scale(D)Lnet/minecraft/world/phys/Vec3;'
    value, entity, tag, key, read, subtract = body[at-6:at]
    assert value['opcode'] in ('0xe', '0xf', '0x14') and type(value['operand']) is float
    assert entity['opcode'] in ('0x19', '0x2a', '0x2b', '0x2c', '0x2d')
    assert tag['operand'] == 'net/minecraft/world/entity/Entity.getPersistentData()Lnet/minecraft/nbt/CompoundTag;'
    assert key['opcode'] in ('0x12', '0x13') and isinstance(key['operand'], str)
    assert read['operand'] == 'net/minecraft/nbt/CompoundTag.getDouble(Ljava/lang/String;)D'
    assert subtract['opcode'] == '0x67'
    return dict(native_value=value['operand'], value_offset=value['offset'],
                entity_local_index=entity['local_index'], tag_key=key['operand'],
                key_offset=key['offset'], read_offset=read['offset'],
                operation='NATIVE_DOUBLE_LITERAL_MINUS_CURRENT_PERSISTENT_DOUBLE')


def native_registry_spawn_binding(method, offset):
    """Identify a direct ArPhEx registry spawn; never assign it an owner."""
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert body[at]['operand']=='net/minecraft/world/entity/EntityType.spawn(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/entity/MobSpawnType;)Lnet/minecraft/world/entity/Entity;'
    start=max(n for n,i in enumerate(body[:at]) if i['opcode']=='0xb2' and
              str(i['operand']).startswith('net/arphex/init/ArphexModEntities.'))
    holder,read,cast=body[start:start+3]
    assert read['operand']=='net/neoforged/neoforge/registries/DeferredHolder.get()Ljava/lang/Object;'
    assert cast['opcode']=='0xc0' and cast['operand']=='net/minecraft/world/entity/EntityType'
    assert not any('EntityType.spawn(' in str(i['operand']) for i in body[start:at])
    reason=body[at-1]
    assert reason['opcode']=='0xb2' and reason['operand'].startswith('net/minecraft/world/entity/MobSpawnType.')
    return dict(registry_symbol=holder['operand'],registry_offset=holder['offset'],
                cast_offset=cast['offset'],spawn_reason=reason['operand'])


def arrow_factory_binding(method, offset, registry, primitive):
    """Bind a real factory call to its independently verified native scalar sink.

    The binding proves the argument role, not its value, trigger or eligibility.
    Factory kernels are validated separately against native bodies and census.
    """
    role = {'PROJECTILE_BASE_DAMAGE': 'base_damage',
            'PROJECTILE_KNOCKBACK': 'knockback'}[primitive]
    body = method['instructions']
    at = next(n for n, i in enumerate(body) if i['offset'] == offset)
    hit = body[at]
    assert hit['opcode'] == '0xb6'
    row = next(r for r in registry['rows'] if hit['operand'] ==
               r['factory']['entry'][:-6] + '.getArrow' + r['factory']['descriptor'])
    # Accept literals or the explicitly proven round(configDouble)+long pattern.
    # Other computed actor/charge expressions require their own native proof.
    arguments = body[at-3:at]
    configured = arguments[0]['opcode']=='0x89'  # long-to-float after native addition
    expression=None
    if configured:
        expression=body[at-10:at-2]
        assert len(expression)==8
        assert [i['opcode'] for i in expression[:5]]==['0xb2','0xb6','0xc0','0xb6','0xb8']
        assert expression[5]['opcode'] in ('0x9','0xa','0x14')
        assert [i['opcode'] for i in expression[-2:]]==['0x61','0x89']
        assert expression[0]['operand'].startswith('net/arphex/configuration/ConfigurationSettingsConfiguration.')
        assert expression[1]['operand']=='net/neoforged/neoforge/common/ModConfigSpec$ConfigValue.get()Ljava/lang/Object;'
        assert expression[2]['operand']=='java/lang/Double'
        assert expression[3]['operand']=='java/lang/Double.doubleValue()D'
        assert expression[4]['operand']=='java/lang/Math.round(D)J'
        assert isinstance(expression[5]['operand'],int)
    else:
        assert arguments[0]['opcode'] in ('0xb','0xc','0xd','0x12','0x13') and isinstance(arguments[0]['operand'],(int,float))
    assert all(i['opcode'] in ('0x2','0x3','0x4','0x5','0x6','0x7','0x8','0x10','0x11','0x12','0x13')
               and isinstance(i['operand'],int) for i in arguments[1:])
    literal_arguments = {name: dict(offset=i['offset'], opcode=i['opcode'], value=i['operand'])
                         for name,i in zip(('base_damage','knockback','piercing'),arguments)
                         if not (configured and name=='base_damage')}
    return dict(factory=row['factory'], owned_arrow_entry=row['owned_arrow_entry'],
                intrinsic_arrow_root=row['intrinsic_arrow_root'], parameter_role=role,
                kernel=row['factory'] if role == 'base_damage' else row['constructor'],
                literal_arguments=literal_arguments,
                **(dict(base_damage_expression=expression) if configured else {}))


def literal_tag_double_binding(method, offset):
    """Bind a directly authored raw key/value write, refusing computed values."""
    body=method['instructions'];at=next(n for n,i in enumerate(body) if i['offset']==offset)
    assert body[at]['operand']=='net/minecraft/nbt/CompoundTag.putDouble(Ljava/lang/String;D)V'
    key,value=body[at-2:at]
    assert key['opcode'] in ('0x12','0x13') and isinstance(key['operand'],str)
    assert value['opcode'] in ('0xe','0xf','0x14') and isinstance(value['operand'],(int,float))
    return dict(key=key['operand'],key_offset=key['offset'],value=value['operand'],value_offset=value['offset'])


def literal_field_numeric_binding(method, offset):
    """Bind a literal primitive field write, refusing computed or flag values."""
    body = method['instructions']
    at = next(n for n, i in enumerate(body) if i['offset'] == offset)
    hit, value = body[at], body[at-1]
    assert hit['opcode'] in ('0xb3', '0xb5') and isinstance(hit['operand'], str)
    descriptor = hit['operand'][-1]
    assert descriptor in ('I', 'F', 'D')
    opcodes = {'I': ('0x2', '0x3', '0x4', '0x5', '0x6', '0x7', '0x8', '0x10', '0x11', '0x12', '0x13'),
               'F': ('0xb', '0xc', '0xd', '0x12', '0x13'), 'D': ('0xe', '0xf', '0x14')}
    assert value['opcode'] in opcodes[descriptor]
    assert type(value['operand']) is (int if descriptor == 'I' else float)
    return dict(field=hit['operand'], native_value=value['operand'],
                value_offset=value['offset'], descriptor=descriptor,
                write='STATIC' if hit['opcode'] == '0xb3' else 'INSTANCE')


def literal_effect_command_arguments(method, offset):
    """Read an explicit effect-give literal; do not infer dynamic commands."""
    command = literal_command_binding(method, offset)['command']
    match = re.fullmatch(r'effect give (\S+) ([a-z0-9_:.]+) ([0-9]+) ([0-9]+)(?: (true|false))?', command)
    assert match, ('not an explicit literal effect-give command', offset)
    selector, effect, duration, amplifier, hidden = match.groups()
    result = dict(effect=effect, duration_seconds=int(duration), amplifier=int(amplifier),
                  hide_particles=hidden == 'true')
    if selector.startswith('@e[') and selector.endswith(']'):
        distances = [v.split('=', 1)[1] for v in selector[3:-1].split(',')
                     if v.startswith('distance=')]
        if distances:
            assert len(distances) == 1
            radius = re.fullmatch(r'\.\.([0-9]+(?:\.[0-9]+)?)', distances[0])
            assert radius, ('unsupported literal distance bound', selector)
            result['selector_distance_max'] = float(radius.group(1))
    return result


def refined_review(review,batch):
    """Apply explicit additive contracts to their existing mechanic identity."""
    result=deepcopy(review);by_id={r['id']:r for r in result['effects']};seen=set()
    for change in batch.get('record_refinements',[]):
        rid=change['id'];assert rid in by_id and rid not in seen,('unknown/duplicate refinement',rid)
        assert change['reason'] and change['behavior_append'];seen.add(rid);row=by_id[rid]
        updates=change.get('field_updates',{})
        assert set(updates)<= {'display_name','primary_classification','classification_reason','closest_vanilla_equivalent','vanilla_differences'},('unsafe identity refinement',rid)
        replacements=change.get('behavior_replacements',[])
        gates=change.get('binary_parameter_updates',{})
        assert isinstance(replacements,list) and isinstance(gates,dict)
        assert set(gates)<=set(row['binary_parameters']),('unknown native gate refinement',rid)
        receipt=dict(checkpoint=batch['checkpoint'],reason=change['reason'])
        if receipt in row.get('contract_refinements',[]):
            # Published batches can be validated without duplicating their
            # additions. A changed or incomplete published contract fails.
            assert change['behavior_append'] in row['actual_behavior'],('missing published behavior',rid)
            assert all(row.get(k)==v for k,v in updates.items()),('changed published field',rid)
            assert all(row['binary_parameters'][k]==v for k,v in gates.items()),('changed published gate',rid)
            for replacement in replacements:
                assert replacement['before'] not in row['actual_behavior'] and replacement['after'] in row['actual_behavior'],('stale published behavior',rid)
            assert all(c in row['scalable_parameter_candidates'] for c in change.get('candidate_additions',[])),('missing published candidate',rid)
            assert all(p in row['implementation'] for p in change.get('implementation_additions',[])),('missing published proof',rid)
            for c in change.get('component_additions',[]):
                target=next(t for t in row['components'] if t['primitive']==c['primitive'])
                for key,values in c.items():
                    if key!='primitive':assert all(target[key].get(k)==v for k,v in values.items()),('changed published parameter',rid,key)
            continue
        for replacement in replacements:
            before,after=replacement['before'],replacement['after']
            assert before and after and before!=after
            assert row['actual_behavior'].count(before)==1,('missing/ambiguous behavior replacement',rid)
            row['actual_behavior']=row['actual_behavior'].replace(before,after,1)
        row['actual_behavior']+=' '+change['behavior_append']
        row.setdefault('contract_refinements',[]).append(receipt)
        row.update(deepcopy(updates))
        row['binary_parameters'].update(deepcopy(gates))
        for component in change.get('component_additions',[]):
            matches=[c for c in row['components'] if c['primitive']==component['primitive']]
            assert len(matches)<=1,('ambiguous component refinement',rid,component)
            if not matches:row['components'].append(deepcopy(component));continue
            for key,values in component.items():
                if key=='primitive':continue
                assert isinstance(values,dict),('non-additive component field',key)
                old=matches[0].setdefault(key,{})
                assert not set(old)&set(values),('component parameter would be overwritten',rid,key)
                old.update(deepcopy(values))
        row['scalable_parameter_candidates']+=deepcopy(change.get('candidate_additions',[]))
        for proof in change.get('implementation_additions',[]):
            if proof not in row['implementation']:row['implementation'].append(deepcopy(proof))
        row['native_boundary']=[dict(entry=p['entry'],methods=p['methods']) for p in row['implementation']]
        for pid in change.get('delivery_path_additions',[]):
            assert pid not in row['delivery_paths'];row['delivery_paths'].append(pid)
    return result


def validate_batch(batch,review,census):
    assert batch['mod_key']==review['mod_key']==census['mod_key']
    native={(r['entry'],r['method'],r['descriptor']):r for r in census['methods']}
    index=EvidenceIndex();ids={r['id'] for r in review['effects']}
    candidates=set()
    refined=refined_review(review,batch)
    changes={c['id']:c for c in batch.get('record_refinements',[])}
    canonical_ids=ids|{r['id'] for r in batch['effects']}
    for row in refined['effects']+batch['effects']:
        for reused in row.get('canonical_contract_reuse',[]):
            assert reused in canonical_ids and reused!=row['id'],('unknown/self canonical reuse',row['id'],reused)
    refined_rows=[dict(r,scalable_parameter_candidates=changes[r['id']].get('candidate_additions',[]))
                  for r in refined['effects'] if r['id'] in changes]
    for row in batch['effects']+refined_rows:
        if row['id'] in changes:
            assert row['id'] in ids and row not in batch['effects'],('refinement collides with new record',row['id'])
        else:
            assert row['id'] not in ids,('existing semantic record must be reused',row['id'])
            ids.add(row['id'])
        assert row['actual_behavior'] and row['source_actor'] and row['native_boundary']
        for proof in row['implementation']+row.get('shared_contracts',[]):
            _,w=index.witness(proof,row)
            for m in w.get('methods',[]):
                if m['name'] in proof['methods']:
                    if proof.get('evidence_format') in ('VANILLA_COMPARISON','SHARED_NATIVE_REFERENCE'):
                        continue
                    key=(proof['entry'],m['name'],m['descriptor'])
                    assert native[key]['code_sha256']==m['code_sha256'],('unindexed native contract',key)
        material_keys = set()
        for profile in row.get('native_armor_material_profiles', []):
            _, witness = index.witness(profile['proof'], row)
            binding = registered_armor_material_binding(witness, census)
            assert binding == profile['binding'], ('wrong pinned armor material profile', profile)
            assert binding['registry_key'] not in material_keys
            material_keys.add(binding['registry_key'])
        for candidate in row['scalable_parameter_candidates']:
            consumer=candidate['native_consumer']
            _,w=index.witness(consumer,row)
            m=next(m for m in w['methods'] if m['name']==consumer['methods'][0] and m['descriptor']==consumer['descriptor'])
            hit=next(i for i in m['instructions'] if i['offset']==consumer['offset'])
            assert hit['operand']==consumer['operand'],('detached native parameter',row['id'],candidate)
            assert hit['opcode']==consumer['opcode']
            expected=dict(entry=consumer['entry'],method=consumer['methods'][0],
                          descriptor=consumer['descriptor'],offset=consumer['offset'])
            assert candidate['native_parameter_identity']==expected,('identity differs from consumer',candidate)
            scalar_sinks=('MobEffectInstance.<init>(','.hurt(','.heal(','.setHealth(',
                'AttributeInstance.setBaseValue(D)V',
                '.addEffect(','.setDeltaMovement(','.setYRot(','.setXRot(',
                '.makeStuckInBlock(','.putDouble(','.queueServerWork(','.inflate(',
                'ItemCooldowns.addCooldown(','.teleportTo(',
                '.setBaseDamage(','.shoot(','.push(','.igniteForSeconds(',
                'LivingIncomingDamageEvent.setAmount(',
                'AABB.ofSize(Lnet/minecraft/world/phys/Vec3;DDD)',
                'PathNavigation.moveTo(DDDD)')
            rng=(candidate['primitive'] in ('ATTACK_SELECTION','SUMMON_DELIVERY','PROC_CHANCE') and
                 'Mth.nextInt(' in str(hit['operand']))
            rounded_tag = 'native_rounded_tag_quotient_binding' in candidate
            if rounded_tag:
                binding = rounded_tag_quotient_binding(m, consumer['offset'])
                assert binding == candidate['native_rounded_tag_quotient_binding']
                assert len(candidate['parameters']) == 1
                component = next(c for c in row['components'] if c['primitive'] == candidate['primitive'])
                assert component['numerical_parameters'][candidate['parameters'][0]] == binding['divisor']
            food_component = 'native_food_component_binding' in candidate
            literal_numeric = 'native_literal_numeric_input_binding' in candidate
            field_literal = 'native_literal_field_numeric_binding' in candidate
            if field_literal:
                binding = literal_field_numeric_binding(m, consumer['offset'])
                assert binding == candidate['native_literal_field_numeric_binding']
                assert len(candidate['parameters']) == 1
                component = next(c for c in row['components'] if c['primitive'] == candidate['primitive'])
                assert component['numerical_parameters'][candidate['parameters'][0]] == binding['native_value']
            block_factor = 'native_block_factor_binding' in candidate
            if block_factor:
                binding = literal_block_factor_binding(m, consumer['offset'])
                assert binding == candidate['native_block_factor_binding']
                assert candidate['primitive'] == {'speedFactor': 'BLOCK_SPEED_FACTOR',
                                                  'jumpFactor': 'BLOCK_JUMP_FACTOR',
                                                  'friction': 'BLOCK_FRICTION'}[binding['property']]
                assert len(candidate['parameters']) == 1
                component = next(c for c in row['components'] if c['primitive'] == candidate['primitive'])
                assert component['numerical_parameters'][candidate['parameters'][0]] == binding['native_value'], \
                    ('component differs from native block factor', candidate)
            if 'native_literal_rng_bounds_binding' in candidate:
                assert rng
                binding = literal_rng_bounds_binding(m, consumer['offset'])
                assert binding == candidate['native_literal_rng_bounds_binding']
                roles = candidate['native_rng_parameter_roles']
                assert set(roles) == set(candidate['parameters'])
                assert set(roles.values()) <= {'minimum', 'maximum'}
                component = next(c for c in row['components'] if c['primitive'] == candidate['primitive'])
                assert all(component['numerical_parameters'][p] == binding[role]
                           for p, role in roles.items()), ('component differs from native RNG bound', candidate)
            if literal_numeric:
                binding = literal_numeric_input_binding(m, consumer['offset'])
                assert binding == candidate['native_literal_numeric_input_binding']
                assert len(candidate['parameters']) == 1
                component = next(c for c in row['components'] if c['primitive'] == candidate['primitive'])
                assert component['numerical_parameters'][candidate['parameters'][0]] == binding['native_value'], \
                    ('component differs from native numeric input', candidate)
            if food_component:
                binding = literal_food_component_binding(m, consumer['offset'])
                assert binding == candidate['native_food_component_binding']
                roles = candidate['native_food_parameter_roles']
                assert set(roles) == set(candidate['parameters'])
                assert set(roles.values()) <= {'nutrition', 'saturation_modifier'}
                component = next(c for c in row['components'] if c['primitive'] == candidate['primitive'])
                assert all(component['numerical_parameters'][p] == binding[role]
                           for p, role in roles.items()), ('component differs from native food input', candidate)
            terrain=(candidate['primitive']=='TERRAIN_PLACEMENT' and
                     hit['operand']=='net/minecraft/world/level/LevelAccessor.setBlock(Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/block/state/BlockState;I)Z')
            explosion=(candidate['primitive']=='NATIVE_EXPLOSION' and
                       hit['operand']=='net/minecraft/world/level/Level.explode(Lnet/minecraft/world/entity/Entity;DDDFLnet/minecraft/world/level/Level$ExplosionInteraction;)Lnet/minecraft/world/level/Explosion;')
            durability=(candidate['primitive']=='ITEM_DURABILITY_REPAIR' and
                        hit['operand']=='net/minecraft/world/item/ItemStack.setDamageValue(I)V')
            attribute='native_attribute_binding' in candidate
            item_attribute='native_item_attribute_binding' in candidate
            command='native_command_binding' in candidate
            if command:
                assert literal_command_binding(m,consumer['offset'])==candidate['native_command_binding'],('wrong native literal command',candidate)
                roles = candidate.get('native_literal_command_argument_roles')
                if roles:
                    assert candidate['primitive'] == 'NATIVE_STATUS_COMMAND'
                    assert set(roles) == set(candidate['parameters'])
                    arguments = literal_effect_command_arguments(m, consumer['offset'])
                    component = next(c for c in row['components'] if c['primitive'] == candidate['primitive'])
                    assert all(role in ('selector_distance_max', 'duration_seconds', 'amplifier')
                               and component['numerical_parameters'][parameter] == arguments[role]
                               for parameter, role in roles.items()), ('component differs from native command arguments', candidate)
            tag_literal='native_tag_double_binding' in candidate
            if tag_literal:
                assert literal_tag_double_binding(m,consumer['offset'])==candidate['native_tag_double_binding'],('wrong native raw-state literal',candidate)
                assert len(candidate['parameters'])==1
                component=next(c for c in row['components'] if c['primitive']==candidate['primitive'])
                assert component['numerical_parameters'][candidate['parameters'][0]]==candidate['native_tag_double_binding']['value'],('component differs from pinned raw-state literal',candidate)
            concat='native_concat_command_binding' in candidate
            if concat:
                assert concat_command_binding(m,consumer['offset'],census,consumer['entry'])==candidate['native_concat_command_binding'],('wrong native concatenated command',candidate)
            area_state=(candidate['primitive']=='NATIVE_AREA_SIZE' and hit['operand']=='net/minecraft/network/syncher/SynchedEntityData.set(Lnet/minecraft/network/syncher/EntityDataAccessor;Ljava/lang/Object;)V')
            block_speed=(candidate['primitive']=='BLOCK_SPEED_FACTOR' and hit['operand']=='net/minecraft/world/level/block/state/BlockBehaviour$Properties.speedFactor(F)Lnet/minecraft/world/level/block/state/BlockBehaviour$Properties;')
            hazard_timer=(candidate['primitive']=='NATIVE_HAZARD_LIFECYCLE' and hit['operand'] in ('net/minecraft/world/level/Level.scheduleTick(Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/block/Block;I)V','net/minecraft/server/level/ServerLevel.scheduleTick(Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/block/Block;I)V'))
            projectile_placement=(candidate['primitive']=='PROJECTILE_PLACEMENT' and hit['operand']=='net/minecraft/world/entity/projectile/Projectile.setPos(DDD)V')
            body_dimensions=(candidate['primitive']=='BODY_DIMENSION_SCALE' and hit['operand']=='net/minecraft/world/entity/EntityDimensions.scale(F)Lnet/minecraft/world/entity/EntityDimensions;')
            synched_clock='native_synched_int_binding' in candidate
            if synched_clock:
                assert candidate['primitive'] in ('ATTACK_CADENCE','CONTROL_CADENCE','NATIVE_HAZARD_MAX_SIZE') and len(candidate['parameters'])==1
                binding=literal_synched_int_binding(m,consumer['offset'])
                assert binding==candidate['native_synched_int_binding']
                component=next(c for c in row['components'] if c['primitive']==candidate['primitive'])
                assert component['numerical_parameters'][candidate['parameters'][0]]==binding['native_value']
            clock_distribution='native_synched_int_distribution_binding' in candidate
            if clock_distribution:
                assert candidate['primitive'] in ('NATIVE_CLOCK_DISTRIBUTION','NATIVE_AREA_SIZE') and candidate['parameters']==['minimum','maximum']
                binding=synched_int_distribution_binding(m,consumer['offset'])
                assert binding==candidate['native_synched_int_distribution_binding']
                component=next(c for c in row['components'] if c['primitive']==candidate['primitive'])
                assert component['numerical_parameters']['minimum']==binding['native_minimum']
                assert component['numerical_parameters']['maximum']==binding['native_maximum']
            vector_scale='native_vector_scale_binding' in candidate
            if vector_scale:
                assert len(candidate['parameters'])==1
                binding=literal_vector_scale_binding(m,consumer['offset'])
                assert binding==candidate['native_vector_scale_binding']
                component=next(c for c in row['components'] if c['primitive']==candidate['primitive'])
                assert component['numerical_parameters'][candidate['parameters'][0]]==binding['native_value']
            vector_expression = 'native_subtract_tag_vector_binding' in candidate
            if vector_expression:
                assert candidate['primitive'] == 'NATIVE_RAY_DELIVERY' and len(candidate['parameters']) == 1
                binding = subtract_tag_vector_scale_binding(m, consumer['offset'])
                assert binding == candidate['native_subtract_tag_vector_binding']
                component = next(c for c in row['components'] if c['primitive'] == candidate['primitive'])
                assert component['numerical_parameters'][candidate['parameters'][0]] == binding['native_value'], \
                    ('component differs from pinned ray base', candidate)
            registry_spawn='native_registry_spawn_binding' in candidate
            if registry_spawn:
                assert candidate['primitive']=='SUMMON_DELIVERY'
                assert native_registry_spawn_binding(m,consumer['offset'])==candidate['native_registry_spawn_binding']
            handoff='native_callee_binding' in candidate
            if handoff:
                assert candidate['primitive'] in ('TERRAIN_DELIVERY','SUMMON_DELIVERY','CONTROL_DELIVERY') and hit['opcode']=='0xb8'
                callee=candidate['native_callee_binding']
                assert hit['operand']==callee['entry'][:-6]+'.'+callee['method']+callee['descriptor']
                assert callee['descriptor'].endswith(')V') and callee['entry'].startswith(consumer['entry'].split('/')[0]+'/'+consumer['entry'].split('/')[1]+'/')
                assert native[(callee['entry'],callee['method'],callee['descriptor'])]['code_sha256']==callee['code_sha256']
                proofs=[p for p in row['implementation']+row.get('shared_contracts',[]) if p['entry']==callee['entry'] and callee['method'] in p['methods']]
                assert proofs,('owned handoff has no independent callee witness',callee)
                _,cw=index.witness(proofs[0],row)
                assert any(cm['name']==callee['method'] and cm['descriptor']==callee['descriptor'] and cm['code_sha256']==callee['code_sha256'] for cm in cw['methods'])
            arrow_factory='native_arrow_factory_binding' in candidate
            if arrow_factory:
                assert len(candidate['parameters'])==1,('one literal factory argument is one parameter',candidate)
                component=next(c for c in row['components'] if c['primitive']==candidate['primitive'])
                sites=[dict(offset=consumer['offset'],binding=candidate['native_arrow_factory_binding'])]+candidate.get('additional_arrow_factory_sites',[])
                assert len({(s.get('method',m['name']),s.get('descriptor',m['descriptor']),s['offset']) for s in sites})==len(sites),('duplicate factory argument site',candidate)
                for site in sites:
                    source_method=m
                    if 'method' in site or 'descriptor' in site:
                        # Additional sites stay in the independently witnessed source
                        # class. A captured lambda is not interchangeable with its caller.
                        assert 'method' in site and 'descriptor' in site
                        source_method=next(sm for sm in w['methods'] if
                            (sm['name'],sm['descriptor'])==(site['method'],site['descriptor']))
                        assert native[(consumer['entry'],source_method['name'],source_method['descriptor'])]['code_sha256']==source_method['code_sha256']
                    binding=site['binding'];registry=read_json(OUT/binding['registry_file'])
                    expected_binding=arrow_factory_binding(source_method,site['offset'],registry,candidate['primitive'])
                    assert binding==dict(registry_file=binding['registry_file'],**expected_binding),('wrong native arrow factory binding',candidate)
                    parameter=candidate['parameters'][0]
                    if binding['parameter_role']=='base_damage' and 'base_damage_expression' in binding:
                        assert parameter in component['parameter_formulas'],('computed factory argument lacks native formula',candidate)
                    else:
                        assert component['numerical_parameters'][parameter]==binding['literal_arguments'][binding['parameter_role']]['value'],('wrong factory argument value',candidate)
                    for proof in (binding['factory'],binding['kernel']):
                        key=(proof['entry'],proof['method'],proof['descriptor'])
                        assert native[key]['code_sha256']==proof['code_sha256']
                        matches=[p for p in row['implementation']+row.get('shared_contracts',[]) if p['entry']==proof['entry'] and proof['method'] in p['methods']]
                        assert matches,('factory scalar sink lacks independent witness',proof)
                        _,cw=index.witness(matches[0],row)
                        assert any(cm['name']==proof['method'] and cm['descriptor']==proof['descriptor'] and cm['code_sha256']==proof['code_sha256'] for cm in cw['methods'])
            if attribute:
                assert literal_attribute_binding(m,consumer['offset'])==candidate['native_attribute_binding'],('wrong native attribute literal',candidate)
                assert len(candidate['parameters'])==1,('one native attribute literal is one parameter',candidate)
                component=next(c for c in row['components'] if c['primitive']==candidate['primitive'])
                parameter=candidate['parameters'][0]
                assert component['numerical_parameters'][parameter]==candidate['native_attribute_binding']['native_value'],('component differs from pinned native attribute',candidate)
            if item_attribute:
                binding=literal_item_attribute_binding(m,consumer['offset'])
                assert binding==candidate['native_item_attribute_binding'],('wrong native item attribute',candidate)
                assert candidate['primitive']=='NATIVE_WEAPON_ATTRIBUTES'
                component=next(c for c in row['components'] if c['primitive']==candidate['primitive'])
                roles=candidate['native_item_attribute_parameter_roles']
                assert set(roles)==set(candidate['parameters'])
                allowed={'native_value'} if binding['kind']=='ITEM_ATTRIBUTE_MODIFIER' else {'attack_bonus','attack_speed'}
                assert set(roles.values())==allowed and len(roles)==len(allowed)
                assert all(component['numerical_parameters'][parameter]==binding[role] for parameter,role in roles.items()),('component differs from pinned item attribute',candidate)
            assert hit['opcode']=='0xb5' or field_literal or block_factor or literal_numeric or food_component or rounded_tag or rng or terrain or explosion or durability or attribute or item_attribute or command or concat or area_state or block_speed or hazard_timer or projectile_placement or body_dimensions or synched_clock or clock_distribution or vector_scale or vector_expression or registry_spawn or handoff or arrow_factory or any(s in str(hit['operand']) for s in scalar_sinks),('not a native scalar consumer',consumer)
            if candidate['primitive'].startswith('MOB_EFFECT_') or 'native_holder_symbol' in candidate:
                symbol,allocation,load=effect_holder_binding(m,consumer['offset'])
                assert (symbol,allocation,load)==(candidate['native_holder_symbol'],
                    candidate['native_holder_allocation_offset'],candidate['native_holder_load_offset'])
            if 'native_damage_type_symbol' in candidate:
                assert damage_source_binding(m,consumer['offset'])==(
                    candidate['native_damage_type_symbol'],candidate['native_damage_source_allocation_offset'],
                    candidate['native_damage_source_constructor_offset'],candidate['native_damage_source_constructor'])
            if 'native_damage_actor_local_index' in candidate:
                assert direct_damage_actor_local(m, consumer['offset']) == candidate['native_damage_actor_local_index'], \
                    ('wrong native damage actor slot', candidate)
            if 'native_receiver_binding' in candidate:
                assert effect_receiver_binding(m,consumer['offset'])==candidate['native_receiver_binding'],('wrong native recipient binding',candidate)
            literal_effect = 'native_literal_effect_arguments' in candidate
            if literal_effect:
                binding = literal_effect_arguments(m, consumer['offset'])
                assert binding == candidate['native_literal_effect_arguments'], ('wrong native status literals', candidate)
                component = next(c for c in row['components'] if c['primitive'] == candidate['primitive'])
                assert set(candidate['parameters']) <= {'duration', 'amplifier'}
                assert all(component['numerical_parameters'][p] == binding[p]
                           for p in candidate['parameters']), ('component differs from native status literals', candidate)
            seen={tuple(expected[k] for k in ('entry','method','descriptor','offset'))}
            for site in candidate.get('additional_consumer_sites',[]):
                identity=tuple(site[k] for k in ('entry','method','descriptor','offset'))
                assert identity not in seen,('duplicate auxiliary site',identity)
                seen.add(identity)
                other_proof=dict(consumer,entry=site['entry'],methods=[site['method']],descriptor=site['descriptor'])
                if site['entry']!=consumer['entry']:
                    assert 'evidence_file' in site and 'witness_id' in site,('cross-class site lacks its own proof',site)
                for key in ('evidence_file','witness_id'):
                    if key in site:other_proof[key]=site[key]
                _,other=index.witness(other_proof,row)
                other_method=next(x for x in other['methods'] if x['name']==site['method'] and x['descriptor']==site['descriptor'])
                other_hit=next(i for i in other_method['instructions'] if i['offset']==site['offset'])
                assert other_hit['operand']==hit['operand'],('auxiliary site uses a different consumer',site)
                if candidate['primitive'].startswith('MOB_EFFECT_') or 'native_holder_symbol' in candidate:
                    assert effect_holder_binding(other_method,site['offset'])[0]==candidate['native_holder_symbol']
                if 'native_damage_type_symbol' in candidate:
                    source=damage_source_binding(other_method,site['offset'])
                    assert (source[0],source[3])==(candidate['native_damage_type_symbol'],candidate['native_damage_source_constructor']),('auxiliary source identity differs',site)
                if 'native_damage_actor_local_index' in candidate:
                    assert 'native_damage_actor_local_index' in site
                    assert direct_damage_actor_local(other_method, site['offset']) == site['native_damage_actor_local_index'], \
                        ('wrong auxiliary damage actor slot', site)
                if attribute:
                    other_binding=literal_attribute_binding(other_method,site['offset'])
                    assert (other_binding['attribute_symbol'],other_binding['native_value'])==(
                        candidate['native_attribute_binding']['attribute_symbol'],
                        candidate['native_attribute_binding']['native_value']),('auxiliary attribute literal differs',site)
                if item_attribute:
                    assert literal_item_attribute_binding(other_method,site['offset'])==candidate['native_item_attribute_binding'],('auxiliary item attribute differs',site)
                if command:
                    other_command=literal_command_binding(other_method,site['offset'])
                    shared=candidate.get('native_shared_command_tokens')
                    if shared:
                        # Different native commands may consume one explicitly
                        # authored coefficient. Prove only those numeric tokens;
                        # preserve every full command and its distinct gates.
                        assert other_command==site['native_command_binding']
                        assert set(shared)==set(candidate['parameters'])
                        primary_tokens=candidate['native_command_binding']['command'].split()
                        other_tokens=other_command['command'].split()
                        component=next(c for c in row['components'] if c['primitive']==candidate['primitive'])
                        for parameter,role in shared.items():
                            positions=role['indices'];assert positions and all(type(n) is int and n>=0 for n in positions)
                            tokens=[primary_tokens[n] for n in positions]
                            assert tokens==[other_tokens[n] for n in positions],('shared command coefficient differs',site,parameter)
                            assert all(re.fullmatch(r'[~^]?-?(?:\d+(?:\.\d*)?|\.\d+)',t) for t in tokens)
                            values=[float(t.lstrip('~^')) for t in tokens]
                            if role.get('absolute',False):
                                assert candidate['primitive']=='TERRAIN_COMMAND' and parameter=='half_extent'
                                assert positions==[1,2,3,4,5,6] and primary_tokens[0]=='fill'
                                assert primary_tokens[7:9]==['air','replace'] and other_tokens[0]=='fill' and other_tokens[7:9]==['air','replace']
                                values=[abs(v) for v in values]
                            assert all(v==component['numerical_parameters'][parameter] for v in values)
                    else:
                        assert other_command['command']==candidate['native_command_binding']['command'],('auxiliary command literal differs',site)
                if vector_scale:
                    assert literal_vector_scale_binding(other_method,site['offset'])['native_value']==candidate['native_vector_scale_binding']['native_value'],('auxiliary vector coefficient differs',site)
                if literal_effect:
                    assert literal_effect_arguments(other_method, site['offset']) == candidate['native_literal_effect_arguments'], ('auxiliary status literals differ', site)
                if vector_expression:
                    binding = subtract_tag_vector_scale_binding(other_method, site['offset'])
                    expected = candidate['native_subtract_tag_vector_binding']
                    assert all(binding[key] == expected[key] for key in ('native_value', 'entity_local_index', 'tag_key', 'operation')), \
                        ('auxiliary ray expression differs', site)
                if tag_literal:
                    other_binding=literal_tag_double_binding(other_method,site['offset'])
                    assert (other_binding['key'],other_binding['value'])==(candidate['native_tag_double_binding']['key'],candidate['native_tag_double_binding']['value']),('auxiliary raw-state literal differs',site)
                if concat:
                    assert concat_command_binding(other_method,site['offset'],census,site['entry'])['template']==candidate['native_concat_command_binding']['template'],('auxiliary command recipe differs',site)
            for parameter in candidate['parameters']:
                identity=tuple(candidate['native_parameter_identity'][k] for k in ('entry','method','descriptor','offset'))+(candidate['primitive'],parameter)
                assert identity not in candidates,('same native parameter counted twice',identity)
                candidates.add(identity)
    merged=refined
    merged['effects']+=batch['effects'];merged['paths']+=batch['paths']
    return audit_review(merged,index)


def promote(batch_path):
    batch=read_json(batch_path);key=batch['mod_key']
    review=read_json(OUT/'mod-reviews'/f'{key}.json')
    census=read_json(OUT/f'{key}-combat-census.json')
    summary=validate_batch(batch,review,census)
    review=refined_review(review,batch)
    review['effects']=sorted(review['effects']+batch['effects'],key=lambda r:r['id'])
    review['paths']=sorted(review['paths']+batch['paths'],key=lambda r:r['id'])
    review.update(checkpoint=batch['checkpoint'],notes_file=batch_path.name,
        scope=batch['closed_scope'],exact_next_task=batch['exact_next_task'])
    review.setdefault('reviewed_batches',[]).append(batch_path.name)
    write_json(OUT/'mod-reviews'/f'{key}.json',review)
    ledger=read_json(OUT/'mod-completion-ledger.json')
    ledger.update(checkpoint=batch['checkpoint'],exact_next_task=batch['exact_next_task'])
    target=next(t for t in ledger['targets'] if t['mod_key']==key)
    target.update(state='PARTIAL',detail=batch['closed_scope']+' Other finite census contracts remain pending.',
        exact_next_task=batch['exact_next_task'],semantic_effect_count=summary['semantic_records'],
        numeric_candidate_count=summary['numeric_candidate_entries'])
    write_json(OUT/'mod-completion-ledger.json',ledger)
    campaign=read_json(OUT/'large-mod-campaign.json')
    campaign.update(checkpoint=batch['checkpoint'],exact_next_task=batch['exact_next_task'])
    campaign.setdefault('closed_batches',[]).append(dict(file=batch_path.name,mod_key=key,
        semantic_records_added=len(batch['effects']),classification_counts=dict(sorted(Counter(r['primary_classification'] for r in batch['effects']).items()))))
    write_json(OUT/'large-mod-campaign.json',campaign)
    decision=read_json(OUT/'research-decision.json')
    decision.update(checkpoint=batch['checkpoint'],next_task=batch['exact_next_task'],
        large_mod_campaign_file='large-mod-campaign.json')
    write_json(OUT/'research-decision.json',decision)
    refresh()
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('batch',type=__import__('pathlib').Path)
    print(promote(parser.parse_args().batch))
