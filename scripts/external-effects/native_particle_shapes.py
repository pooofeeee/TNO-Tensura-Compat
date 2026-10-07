"""Exact client Particle API context, independent of names or combat producers."""
import re

P='net/minecraft/client/particle/'
WORLD='Lnet/minecraft/client/multiplayer/ClientLevel;'
SPRITE='L'+P+'SpriteSet;'
CTOR='('+WORLD+'DDDDDD'+SPRITE+')V'
CREATE='(Lnet/minecraft/core/particles/SimpleParticleType;'+WORLD+'DDDDDD)L'+P+'Particle;'
FIELDS={'spriteSet'+SPRITE,'quadSizeF','lifetimeI','gravityF','hasPhysicsZ','xdD','ydD','zdD','angularVelocityF','angularAccelerationF'}


def particle_shape(entry,name,descriptor,access,body,superclass):
    owner=entry[:-6];ops=[i['opcode'] for i in body]
    if superclass==P+'TextureSheetParticle':
        if name=='tick' and descriptor=='()V' and ops==['0x2a','0xb7','0xb1'] and body[0].get('local_index')==0 and body[1]['operand']==P+'TextureSheetParticle.tick()V':
            return dict(kind='EXACT_NATIVE_PARTICLE_PARENT_TICK')
        if name=='tick' and descriptor=='()V' and ops==['0x2a','0xb7','0x2a','0x2a','0xb4','0xb5','0x2a','0x59','0xb4','0x2a','0xb4','0x62','0xb5','0x2a','0x59','0xb4','0x2a','0xb4','0x62','0xb5','0xb1']:
            values={1:P+'TextureSheetParticle.tick()V',4:owner+'.rollF',5:owner+'.oRollF',8:owner+'.rollF',
                    10:owner+'.angularVelocityF',12:owner+'.rollF',15:owner+'.angularVelocityF',17:owner+'.angularAccelerationF',19:owner+'.angularVelocityF'}
            if all(body[j]['operand']==v for j,v in values.items()) and all(i.get('local_index')==0 for i in body if i['opcode']=='0x2a'):
                return dict(kind='EXACT_NATIVE_PARTICLE_ROLL_TICK')
        if name=='getRenderType' and descriptor=='()L'+P+'ParticleRenderType;' and ops==['0xb2','0xb0'] and body[0]['operand'] in {P+'ParticleRenderType.'+n+'L'+P+'ParticleRenderType;' for n in ('PARTICLE_SHEET_OPAQUE','PARTICLE_SHEET_TRANSLUCENT','PARTICLE_SHEET_LIT')}:
            return dict(kind='EXACT_NATIVE_PARTICLE_RENDER_TYPE',particle_render_type=body[0]['operand'])
        if name=='getLightColor' and descriptor=='(F)I' and len(body)==2 and body[0]['opcode'] in ('0x12','0x13','0x11','0x10') and type(body[0]['operand'])==int and ops[-1]=='0xac':
            return dict(kind='EXACT_NATIVE_PARTICLE_RENDER_LIGHT',render_light=body[0]['operand'])
        if name=='<init>' and descriptor==CTOR:
            if ops[:6]!=['0x2a','0x2b','0x28','0x18','0x18','0xb7'] or [i.get('local_index') for i in body[:5]]!=[0,1,2,4,6] or body[5]['operand']!=P+'TextureSheetParticle.<init>('+WORLD+'DDD)V' or ops[-1]!='0xb1':return None
            allowed={'0x2a','0x2b','0x28','0x18','0x19','0xb4','0xb5','0xb6','0xb7','0xb8','0xb9','0xb1',
                     '0x3','0x4','0x5','0x6','0x7','0x8','0xb','0xc','0xd','0xf','0x10','0x11','0x12','0x13','0x14','0x59','0x6a','0x6b','0x64','0x60'}
            calls={owner+'.setSize(FF)V',owner+'.pickSprite('+SPRITE+')V','java/lang/Math.max(II)I','net/minecraft/util/RandomSource.nextInt(I)I'}
            for j,i in enumerate(body[6:]):
                if i['opcode'] not in allowed:return None
                if i['opcode'] in ('0xb6','0xb7','0xb8','0xb9') and i['operand'] not in calls:return None
                if i['opcode'] in ('0xb4','0xb5'):
                    if not str(i['operand']).startswith(owner+'.'):return None
                    field=i['operand'][len(owner)+1:]
                    if field not in FIELDS|({'randomLnet/minecraft/util/RandomSource;'} if i['opcode']=='0xb4' else set()):return None
            return dict(kind='EXACT_NATIVE_CLIENT_PARTICLE_CONSTRUCTION',particle_fields=sorted({i['operand'] for i in body if i['opcode']=='0xb5'}))
        if name=='provider' and access & 8 and descriptor.startswith('('+SPRITE+')L') and ops==['0xbb','0x59','0x2a','0xb7','0xb0'] and body[2].get('local_index')==0:
            target=str(body[0]['operand'])
            if descriptor!='('+SPRITE+')L'+target+';' or body[3]['operand']!=target+'.<init>('+SPRITE+')V':return None
            return dict(kind='EXACT_NATIVE_PARTICLE_PROVIDER_FACTORY',target=dict(entry=target+'.class',method='<init>',descriptor='('+SPRITE+')V'))
    if superclass=='java/lang/Object':
        if name=='<init>' and descriptor=='('+SPRITE+')V' and ops==['0x2a','0xb7','0x2a','0x2b','0xb5','0xb1'] and [body[j].get('local_index') for j in (0,2,3)]==[0,0,1] and body[1]['operand']=='java/lang/Object.<init>()V' and body[4]['operand']==owner+'.spriteSet'+SPRITE:
            return dict(kind='EXACT_NATIVE_PARTICLE_SPRITE_PROVIDER')
        if name=='createParticle' and descriptor==CREATE and ops==['0xbb','0x59','0x2c','0x29','0x18','0x18','0x18','0x18','0x18','0x2a','0xb4','0xb7','0xb0'] and [body[j].get('local_index') for j in range(2,10)]==[2,3,5,7,9,11,13,0]:
            target=str(body[0]['operand'])
            if body[10]['operand']!=owner+'.spriteSet'+SPRITE or body[11]['operand']!=target+'.<init>'+CTOR:return None
            return dict(kind='EXACT_NATIVE_CLIENT_PARTICLE_FACTORY',target=dict(entry=target+'.class',method='<init>',descriptor=CTOR))
    return None


def validate_context(shape,entry,census):
    classes={c['entry']:c for c in census['classes']};cls=classes[entry]
    if cls['superclass']=='java/lang/Object':
        assert P+'ParticleProvider' in cls['interfaces'],'Provider must implement the native client ParticleProvider API'
        assert any(f['name']=='spriteSet' and f['descriptor']==SPRITE and not f['access'] & 8 for f in cls['fields'])
    else:assert cls['superclass']==P+'TextureSheetParticle'
    target=shape.get('target')
    if target:
        c=classes[target['entry']]
        if target['descriptor']==CTOR:assert c['superclass']==P+'TextureSheetParticle'
        else:assert c['superclass']=='java/lang/Object' and P+'ParticleProvider' in c['interfaces']
    if shape['kind']=='EXACT_NATIVE_CLIENT_PARTICLE_CONSTRUCTION':
        inherited={'setSize(FF)V','pickSprite('+SPRITE+')V'}
        assert not inherited & {m['method']+m['descriptor'] for m in census['methods']},'Authored particle setter requires separate review'
