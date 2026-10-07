"""Prove narrow native forwarding/context shapes from an existing finite queue.

No names, keyword absence or capture-only witness can establish an exclusion.
Bridges require a previously dispositioned concrete target. Context constructors
must call only Object.<init>; empty helpers must be static void methods. Distance
ordering factories require their exact pure native query lambda, including the
resolved bootstrap. Callers' admission, ordering and payloads remain separate.
"""
import argparse
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from catalog_common import OUT, read_json, write_json, sha256, byte_hash
from classfile import ClassFile
from native_evidence import annotate_local_operands


def signature(descriptor):
    match=re.fullmatch(r'\((.*?)\)(.+)',descriptor)
    assert match
    args=re.findall(r'\[*(?:L[^;]+;|[BCDFIJSZ])',match[1])
    assert ''.join(args)==match[1]
    ret=match[2]
    assert re.fullmatch(r'V|\[*(?:L[^;]+;|[BCDFIJSZ])',ret)
    return args,ret


def kind(t):
    return 'A' if t.startswith(('L','[')) else 'I' if t in 'BCISZ' else t


def distance_query_shape(entry, descriptor, access, body, bootstraps):
    """Two exact query-only shapes; never infer purity from a method name."""
    entity='net/minecraft/world/entity/Entity'
    query_descriptor='(DDDL'+entity+';)D'
    ops=[i['opcode'] for i in body]
    if descriptor==query_descriptor and access & 8:
        if ops!=['0x19','0x26','0x28','0x18','0xb6','0xaf']:return None
        if [body[j].get('local_index') for j in (0,1,2,3)]!=[6,0,2,4]:return None
        if body[4]['operand']!=entity+'.distanceToSqr(DDD)D':return None
        return dict(kind='EXACT_NATIVE_DISTANCE_QUERY')
    if descriptor!='(DDD)Ljava/util/Comparator;' or access & 8:return None
    if ops!=['0x27','0x29','0x18','0xba','0xb8','0xb0']:return None
    if [body[j].get('local_index') for j in (0,1,2)]!=[1,3,5]:return None
    if body[4]['operand']!='java/util/Comparator.comparingDouble(Ljava/util/function/ToDoubleFunction;)Ljava/util/Comparator;':return None
    match=re.fullmatch(r'bootstrap#([0-9]+):applyAsDouble\(DDD\)Ljava/util/function/ToDoubleFunction;',body[3]['operand'])
    if not match:return None
    number=match[1]
    if set(bootstraps)!={number}:return None
    bootstrap=bootstraps[number]
    expected_handle=dict(tag=15,value='java/lang/invoke/LambdaMetafactory.metafactory(Ljava/lang/invoke/MethodHandles$Lookup;Ljava/lang/String;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodHandle;Ljava/lang/invoke/MethodType;)Ljava/lang/invoke/CallSite;',reference_kind=6)
    if bootstrap.get('handle')!=expected_handle:return None
    args=bootstrap.get('arguments',[])
    if len(args)!=3 or args[0]!=dict(tag=16,value='(Ljava/lang/Object;)D') or args[2]!=dict(tag=16,value='(L'+entity+';)D'):return None
    target=args[1]
    if set(target)!={'tag','value','reference_kind'} or target['tag']!=15 or target['reference_kind']!=6:return None
    method=re.fullmatch(r'SELF\.([^.(]+)'+re.escape(query_descriptor),target['value'])
    if not method:return None
    return dict(kind='EXACT_NATIVE_DISTANCE_COMPARATOR_FACTORY',target=dict(entry=entry,method=method[1],descriptor=query_descriptor))


