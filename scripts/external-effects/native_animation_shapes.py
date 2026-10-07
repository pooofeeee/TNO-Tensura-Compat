"""Narrow GeckoLib context proofs; gameplay readers and native state stay separate.

These shapes are invoked by the existing finite-queue collector, not a new scan.
Resolved calls/fields, native inheritance, bootstrap handles and actual field
consumers are checked. A callback name, absence of combat keywords, or captured
method alone cannot establish this disposition.
"""
import re

G = 'software/bernie/geckolib/animation/'
PREDICATE = '(L'+G+'AnimationState;)L'+G+'PlayState;'
REGISTRAR = '(L'+G+'AnimatableManager$ControllerRegistrar;)V'
PARENTS = {'net/minecraft/world/entity/'+n for n in
           ('monster/Monster','monster/Spider','TamableAnimal','PathfinderMob','animal/Animal')}
QUERIES = {'isSprinting()Z','isDeadOrDying()Z','isShiftKeyDown()Z','onGround()Z',
           'isInWaterOrBubble()Z','isAggressive()Z','isVehicle()Z'}
ATTACK_QUERIES = {'getX()D','getZ()D','getAttackAnim(F)F','level()Lnet/minecraft/world/level/Level;'}
STRING_GET = 'net/minecraft/network/syncher/SynchedEntityData.get(Lnet/minecraft/network/syncher/EntityDataAccessor;)Ljava/lang/Object;'
STRING_SET = 'net/minecraft/network/syncher/SynchedEntityData.set(Lnet/minecraft/network/syncher/EntityDataAccessor;Ljava/lang/Object;)V'
CONSTRUCTOR = G+'AnimationController.<init>(Lsoftware/bernie/geckolib/animatable/GeoAnimatable;Ljava/lang/String;IL'+G+'AnimationController$AnimationStateHandler;)V'
ADD = G+'AnimatableManager$ControllerRegistrar.add(L'+G+'AnimationController;)L'+G+'AnimatableManager$ControllerRegistrar;'
METAF = 'java/lang/invoke/LambdaMetafactory.metafactory(Ljava/lang/invoke/MethodHandles$Lookup;Ljava/lang/String;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodType;Ljava/lang/invoke/MethodHandle;Ljava/lang/invoke/MethodType;)Ljava/lang/invoke/CallSite;'
CONCAT = 'java/lang/invoke/StringConcatFactory.makeConcatWithConstants(Ljava/lang/invoke/MethodHandles$Lookup;Ljava/lang/String;Ljava/lang/invoke/MethodType;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/invoke/CallSite;'


def concat_only(body, bootstraps):
    sites = [i for i in body if i['opcode']=='0xba']
    numbers = set()
    for i in sites:
        m = re.fullmatch(r'bootstrap#(\d+):makeConcatWithConstants\(Ljava/lang/String;Ljava/lang/String;\)Ljava/lang/String;', str(i['operand']))
        if not m:return False
        numbers.add(m[1]);b=bootstraps.get(m[1],{})
        if b.get('handle') != dict(tag=15,value=CONCAT,reference_kind=6):return False
        args=b.get('arguments',[])
        if len(args)!=1 or args[0].get('tag')!=8 or not isinstance(args[0].get('value'),str) or args[0]['value'].count('\x01')!=2:return False
    return set(bootstraps)==numbers


