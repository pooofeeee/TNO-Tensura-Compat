"""Exact GeckoLib model/query/bone context; target coverage remains mandatory."""
import re
from native_animation_shapes import CONCAT,STRING_GET

G='software/bernie/geckolib/'
RESOURCE='Lnet/minecraft/resources/ResourceLocation;'


def recipe(body,bootstraps):
    sites=[i for i in body if i['opcode']=='0xba']
    if len(sites)!=1:return None
    m=re.fullmatch(r'bootstrap#(\d+):makeConcatWithConstants\(Ljava/lang/String;\)Ljava/lang/String;',str(sites[0]['operand']))
    if not m or set(bootstraps)!={m[1]}:return None
    b=bootstraps[m[1]]
    if b.get('handle')!=dict(tag=15,value=CONCAT,reference_kind=6):return None
    args=b.get('arguments',[])
    if len(args)!=1 or args[0].get('tag')!=8 or not isinstance(args[0].get('value'),str):return None
    return args[0]['value']


def model_shape(entry,name,descriptor,access,body,bootstraps,superclass):
    if superclass!=G+'model/GeoModel' or access & 8:return None
    owner=entry[:-6];ops=[i['opcode'] for i in body]
    if name=='<init>' and descriptor=='()V' and ops==['0x2a','0xb7','0xb1'] and body[0].get('local_index')==0 and body[1]['operand']==G+'model/GeoModel.<init>()V':
        return dict(kind='EXACT_GECKO_MODEL_PARENT_CONSTRUCTION')
    arg=re.fullmatch(r'\(L([^;]+);\)'+re.escape(RESOURCE),descriptor)
    if arg and name=='getTextureResource' and ops==['0x2b','0xb6','0xba','0xb8','0xb0']:
        actor=arg[1];s=recipe(body,bootstraps)
        if body[0].get('local_index')!=1 or body[1]['operand']!=actor+'.getTexture()Ljava/lang/String;' or body[3]['operand']!='net/minecraft/resources/ResourceLocation.parse(Ljava/lang/String;)'+RESOURCE:return None
        if not s or not re.fullmatch(r'[a-z0-9_.-]+:textures/[a-z0-9_/.-]*\x01\.png',s):return None
        return dict(kind='EXACT_GECKO_DYNAMIC_TEXTURE_QUERY',asset_recipe=s,
                    target=dict(entry=actor+'.class',method='getTexture',descriptor='()Ljava/lang/String;'))
    if arg and name in ('getAnimationResource','getModelResource') and ops==['0x2b','0xb6','0xb2','0xb6','0xc0','0x4d','0x2c','0xc6','0x2c','0xb6','0x99','0x12','0x4d','0x12','0x2c','0xba','0xb8','0xb0']:
        actor=arg[1];suffix='animations/\x01.animation.json' if name=='getAnimationResource' else 'geo/\x01.geo.json'
        values={1:actor+'.getEntityData()Lnet/minecraft/network/syncher/SynchedEntityData;',3:STRING_GET,4:'java/lang/String',
                9:'java/lang/String.isEmpty()Z',16:'net/minecraft/resources/ResourceLocation.fromNamespaceAndPath(Ljava/lang/String;Ljava/lang/String;)'+RESOURCE}
        if any(body[j]['operand']!=v for j,v in values.items()) or recipe(body,bootstraps)!=suffix:return None
        if body[0].get('local_index')!=1 or any(body[j].get('local_index')!=2 for j in (5,6,8,12,14)):return None
        if not isinstance(body[11]['operand'],str) or not isinstance(body[13]['operand'],str):return None
        field=body[2]['operand']
        if not re.fullmatch(re.escape(actor)+r'\.DATA_[A-Za-z0-9_]+Lnet/minecraft/network/syncher/EntityDataAccessor;',str(field)):return None
        return dict(kind='EXACT_GECKO_SYNCED_STRING_ASSET_QUERY',actor_entry=actor+'.class',asset_recipe=suffix,
                    asset_namespace=body[13]['operand'],fallback_asset_name=body[11]['operand'],string_accessor=field,
                    inherited_query='getEntityData()Lnet/minecraft/network/syncher/SynchedEntityData;')
    if name=='setCustomAnimations' and re.fullmatch(r'\(L[^;]+;JL'+G+r'animation/AnimationState;\)V',descriptor):
        expected=['0x2a','0xb6','0x12','0xb6','0x3a','0x19','0xc6','0x19','0xb2','0xb6','0xc0','0x3a',
                  '0x19','0x19','0xb6','0x12','0x6a','0xb6','0x19','0x19','0xb6','0x12','0x6a','0xb6','0xb1']
        if ops!=expected or bootstraps:return None
        values={1:owner+'.getAnimationProcessor()L'+G+'animation/AnimationProcessor;',
                3:G+'animation/AnimationProcessor.getBone(Ljava/lang/String;)L'+G+'cache/object/GeoBone;',
                8:G+'constant/DataTickets.ENTITY_MODEL_DATAL'+G+'constant/dataticket/DataTicket;',
                9:G+'animation/AnimationState.getData(L'+G+'constant/dataticket/DataTicket;)Ljava/lang/Object;',
                10:G+'model/data/EntityModelData',14:G+'model/data/EntityModelData.headPitch()F',
                17:G+'cache/object/GeoBone.setRotX(F)V',20:G+'model/data/EntityModelData.netHeadYaw()F',23:G+'cache/object/GeoBone.setRotY(F)V'}
        if any(body[j]['operand']!=v for j,v in values.items()):return None
        if any(body[j].get('local_index')!=v for j,v in {0:0,4:5,5:5,7:4,11:6,12:5,13:6,18:5,19:6}.items()):return None
        if not isinstance(body[2]['operand'],str) or any(type(body[j]['operand']) not in (int,float) for j in (15,21)):return None
        return dict(kind='EXACT_GECKO_MODEL_BONE_ROTATION',bone_name=body[2]['operand'],original_pitch_factor=body[15]['operand'],original_yaw_factor=body[21]['operand'],
                    inherited_query='getAnimationProcessor()L'+G+'animation/AnimationProcessor;')
    return None


def validate_context(shape,entry,census):
    classes={c['entry']:c for c in census['classes']}
    assert classes[entry]['superclass']==G+'model/GeoModel'
    if shape.get('inherited_query'):
        assert shape['inherited_query'] not in {m['method']+m['descriptor'] for m in census['methods']},'Authored model/query override needs review'
    if shape.get('actor_entry') or shape.get('target'):
        target=shape.get('actor_entry') or shape['target']['entry']
        assert G+'animatable/GeoEntity' in classes[target]['interfaces'],'Dynamic asset source must be an actual native GeoEntity'
    if shape.get('string_accessor'):
        actor=classes[shape['actor_entry']];field=shape['string_accessor'].split('.')[-1]
        assert any(f['name']+f['descriptor']==field and f['access'] & 8 for f in actor['fields'])