def asset_query_shape(name, descriptor, access, body, superclass):
    """Exact constant GeckoLib model assets, not arbitrary resource/gate queries."""
    if superclass!='software/bernie/geckolib/model/GeoModel':return None
    roots={'getAnimationResource':('animations/','.animation.json'),
           'getModelResource':('geo/','.geo.json'),
           'getTextureResource':('textures/','.png')}
    if name not in roots or access & 8:return None
    args,ret=signature(descriptor)
    if len(args)!=1 or kind(args[0])!='A' or ret!='Lnet/minecraft/resources/ResourceLocation;':return None
    if len(body)!=3 or body[0]['opcode'] not in ('0x12','0x13') or body[1]['opcode']!='0xb8' or body[2]['opcode']!='0xb0':return None
    if body[1]['operand']!='net/minecraft/resources/ResourceLocation.parse(Ljava/lang/String;)Lnet/minecraft/resources/ResourceLocation;':return None
    identifier=body[0]['operand']
    if not isinstance(identifier,str) or not re.fullmatch(r'[a-z0-9_.-]+:[a-z0-9_./-]+',identifier):return None
    namespace,path=identifier.split(':',1);prefix,suffix=roots[name]
    if not path.startswith(prefix) or not path.endswith(suffix) or '..' in path.split('/'):return None
    return dict(kind='EXACT_GECKO_MODEL_ASSET_QUERY',asset_identifier=identifier)


def presentation_leaf_shape(entry, name, descriptor, access, body, superclass):
    """Exact public API leaves, not arbitrary constant gates or field getters."""
    if access & 8:return None
    ops=[i['opcode'] for i in body]
    sounds={'getAmbientSound':'()Lnet/minecraft/sounds/SoundEvent;',
            'getDeathSound':'()Lnet/minecraft/sounds/SoundEvent;',
            'getHurtSound':'(Lnet/minecraft/world/damagesource/DamageSource;)Lnet/minecraft/sounds/SoundEvent;'}
    if sounds.get(name)==descriptor and ops[:1]==['0xb2'] and len(body)==6 \
            and body[1]['opcode'] in ('0x12','0x13') and ops[2:]==['0xb8','0xb9','0xc0','0xb0'] \
            and body[0]['operand']=='net/minecraft/core/registries/BuiltInRegistries.SOUND_EVENTLnet/minecraft/core/Registry;' \
            and body[2]['operand']=='net/minecraft/resources/ResourceLocation.parse(Ljava/lang/String;)Lnet/minecraft/resources/ResourceLocation;' \
            and body[3]['operand']=='net/minecraft/core/Registry.get(Lnet/minecraft/resources/ResourceLocation;)Ljava/lang/Object;' \
            and body[4]['operand']=='net/minecraft/sounds/SoundEvent' \
            and isinstance(body[1]['operand'],str) \
            and re.fullmatch(r'(?:[a-z0-9_.-]+:)?[a-z0-9_./-]+',body[1]['operand']):
        return dict(kind='EXACT_NATIVE_SOUND_REGISTRY_QUERY',sound_identifier=body[1]['operand'])
    cache='Lsoftware/bernie/geckolib/animatable/instance/AnimatableInstanceCache;'
    if name=='getAnimatableInstanceCache' and descriptor=='()'+cache and ops==['0x2a','0xb4','0xb0'] \
            and re.fullmatch(re.escape(entry[:-6])+r'\.[^.]+?'+re.escape(cache),str(body[1]['operand'])):
        return dict(kind='EXACT_GECKO_ANIMATION_CACHE_QUERY',cache_field=body[1]['operand'])
    args,ret=signature(descriptor)
    if superclass=='software/bernie/geckolib/renderer/GeoEntityRenderer' and name=='getDeathMaxRotation' \
            and len(args)==1 and kind(args[0])=='A' and ret=='F' and len(body)==2 \
            and body[0]['opcode'] in ('0xb','0xc','0xd','0x12','0x13') and body[1]['opcode']=='0xae' \
            and type(body[0]['operand']) in (int,float):
        return dict(kind='EXACT_GECKO_DEATH_RENDER_ROTATION',render_degrees=body[0]['operand'])
    tooltip='(Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/item/Item$TooltipContext;Ljava/util/List;Lnet/minecraft/world/item/TooltipFlag;)V'
    parents={'net/minecraft/world/level/block/Block'}|{'net/minecraft/world/item/'+n for n in
        ('Item','SwordItem','ArmorItem','BowItem','CrossbowItem','TridentItem','ShieldItem','TieredItem','PickaxeItem')}
    if name=='appendHoverText' and descriptor==tooltip and superclass in parents and len(body)>=12 \
            and ops[:6]==['0x2a','0x2b','0x2c','0x2d','0x19','0xb7'] \
            and [body[j].get('local_index') for j in range(5)]==list(range(5)) \
            and body[5]['operand']==superclass+'.appendHoverText'+tooltip and ops[-1]=='0xb1':
        tail=body[6:-1]
        if len(tail)%5==0 and all(
                chunk[0]['opcode']=='0x2d' and chunk[0].get('local_index')==3 \
                and chunk[1]['opcode'] in ('0x12','0x13') and isinstance(chunk[1]['operand'],str) \
                and chunk[2]['opcode']=='0xb8' and chunk[2]['operand']=='net/minecraft/network/chat/Component.literal(Ljava/lang/String;)Lnet/minecraft/network/chat/MutableComponent;' \
                and chunk[3]['opcode']=='0xb9' and chunk[3]['operand']=='java/util/List.add(Ljava/lang/Object;)Z' \
                and chunk[4]['opcode']=='0x57' for chunk in (tail[j:j+5] for j in range(0,len(tail),5))):
            return dict(kind='EXACT_NATIVE_LITERAL_TOOLTIP',tooltip_lines=[tail[j+1]['operand'] for j in range(0,len(tail),5)])
    return None


