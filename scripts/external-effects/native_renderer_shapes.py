"""Exact renderer bindings and simple presentation leaves, not class exclusions."""
import re
from native_model_shapes import G,RESOURCE

CTX='(Lnet/minecraft/client/renderer/entity/EntityRendererProvider$Context;)V'
LAYER='L'+G+'renderer/layer/GeoRenderLayer;'
LCTOR='(L'+G+'renderer/GeoRenderer;)V'
BASECTOR=G+'renderer/GeoEntityRenderer.<init>(Lnet/minecraft/client/renderer/entity/EntityRendererProvider$Context;L'+G+'model/GeoModel;)V'
PRETAIL='L'+G+'cache/object/BakedGeoModel;Lnet/minecraft/client/renderer/MultiBufferSource;Lcom/mojang/blaze3d/vertex/VertexConsumer;ZFIII)V'
PREBASE='(Lcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/world/entity/Entity;'+PRETAIL


def renderer_shape(entry,name,descriptor,access,body,superclass):
    if access & 8:return None
    owner=entry[:-6];ops=[i['opcode'] for i in body]
    if superclass==G+'renderer/layer/GeoRenderLayer' and name=='<init>' and descriptor==LCTOR and ops==['0x2a','0x2b','0xb7','0xb1'] and [body[j].get('local_index') for j in (0,1)]==[0,1] and body[2]['operand']==G+'renderer/layer/GeoRenderLayer.<init>'+LCTOR:
        return dict(kind='EXACT_GECKO_RENDER_LAYER_PARENT_CONSTRUCTION')
    if superclass!=G+'renderer/GeoEntityRenderer':return None
    if name=='<init>' and descriptor==CTX:
        if ops[:6]!=['0x2a','0x2b','0xbb','0x59','0xb7','0xb7'] or [body[j].get('local_index') for j in (0,1)]!=[0,1] or body[5]['operand']!=BASECTOR or ops[-1]!='0xb1':return None
        model=str(body[2]['operand'])
        if body[4]['operand']!=model+'.<init>()V':return None
        targets=[dict(entry=model+'.class',method='<init>',descriptor='()V')];fields=[];at=6
        while at<len(body)-1:
            if body[at]['opcode']!='0x2a' or body[at].get('local_index')!=0:return None
            if at+2<len(body) and body[at+1]['opcode'] in ('0xb','0xc','0xd','0x12','0x13') and body[at+2]['opcode']=='0xb5':
                value=body[at+1]['operand'];field=body[at+2]['operand']
                if type(value) not in (int,float) or field not in (owner+'.shadowRadiusF',owner+'.debugYawF'):return None
                fields.append(dict(field=field,value=value));at+=3;continue
            if at+6>=len(body) or [i['opcode'] for i in body[at:at+7]]!=['0x2a','0xbb','0x59','0x2a','0xb7','0xb6','0x57'] or body[at+3].get('local_index')!=0:return None
            target=str(body[at+1]['operand'])
            if body[at+4]['operand']!=target+'.<init>'+LCTOR or body[at+5]['operand']!=owner+'.addRenderLayer('+LAYER+')L'+G+'renderer/GeoEntityRenderer;':return None
            targets.append(dict(entry=target+'.class',method='<init>',descriptor=LCTOR));at+=7
        if not fields:return None
        return dict(kind='EXACT_GECKO_RENDERER_CONSTRUCTION',model_entry=model+'.class',targets=targets,renderer_initial_fields=fields)
    arg=re.fullmatch(r'\(L([^;]+);'+re.escape(RESOURCE)+r'Lnet/minecraft/client/renderer/MultiBufferSource;F\)Lnet/minecraft/client/renderer/RenderType;',descriptor)
    if name=='getRenderType' and arg and ops==['0x2a','0x2b','0xb6','0xb8','0xb0'] and [body[j].get('local_index') for j in (0,1)]==[0,1] and body[2]['operand']==owner+'.getTextureLocation(Lnet/minecraft/world/entity/Entity;)'+RESOURCE and body[3]['operand']=='net/minecraft/client/renderer/RenderType.entityTranslucent('+RESOURCE+')Lnet/minecraft/client/renderer/RenderType;':
        return dict(kind='EXACT_GECKO_RENDERER_TEXTURE_TYPE_QUERY',actor_entry=arg[1]+'.class',targets=[dict(entry=entry,method='<init>',descriptor=CTX)])
    arg=re.fullmatch(r'\(Lcom/mojang/blaze3d/vertex/PoseStack;L([^;]+);'+re.escape(PRETAIL),descriptor)
    if name=='preRender' and arg and len(body)==21:
        prefix=['0xc','0x38','0x2a','0x17','0xb5','0x2a','0x17','0xb5']
        if ops[:8]!=prefix and not (ops[0] in ('0xb','0xd','0x12','0x13') and ops[1:8]==prefix[1:]):return None
        if type(body[0]['operand']) not in (int,float) or any(body[j].get('local_index')!=11 for j in (1,3,6)) or any(body[j].get('local_index')!=0 for j in (2,5)) or body[4]['operand']!=owner+'.scaleHeightF' or body[7]['operand']!=owner+'.scaleWidthF':return None
        if ops[8:]!=['0x2a','0x2b','0x2c','0x2d','0x19','0x19','0x15','0x17','0x15','0x15','0x15','0xb7','0xb1'] or [i.get('local_index') for i in body[8:19]]!=list(range(11)) or body[19]['operand']!=G+'renderer/GeoEntityRenderer.preRender'+PREBASE:return None
        return dict(kind='EXACT_GECKO_LITERAL_RENDER_SCALE',original_renderer_scale=body[0]['operand'])
    return None


