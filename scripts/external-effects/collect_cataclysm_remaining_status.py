from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_cataclysm_foundation import targets,KEY,PKG

FIELDS=['EFFECTMONSTROUS','EFFECTBLAZING_BRAND','EFFECTBONE_FRACTURE','EFFECTCURSE_OF_DESERT','EFFECTWETNESS']
def usages():
    t=targets()[KEY];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(z.namelist()):
            if not n.endswith('.class'):continue
            c=ClassFile(z.read(n))
            for m in c.methods:
                ins=list(c.instructions(m.get('code',b'')));hits=[i for i in ins if i['opcode']=='0xb2' and any('ModEffect.'+f+'L' in str(i.get('operand','')) for f in FIELDS)]
                if hits:rows.append(dict(entry=n,method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')),hits=hits))
    return dict(schema='tno.external_effects.cataclysm_remaining_status_usages.v1',jar_sha256=t['sha256'],fields=FIELDS,rows=rows)

def save():
    u=usages();wanted={};t=targets()[KEY]
    for r in u['rows']:wanted.setdefault(r['entry'],set()).add(r['method'])
    with zipfile.ZipFile(t['path']) as z:
        for short in ['effects/EffectMonstrous','effects/EffectBlazing_Brand','effects/EffectBone_Fracture','effects/EffectCurse_Of_Desert','effects/EffectWetness']:
            n=PKG+short+'.class';wanted[n]={m['name'] for m in ClassFile(z.read(n)).methods}
    wanted[PKG+'client/event/ClientEvent.class'].add('ClientEvent')
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Last five status cores and all native effect-field reader slices; full attack families stay pending.',evidence_specifications=[dict(id='cataclysm:remaining_status:'+n,mod_key=KEY,entry=n,methods=sorted(v)) for n,v in sorted(wanted.items())]);write_json(OUT/'cataclysm-remaining-status-usages.json',u);write_json(OUT/'native-specifications/cataclysm-remaining-status.json',s);write_json(OUT/'native-evidence/cataclysm-remaining-status.json',collect(s))
    a=dict(read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'][0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/entity/LivingEntity.class':['removeEffectNoUpdate','addEffect','onEffectAdded','onEffectRemoved','isSensitiveToWater'],'net/minecraft/world/effect/MobEffect.class':['addAttributeModifiers','removeAttributeModifiers','applyEffectTick'],'net/minecraft/world/effect/MobEffect$AttributeTemplate.class':['create']}
    r=dict(id='cataclysm-remaining-status-244',scope='Native raw effect replacement and attribute cleanup, base inert tick and water sensitivity.',archives=[a]);write_json(OUT/'reference-specifications/cataclysm-remaining-status-244.json',r);write_json(OUT/'reference-evidence/cataclysm-remaining-status-244.json',reference_collect(r,source_aids=True));print('Remaining status methods',len(u['rows']),'native witnesses',len(wanted))

if __name__=='__main__':save()