def forwarding_shape(entry, name, descriptor, access, body, exception_handlers=(), bootstraps=None, superclass=None):
    """Return an exact proof shape or None; do not establish target coverage."""
    if exception_handlers:return None
    from native_animation_shapes import animation_shape
    animation=animation_shape(entry,name,descriptor,access,body,bootstraps or {},superclass)
    if animation:return animation
    from native_particle_shapes import particle_shape
    particle=particle_shape(entry,name,descriptor,access,body,superclass)
    if particle and not bootstraps:return particle
    # Only compiler-generated, static one-reference predicates. A public/native
    # admission callback returning a constant is deliberately not covered here.
    # The caller's query/admission and its unconditional predicate remain native.
    args,ret=signature(descriptor)
    ops=[i['opcode'] for i in body]
    if access & 0x1008 == 0x1008 and len(args)==1 and kind(args[0])=='A' \
            and ret=='Z' and ops==['0x4','0xac'] and body[0]['operand']==1:
        return dict(kind='EXACT_SYNTHETIC_TRUE_PREDICATE')
    if access & 8 and descriptor=='(Lnet/minecraft/world/phys/Vec3;Lnet/minecraft/world/entity/Entity;)D' \
            and ops==['0x2b','0x2a','0xb6','0xaf'] \
            and [body[j].get('local_index') for j in (0,1)]==[1,0] \
            and body[2]['operand']=='net/minecraft/world/entity/Entity.distanceToSqr(Lnet/minecraft/world/phys/Vec3;)D':
        return dict(kind='EXACT_NATIVE_VEC3_DISTANCE_QUERY')
    asset=asset_query_shape(name,descriptor,access,body,superclass)
    if asset:return asset
    presentation=presentation_leaf_shape(entry,name,descriptor,access,body,superclass)
    if presentation:return presentation
    query=distance_query_shape(entry,descriptor,access,body,bootstraps or {})
    if query:return query
    ops=[i['opcode'] for i in body]
    if access & 8 and descriptor.endswith(')V') and ops==['0xb1']:
        return dict(kind='EMPTY_STATIC_VOID_HELPER')
    if name=='<init>' and descriptor=='()V' and ops==['0x2a','0xb7','0xb1'] \
            and body[1]['operand']=='java/lang/Object.<init>()V':
        return dict(kind='OBJECT_ONLY_CONTEXT_CONSTRUCTOR')
    if access & 0x1040 != 0x1040 or access & 8 or len(body)<3:return None
    call=body[-2]
    if call['opcode']!='0xb6' or not isinstance(call['operand'],str):return None
    owner=entry[:-6]
    prefix=owner+'.'+name
    if not call['operand'].startswith(prefix+'('):return None
    target_desc=call['operand'][len(prefix):]
    if target_desc==descriptor:return None
    args,ret=signature(descriptor); target_args,target_ret=signature(target_desc)
    if len(args)!=len(target_args) or kind(ret)!=kind(target_ret):return None
    returns={'V':'0xb1','I':'0xac','J':'0xad','F':'0xae','D':'0xaf','A':'0xb0'}
    if body[-1]['opcode']!=returns.get(kind(ret)):return None
    before=body[:-2]
    if before[0]['opcode']!='0x2a':return None
    at=1;slot=1
    loads={'I':range(0x1a,0x1e),'J':range(0x1e,0x22),'F':range(0x22,0x26),
           'D':range(0x26,0x2a),'A':range(0x2a,0x2e)}
    generic={'I':'0x15','J':'0x16','F':'0x17','D':'0x18','A':'0x19'}
    for source,target in zip(args,target_args):
        if kind(source)!=kind(target) or at>=len(before):return None
        i=before[at];op=int(i['opcode'],16);k=kind(source)
        local=op-min(loads[k]) if op in loads[k] else i.get('local_index') if i['opcode']==generic[k] else None
        if local!=slot:return None
        at+=1;slot+=2 if k in ('J','D') else 1
        if k=='A' and source!=target:
            cast=target[1:-1] if target.startswith('L') else target
            if at>=len(before) or before[at]['opcode']!='0xc0' or before[at]['operand']!=cast:return None
            at+=1
        elif source!=target:return None
    if at!=len(before):return None
    return dict(kind='EXACT_COMPILER_BRIDGE',target=dict(entry=entry,method=name,descriptor=target_desc))