def animation_shape(entry, name, descriptor, access, body, bootstraps, superclass):
    if access & 8:return None
    owner=entry[:-6];ops=[i['opcode'] for i in body]
    if name=='idlePredicate' and descriptor==PREDICATE and superclass=='net/minecraft/world/item/Item':
        expected=['0x2a','0xb4','0x12','0xb6','0x99','0x2b','0xb6','0xb8','0x12','0xb6','0xb6','0xb2','0xb0','0xb2','0xb0']
        if ops!=expected or bootstraps:return None
        values={1:owner+'.animationprocedureLjava/lang/String;',2:'empty',3:'java/lang/String.equals(Ljava/lang/Object;)Z',
                6:G+'AnimationState.getController()L'+G+'AnimationController;',7:G+'RawAnimation.begin()L'+G+'RawAnimation;',
                9:G+'RawAnimation.thenLoop(Ljava/lang/String;)L'+G+'RawAnimation;',10:G+'AnimationController.setAnimation(L'+G+'RawAnimation;)V',
                11:G+'PlayState.CONTINUEL'+G+'PlayState;',13:G+'PlayState.STOPL'+G+'PlayState;'}
        if any(body[j]['operand']!=v for j,v in values.items()) or body[0].get('local_index')!=0 or body[5].get('local_index')!=1 or not isinstance(body[8]['operand'],str):return None
        return dict(kind='EXACT_GECKO_ITEM_IDLE_CLIP_CONTEXT',idle_clip=body[8]['operand'])
    # Preserve the exact String transport, without deciding what a producer or
    # reader means. No native actor authored onSyncedDataUpdated is permitted.
    string_names={'getTexture':'TEXTURE','setTexture':'TEXTURE',
                  'getSyncedAnimation':'ANIMATION','setAnimation':'ANIMATION'}
    if superclass in PARENTS and name in string_names:
        get=name.startswith('get')
        if descriptor!=('()Ljava/lang/String;' if get else '(Ljava/lang/String;)V'):return None
        expected=['0x2a','0xb4','0xb2','0xb6','0xc0','0xb0'] if get else ['0x2a','0xb4','0xb2','0x2b','0xb6','0xb1']
        if ops!=expected or body[0].get('local_index')!=0:return None
        if body[1]['operand']!=owner+'.entityDataLnet/minecraft/network/syncher/SynchedEntityData;':return None
        field=owner+'.'+string_names[name]+'Lnet/minecraft/network/syncher/EntityDataAccessor;'
        if body[2]['operand']!=field:return None
        if get and (body[3]['operand']!=STRING_GET or body[4]['operand']!='java/lang/String'):return None
        if not get and (body[3].get('local_index')!=1 or body[4]['operand']!=STRING_SET):return None
        return dict(kind='EXACT_NATIVE_SYNCED_ANIMATION_STRING_TRANSPORT',string_accessor=field,string_operation='GET' if get else 'SET')
    if name=='registerControllers' and descriptor==REGISTRAR and superclass in PARENTS|{'net/minecraft/world/item/Item'}:
        # Exact constructor/registrar sequences. Every handler must independently
        # have a reviewed disposition; lambda capture is not target coverage.
        chunks=[];at=0;stored=2
        while at<len(body)-1:
            start=at
            inline=body[at]['opcode']=='0x2b'
            if inline:at+=1
            if at+8>=len(body):return None
            b=body[at:at+8]
            if [i['opcode'] for i in b[:3]]!=['0xbb','0x59','0x2a'] or b[0]['operand']!=G+'AnimationController' or b[2].get('local_index')!=0:return None
            if b[3]['opcode'] not in ('0x12','0x13') or not isinstance(b[3]['operand'],str):return None
            if b[4]['opcode'] not in ('0x3','0x4','0x5','0x6','0x7','0x8','0x10','0x11') or type(b[4]['operand'])!=int:return None
            if b[5]['opcode']!='0x2a' or b[5].get('local_index')!=0 or b[6]['opcode']!='0xba' or b[7]['opcode']!='0xb7' or b[7]['operand']!=CONSTRUCTOR:return None
            m=re.fullmatch(r'bootstrap#(\d+):handle\(L'+re.escape(owner)+r';\)L'+G+r'AnimationController\$AnimationStateHandler;',str(b[6]['operand']))
            if not m:return None
            bootstrap=bootstraps.get(m[1],{})
            if bootstrap.get('handle')!=dict(tag=15,value=METAF,reference_kind=6):return None
            args=bootstrap.get('arguments',[])
            if len(args)!=3 or args[0]!=dict(tag=16,value=PREDICATE) or args[2]!=dict(tag=16,value=PREDICATE):return None
            target=args[1]
            t=re.fullmatch(r'SELF\.([^.()]+)'+re.escape(PREDICATE),str(target.get('value')))
            if not t or target.get('tag')!=15 or target.get('reference_kind')!=5:return None
            at+=8
            if not inline:
                if at+2>=len(body) or body[at].get('local_index')!=stored or body[at]['opcode'] not in ('0x4d','0x4e') or body[at+1]['opcode']!='0x2b' or body[at+1].get('local_index')!=1 or body[at+2].get('local_index')!=stored or body[at+2]['opcode'] not in ('0x2c','0x2d'):return None
                stored+=1;at+=3
            elif body[start].get('local_index')!=1:return None
            if at+1>=len(body) or body[at]['opcode']!='0xb6' or body[at]['operand']!=ADD or body[at+1]['opcode']!='0x57':return None
            at+=2
            chunks.append(dict(entry=entry,method=t[1],descriptor=PREDICATE,bootstrap=m[1],controller_name=b[3]['operand'],transition_ticks=b[4]['operand']))
        if not chunks or body[-1]['opcode']!='0xb1' or set(bootstraps)!={t['bootstrap'] for t in chunks}:return None
        return dict(kind='EXACT_GECKO_CONTROLLER_REGISTRATION',targets=[{k:t[k] for k in ('entry','method','descriptor')} for t in chunks],controllers=chunks)
    if superclass not in PARENTS or descriptor!=PREDICATE or name not in ('movementPredicate','attackingPredicate'):return None
    attack=name=='attackingPredicate'
    calls={G+'RawAnimation.begin()L'+G+'RawAnimation;',G+'RawAnimation.thenLoop(Ljava/lang/String;)L'+G+'RawAnimation;',
           G+'RawAnimation.thenPlay(Ljava/lang/String;)L'+G+'RawAnimation;',G+'AnimationState.setAndContinue(L'+G+'RawAnimation;)L'+G+'PlayState;',
           G+'AnimationState.getLimbSwingAmount()F',G+'AnimationState.isMoving()Z','java/lang/String.equals(Ljava/lang/Object;)Z','java/lang/String.isEmpty()Z',STRING_GET}
    queries=QUERIES if not attack else ATTACK_QUERIES
    calls|={owner+'.'+q for q in queries}
    if attack:calls|={G+'AnimationState.getPartialTick()F',G+'AnimationState.getController()L'+G+'AnimationController;',
                     G+'AnimationController.getAnimationState()L'+G+'AnimationController$State;',G+'AnimationController.forceAnimationReset()V',
                     'net/minecraft/world/level/Level.getGameTime()J','java/lang/Math.sqrt(D)D','java/lang/Boolean.booleanValue()Z'}
    allowed={'0x2a','0x2b','0x2c','0x4d','0x12','0x13','0x95','0x96','0x99','0x9a','0x9b','0x9e','0xc6',
             '0xb2','0xb4','0xb6','0xb8','0xb0','0xc0','0xba'}
    if attack:allowed|={'0x67','0x49','0x39','0x28','0x18','0x6b','0x63','0x90','0x38','0xb','0x4','0x3','0x14','0x61','0x94','0x9d','0xa6','0xb5','0x3a','0x19'}
    if not body or any(i['opcode'] not in allowed for i in body) or not concat_only(body,bootstraps):return None
    queries_used=[];written=[]
    for j,i in enumerate(body):
        op=i['opcode'];operand=str(i['operand'])
        if op in ('0xb6','0xb8'):
            if operand not in calls:return None
            if operand.startswith(owner+'.'):queries_used.append(operand[len(owner)+1:])
        elif op in ('0xb2','0xb4'):
            if operand in {G+'PlayState.STOPL'+G+'PlayState;',G+'PlayState.CONTINUEL'+G+'PlayState;',G+'AnimationController$State.STOPPEDL'+G+'AnimationController$State;'}:continue
            if not operand.startswith(owner+'.'):return None
            field=operand[len(owner)+1:]
            fixed={'animationprocedureLjava/lang/String;','entityDataLnet/minecraft/network/syncher/SynchedEntityData;'}
            if attack:fixed|={'xOldD','zOldD','swingingZ','lastSwingJ'}
            if field not in fixed and not re.fullmatch(r'(?:DATA_[A-Za-z0-9_]+|SHOOT)Lnet/minecraft/network/syncher/EntityDataAccessor;',field):return None
        elif op=='0xb5':
            if operand==owner+'.swingingZ':
                if j<2 or body[j-2].get('local_index')!=0 or body[j-2]['opcode']!='0x2a' or body[j-1]['opcode'] not in ('0x3','0x4'):return None
            elif operand==owner+'.lastSwingJ':
                if j<4 or [b['opcode'] for b in body[j-4:j]]!=['0x2a','0x2a','0xb6','0xb6'] or [b.get('local_index') for b in body[j-4:j-2]]!=[0,0] or body[j-2]['operand']!=owner+'.level()Lnet/minecraft/world/level/Level;' or body[j-1]['operand']!='net/minecraft/world/level/Level.getGameTime()J':return None
            else:return None
            written.append(operand)
        elif op=='0xc0' and operand not in ('java/lang/String','java/lang/Boolean'):return None
    if G+'AnimationState.setAndContinue(L'+G+'RawAnimation;)L'+G+'PlayState;' not in {i['operand'] for i in body}:return None
    if attack and sorted(written)!=sorted([owner+'.swingingZ']*2+[owner+'.lastSwingJ']):return None
    return dict(kind='EXACT_GECKO_ATTACK_ANIMATION_CONTEXT' if attack else 'EXACT_GECKO_MOVEMENT_CLIP_SELECTION',
                inherited_queries=sorted(set(queries_used)),animation_only_fields=sorted(set(written)))


