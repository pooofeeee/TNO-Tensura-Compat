from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_cataclysm_foundation import targets,KEY,PKG

FIELDS=['EFFECTGHOST_FORM','EFFECTGHOST_SICKNESS','EFFECTABYSSAL_FEAR','EFFECTBLESSING_OF_AMETHYST']
def usages():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(z.namelist()):
            if not n.endswith('.class'):continue
            c=ClassFile(z.read(n))
            for m in c.methods:
                ins=list(c.instructions(m.get('code',b'')));hits=[i for i in ins if i['opcode']=='0xb2' and any('ModEffect.'+f+'L' in str(i.get('operand','')) for f in FIELDS)]
                if hits:rows.append(dict(entry=n,method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(schema='tno.external_effects.cataclysm_ghost_fear_usages.v1',jar_sha256=t['sha256'],fields=FIELDS,rows=rows)

def save():
    u=usages();wanted={};t=targets()[KEY]
    for r in u['rows']:wanted.setdefault(r['entry'],set()).add(r['method'])
    full=['effects/EffectGhostForm','effects/EffectGhost_Sickness','effects/EffectAbyssal_Fear','effects/EffectBlessing_Of_Amethyst','items/Blessed_Amethyst_Crab_Meat','entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Mine_Entity']
    with zipfile.ZipFile(t['path']) as z:
        for short in full:
            n=PKG+short+'.class';wanted[n]={m['name'] for m in ClassFile(z.read(n)).methods}
    wanted.setdefault(PKG+'event/ServerEventHandler.class',set()).add('DeathEvent')
    wanted.setdefault(PKG+'init/ModItems.class',set()).add('<clinit>')
    wanted[PKG+'entity/AnimationMonster/BossMonsters/The_Leviathan/Abyss_Orb_Entity.class']|={'getDamage','onHitBlock'}
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Ghost rebirth/sickness, heal veto and Blessing cleanse/food; originating Leviathan attack family remains pending.',evidence_specifications=[dict(id='cataclysm:ghost_fear:'+n,mod_key=KEY,entry=n,methods=sorted(v)) for n,v in sorted(wanted.items())]);write_json(OUT/'cataclysm-ghost-fear-usages.json',u);write_json(OUT/'native-specifications/cataclysm-ghost-fear.json',s);write_json(OUT/'native-evidence/cataclysm-ghost-fear.json',collect(s))
    originals=read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'];a=dict(originals[0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/entity/LivingEntity.class':['heal','setHealth','removeEffect','removeAllEffects','removeEffectsCuredBy','tickEffects','addEffect','addEatEffect'],'net/minecraft/world/effect/MobEffectInstance.class':['<init>','getEffect','tick']}
    b=dict(originals[1]);b.pop('semantic_review',None);b['classes']={'net/neoforged/neoforge/common/extensions/IMobEffectExtension.class':['fillEffectCures']}
    r=dict(id='cataclysm-ghost-fear-244',scope='Native HP assignment vs healing event, cure-set vs explicit removal, finite effect expiry and food delivery.',archives=[a,b]);write_json(OUT/'reference-specifications/cataclysm-ghost-fear-244.json',r);write_json(OUT/'reference-evidence/cataclysm-ghost-fear-244.json',reference_collect(r,source_aids=True));print('Ghost/Fear reference methods',len(u['rows']),'native witnesses',len(wanted))

if __name__=='__main__':save()