def collect(census, index, jar, selection=None, field_index=None):
    assert sha256(jar)==census['jar_sha256']
    native={(m['entry'],m['method'],m['descriptor']):m for m in census['methods']}
    covered={(m['entry'],m['method'],m['descriptor']) for m in index['methods']}
    selected={(r['entry'],r['method'],r['descriptor']) for r in selection} if selection is not None else None
    if selected is not None:
        assert selected <= set(native)
        covered-=selected
    assert index['jar_sha256']==census['jar_sha256']
    classes={c['entry']:c for c in census['classes']}
    candidates=[m for k,m in native.items() if k not in covered and (selected is None or k in selected) and
                (m['access'] & 0x1040==0x1040 or
                 (m['access'] & 8 and m['descriptor'].endswith(')V') and m['code_bytes']==1) or
                 (m['method']=='<init>' and m['descriptor']=='()V' and m['code_bytes']==5) or
                 (classes[m['entry']]['superclass']=='software/bernie/geckolib/model/GeoModel' and m['method'] in ('getAnimationResource','getModelResource','getTextureResource') and m['code_bytes'] in (6,7)) or
                 (m['method'] in ('getAmbientSound','getHurtSound','getDeathSound') and m['code_bytes'] in (17,18)) or
                 (m['method']=='getAnimatableInstanceCache' and m['code_bytes']==5) or
                 (m['method'] in ('movementPredicate','attackingPredicate','idlePredicate','registerControllers','getTexture','setTexture','getSyncedAnimation','setAnimation')) or
                 (classes[m['entry']]['superclass']=='net/minecraft/client/particle/TextureSheetParticle') or
                 ('net/minecraft/client/particle/ParticleProvider' in classes[m['entry']]['interfaces']) or
                 (m['method']=='appendHoverText') or
                 (classes[m['entry']]['superclass']=='software/bernie/geckolib/renderer/GeoEntityRenderer' and m['method']=='getDeathMaxRotation' and m['code_bytes'] in (2,3,4)) or
                 (m['access'] & 0x1008 == 0x1008 and m['descriptor'].endswith(')Z') and m['code_bytes']==2) or
                 (m['access'] & 8 and m['descriptor']=='(Lnet/minecraft/world/phys/Vec3;Lnet/minecraft/world/entity/Entity;)D' and m['code_bytes']==6) or
                 (m['descriptor'] in ('(DDD)Ljava/util/Comparator;','(DDDLnet/minecraft/world/entity/Entity;)D') and m['code_bytes'] in (10,13)))]
    parsed={};waiting=[];rows=[]
    with zipfile.ZipFile(jar) as z:
        for m in candidates:
            entry=m['entry']
            if entry not in parsed:
                raw=z.read(entry);assert byte_hash(raw)==classes[entry]['entry_sha256']
                parsed[entry]=ClassFile(raw,retain_code_metadata=True)
            cls=parsed[entry];method=next(x for x in cls.methods if (x['name'],x['descriptor'])==(m['method'],m['descriptor']))
            code=method.get('code',b'');assert byte_hash(code)==m['code_sha256'] and method['access']==m['access']
            body=annotate_local_operands(list(cls.instructions(code)),code)
            from compare_native_methods import bootstrap_signature,referenced_bootstraps
            bootstraps={str(n):bootstrap_signature(cls,n) for n in referenced_bootstraps(body)}
            shape=forwarding_shape(entry,m['method'],m['descriptor'],m['access'],body,method.get('exception_handlers',[]),bootstraps,cls.super)
            if not shape:continue
            if is_animation(shape):
                from native_animation_shapes import validate_context
                if shape.get('animation_only_fields') and field_index is None:continue
                validate_context(shape,entry,census,field_index)
            if is_particle(shape):
                from native_particle_shapes import validate_context
                validate_context(shape,entry,census)
            waiting.append(dict(entry=entry,entry_sha256=classes[entry]['entry_sha256'],method=m['method'],descriptor=m['descriptor'],
                access=m['access'],code_sha256=m['code_sha256'],code_hex=code.hex(),instructions=body,exception_handlers=[],
                **(dict(superclass=cls.super) if is_animation(shape) or is_particle(shape) or shape['kind'] in ('EXACT_GECKO_MODEL_ASSET_QUERY','EXACT_GECKO_DEATH_RENDER_ROTATION','EXACT_NATIVE_LITERAL_TOOLTIP') else {}),
                **(dict(bootstraps=bootstraps) if bootstraps else {}),**shape))
    query_keys={(r['entry'],r['method'],r['descriptor']) for r in waiting if r['kind']=='EXACT_NATIVE_DISTANCE_QUERY'}
    while waiting:
        next_wait=[]
        for r in waiting:
            target=r.get('target');targets=required_targets(r)
            if r['kind']=='EXACT_NATIVE_DISTANCE_COMPARATOR_FACTORY' and (target['entry'],target['method'],target['descriptor']) not in query_keys:
                continue
            if any((t['entry'],t['method'],t['descriptor']) not in covered for t in targets):
                next_wait.append(r);continue
            for t in targets:t['code_sha256']=native[(t['entry'],t['method'],t['descriptor'])]['code_sha256']
            covered.add((r['entry'],r['method'],r['descriptor']));rows.append(r)
        if len(next_wait)==len(waiting):break
        waiting=next_wait
    if selected is not None:
        assert {(r['entry'],r['method'],r['descriptor']) for r in rows}==selected,'Pinned selection no longer has exact context/target proof'
    templates={}
    for r in rows:
        body=r.pop('instructions')
        digest=byte_hash(json.dumps(body,sort_keys=True,separators=(',',':')).encode())
        templates.setdefault(digest,body);r['instruction_template']=digest
    scope='Exact unresolved finite-census methods only. No new semantics from constructor defaults; fields/readers remain queued. Virtual subclass dispatch and checkcast failure remain native. No bridge target closes from capture alone.'
    if query_keys:
        scope+=' Distance comparator factories require exact pure target-query proof; native ordering and caller combat gates/payloads remain separate.'
    if any(r['kind']=='EXACT_GECKO_MODEL_ASSET_QUERY' for r in rows):
        scope+=' Constant GeckoLib model asset queries require exact superclass/API/asset path shape; renderer/actor/input state and computed selectors remain separate.'
    if any(r['kind'] in ('EXACT_SYNTHETIC_TRUE_PREDICATE','EXACT_NATIVE_VEC3_DISTANCE_QUERY') for r in rows):
        scope+=' Exact synthetic true predicates and current native Vec3 distance queries contribute no separate scalar/payload; caller selection, admission and ordering are retained, not excluded.'
    if any(r['kind'] in ('EXACT_NATIVE_SOUND_REGISTRY_QUERY','EXACT_GECKO_ANIMATION_CACHE_QUERY','EXACT_GECKO_DEATH_RENDER_ROTATION','EXACT_NATIVE_LITERAL_TOOLTIP') for r in rows):
        scope+=' Exact sound registry returns, GeckoLib animation-cache queries and literal renderer death rotations are presentation API leaves; actor death/hurt, animation state writers and physical transforms remain separate.'
        if any(r['kind']=='EXACT_NATIVE_LITERAL_TOOLTIP' for r in rows):
            scope+=' Literal tooltip additions mutate only the supplied text list after the exact native parent call; tooltip claims do not establish actual combat values or active mechanics.'
    if any(is_animation(r) for r in rows):
        scope+=' GeckoLib clip callbacks require exact allowed API effects, no authored native query overrides, and native actor inheritance. Scratch attack animation fields must be actor-declared with no gameplay consumers. Controller registration requires every actual typed handler to be independently dispositioned. String transport preserves producer/readers and cannot close them or promote animation clocks into combat scalars.'
    if any(is_particle(r) for r in rows):
        scope+=' Native TextureSheetParticle construction/tick/render fields and typed ParticleProvider factories operate on client particles, not Entity damage or physical actor motion. Exact constructor/factory target coverage is required; particle-requesting combat producers, ownership and actual damage remain separate.'
    return dict(schema='tno.external_effects.exact_native_forwarding.v1',mod_key=census['mod_key'],jar_sha256=census['jar_sha256'],
        scope=scope,
        **(dict(field_index_file=census['mod_key']+'-native-field-use-index.json',
                field_index_content_sha256=byte_hash(json.dumps(field_index,sort_keys=True,separators=(',',':')).encode())) if any(r.get('animation_only_fields') for r in rows) else {}),
        summary=dict(methods=len(rows),counts_by_kind=dict(sorted(Counter(r['kind'] for r in rows).items()))),
        instruction_templates=dict(sorted(templates.items())),
        rows=sorted(rows,key=lambda r:(r['entry'],r['method'],r['descriptor'])))