def validate_context(shape, entry, census, field_index=None):
    """Independent finite declaration/consumer constraints for allowed effects."""
    classes={c['entry']:c for c in census['classes']};cls=classes[entry]
    assert any(t in cls['interfaces'] for t in ('software/bernie/geckolib/animatable/GeoEntity','software/bernie/geckolib/animatable/GeoItem'))
    # All declared overrides, including descendants, remain visible. A new
    # authored implementation of a whitelisted query requires its own review.
    declared={(m['method']+m['descriptor']) for m in census['methods']}
    assert not set(shape.get('inherited_queries',[])) & declared,'Authored native-query override requires review'
    if shape['kind']=='EXACT_NATIVE_SYNCED_ANIMATION_STRING_TRANSPORT':
        assert not any(m['method']=='onSyncedDataUpdated' for m in census['methods']),'Authored synced-data callback requires review'
        field=shape['string_accessor'].split('.')[-1]
        assert any(f['name']+f['descriptor']==field and f['access'] & 8 for f in cls['fields'])
    if shape.get('animation_only_fields'):
        assert field_index is not None,'Animation scratch writes need actual field-consumer proof'
        assert field_index['jar_sha256']==census['jar_sha256'] and field_index['mod_key']==census['mod_key']
        fields={f['name']+f['descriptor'] for f in cls['fields'] if not f['access'] & 8}
        targets=set(shape['animation_only_fields'])
        assert {f.split('.')[-1] for f in targets}<=fields,'Field must be declared on actor, not inherited combat swing state'
        from collect_combat_census import decode_sites
        for m in field_index['methods']:
            for i in decode_sites(field_index,m,'field_sites'):
                if i['operand'] in targets:
                    assert m['entry']==entry and m['method'] in ('<init>','attackingPredicate'),'Gameplay field consumer prevents presentation disposition'
