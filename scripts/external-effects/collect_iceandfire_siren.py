"""Pin Siren song state and actual status producer; separate flute read-ahead."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from collect_iceandfire_foundation import IAF,targets

FULL=['entity/SirenEntity','effect/SirenCharmStatusEffect','render/SirenShaderRenderHelper','config/IafCommonConfig$SirenConfig']

def census():
    result=[]
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        classes=0;legacy=[]
        for entry in z.namelist():
            if not entry.endswith('.class'):continue
            classes+=1
            if 'SirenData' in entry:legacy.append(entry)
            c=ClassFile(z.read(entry))
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(k in str(i.get('operand')) for k in ['IafStatusEffects.SIREN_CHARM','SirenEntity.charmingEntities','SirenEntity.tickCharm(','SirenEntity.stopCharm(','SirenEntity.isWearingEarplugs(','MiscData.setLoveTicks('])]
                if hits:result.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
    return dict(schema='tno.external_effects.iaf_siren_callers.v1',jar_sha256=targets()['iceandfire']['sha256'],parsed_classes=classes,siren_data_classes=legacy,rows=result)

def save():
    rows=[]
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:
        for short in FULL:
            c=ClassFile(z.read(IAF+short+'.class'));rows.append(dict(id='iaf:siren:'+short,mod_key='iceandfire',entry=IAF+short+'.class',methods=sorted({m['name'] for m in c.methods})))
    rows.append(dict(id='iaf:siren:stone-check',mod_key='iceandfire',entry=IAF+'entity/GorgonEntity.class',methods=['isStoneMob']))
    rows.append(dict(id='iaf:siren:prey-tag',mod_key='iceandfire',entry='data/iceandfire/tags/entity_type/siren_charmable.json'))
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Siren song/charm state and marker; entity class availability does not complete unrelated melee/AI/render behavior.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-siren.json',s);write_json(OUT/'native-evidence/iceandfire-siren.json',collect(s));write_json(OUT/'iceandfire-siren-callers.json',census())
    print('Siren witnesses saved:',len(rows))

if __name__=='__main__':save()