def required_targets(row):
    return ([row['target']] if row.get('target') else [])+row.get('targets',[])


def is_animation(row):
    return row['kind'] in {'EXACT_GECKO_CONTROLLER_REGISTRATION','EXACT_GECKO_MOVEMENT_CLIP_SELECTION',
                           'EXACT_GECKO_ATTACK_ANIMATION_CONTEXT','EXACT_NATIVE_SYNCED_ANIMATION_STRING_TRANSPORT','EXACT_GECKO_ITEM_IDLE_CLIP_CONTEXT'}


def is_particle(row):
    return row['kind'] in {'EXACT_NATIVE_PARTICLE_PARENT_TICK','EXACT_NATIVE_PARTICLE_ROLL_TICK','EXACT_NATIVE_PARTICLE_RENDER_TYPE','EXACT_NATIVE_PARTICLE_RENDER_LIGHT',
        'EXACT_NATIVE_CLIENT_PARTICLE_CONSTRUCTION','EXACT_NATIVE_PARTICLE_PROVIDER_FACTORY','EXACT_NATIVE_PARTICLE_SPRITE_PROVIDER','EXACT_NATIVE_CLIENT_PARTICLE_FACTORY'}


def validate(document,census,covered,field_index=None):
    assert document['schema']=='tno.external_effects.exact_native_forwarding.v1'
    assert document['mod_key']==census['mod_key'] and document['jar_sha256']==census['jar_sha256']
    if any(r.get('animation_only_fields') for r in document['rows']):
        assert field_index is not None
        assert document['field_index_file']==census['mod_key']+'-native-field-use-index.json'
        assert document['field_index_content_sha256']==byte_hash(json.dumps(field_index,sort_keys=True,separators=(',',':')).encode()),'Changed animation field-consumer evidence'
    native={(m['entry'],m['method'],m['descriptor']):m for m in census['methods']}
    classes={c['entry']:c for c in census['classes']};accepted=[];todo=list(document['rows']);seen=set()
    templates=document['instruction_templates']
    for digest,body in templates.items():
        assert byte_hash(json.dumps(body,sort_keys=True,separators=(',',':')).encode())==digest
    assert set(templates)=={r['instruction_template'] for r in todo}
    for r in todo:
        key=(r['entry'],r['method'],r['descriptor']);assert key not in seen;seen.add(key)
        n=native[key];assert r['code_sha256']==n['code_sha256']==byte_hash(bytes.fromhex(r['code_hex']))
        assert r['entry_sha256']==classes[r['entry']]['entry_sha256'] and r['access']==n['access']
        if 'superclass' in r:assert r['superclass']==classes[r['entry']]['superclass']
        shape=forwarding_shape(r['entry'],r['method'],r['descriptor'],r['access'],templates[r['instruction_template']],r['exception_handlers'],r.get('bootstraps'),r.get('superclass'))
        assert shape and shape['kind']==r['kind']
        if is_animation(shape):
            from native_animation_shapes import validate_context
            validate_context(shape,r['entry'],census,field_index)
        if is_particle(shape):
            from native_particle_shapes import validate_context
            validate_context(shape,r['entry'],census)
        for field,value in shape.items():
            if field not in ('kind','target','targets'):assert r[field]==value
        if 'target' in shape:
            assert all(r['target'][k]==v for k,v in shape['target'].items())
            t=r['target'];assert t['code_sha256']==native[(t['entry'],t['method'],t['descriptor'])]['code_sha256']
        else:assert 'target' not in r
        if shape.get('targets'):
            assert len(r['targets'])==len(shape['targets'])
            for t,s in zip(r['targets'],shape['targets']):
                assert all(t[k]==v for k,v in s.items())
                assert t['code_sha256']==native[(t['entry'],t['method'],t['descriptor'])]['code_sha256']
        else:assert 'targets' not in r
    covered=set(covered)
    query_keys={(r['entry'],r['method'],r['descriptor']) for r in todo if r['kind']=='EXACT_NATIVE_DISTANCE_QUERY'}
    for r in todo:
        if r['kind']=='EXACT_NATIVE_DISTANCE_COMPARATOR_FACTORY':
            t=r['target']
            assert (t['entry'],t['method'],t['descriptor']) in query_keys,'Comparator target lacks exact pure-query proof'
    while todo:
        pending=[]
        for r in todo:
            if any((t['entry'],t['method'],t['descriptor']) not in covered for t in required_targets(r)):pending.append(r);continue
            covered.add((r['entry'],r['method'],r['descriptor']));accepted.append(r)
        assert len(pending)<len(todo),'Bridge target lacks prior exact contract/exclusion; cycles cannot self-prove'
        todo=pending
    assert document['summary']==dict(methods=len(accepted),counts_by_kind=dict(sorted(Counter(r['kind'] for r in accepted).items())))
    return accepted


