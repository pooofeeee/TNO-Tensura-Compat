from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from vanilla_reference import prepare
from collect_cataclysm_foundation import targets,KEY,PKG

def usages():
    rows=[];t=targets()[KEY]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(z.namelist()):
            if not n.endswith('.class'):continue
            c=ClassFile(z.read(n))
            for m in c.methods:
                ins=list(c.instructions(m.get('code',b'')));hits=[i for i in ins if i['opcode']=='0xb2' and 'ModEffect.EFFECTSTUN' in str(i.get('operand',''))]
                if hits:rows.append(dict(entry=n,method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(schema='tno.external_effects.cataclysm_stun_usages.v1',jar_sha256=t['sha256'],rows=rows,scope='Whole installed artifact field-reference methods; boss animation/caller parameter schedules remain their family review.')

def save():
    u=usages();wanted={}
    for r in u['rows']:wanted.setdefault(r['entry'],set()).add(r['method'])
    t=targets()[KEY]
    with zipfile.ZipFile(t['path']) as z:
        for short in ['effects/EffectStun','mixin/LivingEntityMixin','util/EntityUtil','message/MessageSwingArm','items/CuriosItem/Unbreakable_Skull']:
            n=PKG+short+'.class';wanted[n]={m['name'] for m in ClassFile(z.read(n)).methods}
        n=PKG+'entity/etc/Animation_Monsters.class';wanted[n]={m['name'] for m in ClassFile(z.read(n)).methods if m['name'] in ['getEntityLivingBaseNearby','getEntitiesNearby'] or m['name'].startswith('lambda$getEntitiesNearby')}
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='STUN core/action hooks and all native STUN reference methods; effect-side admission reviewed, full boss attacks deferred.',evidence_specifications=[dict(id='cataclysm:stun:'+n,mod_key=KEY,entry=n,methods=sorted(names)) for n,names in sorted(wanted.items())])
    write_json(OUT/'cataclysm-stun-usages.json',u);write_json(OUT/'native-specifications/cataclysm-stun.json',s);write_json(OUT/'native-evidence/cataclysm-stun.json',collect(s))
    originals=read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'];a=dict(originals[0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/entity/LivingEntity.class':['addEffect','actuallyHurt','removeEffect'],'net/minecraft/world/entity/player/Player.class':['actuallyHurt'],'net/minecraft/world/effect/MobEffectInstance.class':['<init>','getEffect'],'net/minecraft/world/effect/MobEffect.class':['addAttributeModifiers','removeAttributeModifiers'],'net/minecraft/core/Holder$Reference.class':['equals']}
    b=dict(originals[1]);b.pop('semantic_review',None);b['classes']={'net/neoforged/neoforge/registries/DeferredHolder.class':['*'],'net/neoforged/neoforge/common/CommonHooks.class':['onLivingDamagePost'],'net/neoforged/neoforge/event/entity/living/LivingDamageEvent$Post.class':['*']}
    a['classes'].update({'net/minecraft/world/effect/MobEffect$AttributeTemplate.class':['create'],'net/minecraft/world/entity/projectile/Projectile.class':['getEffectSource']})
    r=dict(id='cataclysm-stun-244',scope='Actual preserved effect holder, modifier amount, overload delegation and post-damage HP timing.',archives=[a,b]);write_json(OUT/'reference-specifications/cataclysm-stun-244.json',r);write_json(OUT/'reference-evidence/cataclysm-stun-244.json',reference_collect(r,source_aids=True))
    v=dict(classes={'net/minecraft/world/damagesource/DamageSources':['<init>','source','mobProjectile','mobAttack','inWall']},resources=[]);write_json(OUT/'vanilla-specifications/cataclysm-stun.json',v);write_json(OUT/'vanilla-evidence/cataclysm-stun.json',prepare(v));print('STUN methods',len(u['rows']),'native witnesses',len(wanted))

if __name__=='__main__':save()