def bind_context(shape,entry,census):
    """Bind inherited texture dispatch to the constructor's actual model target.

The constructor is itself a required independently checked target, whose shape
proves new-model-to-parent argument flow; the original call census supplies its
identity without inferring a model from an actor/renderer display name.
"""
    if shape['kind']!='EXACT_GECKO_RENDERER_TEXTURE_TYPE_QUERY':return shape
    from collect_combat_census import decode_sites
    ctor=next(m for m in census['methods'] if (m['entry'],m['method'],m['descriptor'])==(entry,'<init>',CTX))
    calls=decode_sites(census,ctor,'calls');first=str(calls[0]['operand'])
    assert first.endswith('.<init>()V') and calls[1]['operand']==BASECTOR
    model=first[:-len('.<init>()V')]+'.class';actor=shape['actor_entry'][:-6]
    shape=dict(shape,targets=list(shape['targets'])+[dict(entry=model,method='getTextureResource',descriptor='(L'+actor+';)'+RESOURCE)],
               model_binding=dict(constructor_code_sha256=ctor['code_sha256'],model_entry=model))
    return shape


def validate_context(shape,entry,census):
    classes={c['entry']:c for c in census['classes']};cls=classes[entry]
    if shape['kind']=='EXACT_GECKO_RENDER_LAYER_PARENT_CONSTRUCTION':
        assert cls['superclass']==G+'renderer/layer/GeoRenderLayer';return
    assert cls['superclass']==G+'renderer/GeoEntityRenderer'
    if shape.get('model_entry'):
        assert classes[shape['model_entry']]['superclass']==G+'model/GeoModel'
        for t in shape['targets'][1:]:assert classes[t['entry']]['superclass']==G+'renderer/layer/GeoRenderLayer'
        for f in shape['renderer_initial_fields']:
            if f['field'].endswith('.debugYawF'):assert any(d['name']=='debugYaw' and d['descriptor']=='F' for d in cls['fields'])
    if shape.get('actor_entry'):
        assert G+'animatable/GeoEntity' in classes[shape['actor_entry']]['interfaces']
        assert classes[shape['model_binding']['model_entry']]['superclass']==G+'model/GeoModel'
        assert not any(m['entry']==entry and m['method']=='getTextureLocation' and m['descriptor']=='(Lnet/minecraft/world/entity/Entity;)'+RESOURCE for m in census['methods']),'Authored texture dispatch requires review'
        assert not any(c['superclass']==cls['name'] for c in census['classes']),'Authored renderer descendant dispatch requires review'
    if shape['kind']=='EXACT_GECKO_RENDERER_CONSTRUCTION':
        assert not any(m['entry']==entry and m['method']=='addRenderLayer' for m in census['methods']),'Authored layer admission requires review'