def write_registry(path,document,compact=False):
    """Optional deterministic compact rows/templates; prior formatting is default."""
    if not compact:return write_json(path,document)
    arrays={'rows','instruction_templates'}
    header=json.dumps({k:v for k,v in document.items() if k not in arrays},ensure_ascii=False,indent=2)
    dump=lambda v:json.dumps(v,ensure_ascii=False,separators=(',',':'))
    parts=[header[:-2],',\n  "instruction_templates": {\n',
           ',\n'.join('    '+dump(k)+':'+dump(v) for k,v in document['instruction_templates'].items()),
           '\n  },\n  "rows": [\n',',\n'.join('    '+dump(v) for v in document['rows']),'\n  ]\n}\n']
    Path(path).write_text(''.join(parts),encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mod_key');p.add_argument('--jar',type=Path,required=True);p.add_argument('--index',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--selection',type=Path);p.add_argument('--field-index',type=Path);p.add_argument('--compact',action='store_true');a=p.parse_args()
    c=read_json(OUT/f'{a.mod_key}-combat-census.json');i=read_json(a.index)
    selection=read_json(a.selection)['rows'] if a.selection else None
    fields=read_json(a.field_index) if a.field_index else None
    d=collect(c,i,a.jar,selection=selection,field_index=fields)
    validate(d,c,{(m['entry'],m['method'],m['descriptor']) for m in i['methods']},field_index=fields);write_registry(a.output,d,compact=a.compact);print(d['summary'])
