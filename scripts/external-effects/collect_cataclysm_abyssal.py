from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from selected_reference import collect as reference_collect
from collect_cataclysm_foundation import targets,KEY,PKG

FIELDS=['EFFECTABYSSAL_BURN','EFFECTABYSSAL_CURSE']
def usages():
    t=targets()[KEY];rows=[];damage=[]
    with zipfile.ZipFile(t['path']) as z:
        for n in sorted(z.namelist()):
            if not n.endswith('.class'):continue
            c=ClassFile(z.read(n))
            for m in c.methods:
                ins=list(c.instructions(m.get('code',b'')));base=dict(entry=n,method=m['name'],descriptor=m['descriptor'],code_sha256=byte_hash(m.get('code',b'')))
                hits=[i for i in ins if i['opcode']=='0xb2' and any('ModEffect.'+f+'L' in str(i.get('operand','')) for f in FIELDS)]
                if hits:rows.append(dict(**base,hits=hits))
                hits=[i for i in ins if i['opcode']=='0xb2' and 'CMDamageTypes.ABYSSAL_BURNL' in str(i.get('operand',''))]
                if hits:damage.append(dict(**base,hits=hits))
    return dict(schema='tno.external_effects.cataclysm_abyssal_usages.v1',jar_sha256=t['sha256'],fields=FIELDS,rows=rows,damage_callers=damage)

def save():
    u=usages();wanted={};t=targets()[KEY]
    for r in u['rows']+u['damage_callers']:wanted.setdefault(r['entry'],set()).add(r['method'])
    with zipfile.ZipFile(t['path']) as z:
        for short in ['effects/EffectAbyssal_Burn','effects/EffectAbyssal_Curse']:
            n=PKG+short+'.class';wanted[n]={m['name'] for m in ClassFile(z.read(n)).methods}
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Both abyssal status DOTs, native teleport, stacking/application and concrete status filter slices; full originating attack families pending.',evidence_specifications=[dict(id='cataclysm:abyssal:'+n,mod_key=KEY,entry=n,methods=sorted(v)) for n,v in sorted(wanted.items())]);write_json(OUT/'cataclysm-abyssal-usages.json',u);write_json(OUT/'native-specifications/cataclysm-abyssal.json',s);write_json(OUT/'native-evidence/cataclysm-abyssal.json',collect(s))
    originals=read_json(OUT/'reference-specifications/vv-loader-244.json')['archives'];a=dict(originals[0]);a.pop('semantic_review',None);a['classes']={'net/minecraft/world/entity/LivingEntity.class':['removeEffectNoUpdate','addEffect','getDamageAfterMagicAbsorb']}
    b=dict(originals[1]);b.pop('semantic_review',None);b['classes']={'net/neoforged/neoforge/event/entity/EntityTeleportEvent.class':['*'],'net/neoforged/neoforge/event/entity/EntityTeleportEvent$ChorusFruit.class':['*']}
    r=dict(id='cataclysm-abyssal-244',scope='Raw effect removal versus admission and native teleport-event construction; no inferred bus publication.',archives=[a,b]);write_json(OUT/'reference-specifications/cataclysm-abyssal-244.json',r);write_json(OUT/'reference-evidence/cataclysm-abyssal-244.json',reference_collect(r,source_aids=True));print('Abyssal usages',len(u['rows']),'damage callers',len(u['damage_callers']),'native witnesses',len(wanted))

if __name__=='__main__':save()
