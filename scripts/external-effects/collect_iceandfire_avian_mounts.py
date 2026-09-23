from catalog_common import *
from classfile import ClassFile
from native_evidence import collect
from collect_iceandfire_foundation import IAF,targets
CLASSES=['entity/StymphalianBirdEntity','entity/StymphalianFeatherEntity','entity/StymphalianArrowEntity','entity/AmphithereEntity','entity/AmphithereArrowEntity','entity/HippogryphEntity','entity/HippocampusEntity','entity/util/StymphalianBirdFlock','entity/ai/StymphalianBirdAIFleeGoal','entity/ai/StymphalianBirdAITargetGoal','entity/ai/AmphithereAIAttackMeleeGoal','entity/ai/AmphithereAITargetItemsGoal','entity/ai/HippogryphAITargetItemsGoal','entity/ai/HippogryphAITargetGoal','item/StymphalianFeatherBundleItem','item/tool/StymphalianDaggerItem','item/tool/StymphalianArrowItem','item/tool/AmphithereArrowItem','item/tool/AmphithereMacuahuitlItem']
def census():
    t=targets()['iceandfire'];rows=[]
    with zipfile.ZipFile(t['path']) as z:
        for entry in sorted(n for n in z.namelist() if n.endswith('.class') and any(s in n for s in ['Stymphalian','Amphithere','Hippogryph','Hippocampus'])):
            c=ClassFile(z.read(entry))
            for m in c.methods:
                hits=[i for i in c.instructions(m.get('code',b'')) if any(s in str(i.get('operand','')) for s in ['.hurt(','.heal(','.addEffect(','.setTarget(','.setVictor(','.tame('])]
                if hits:rows.append(dict(entry=entry,method=m['name'],descriptor=m['descriptor'],hits=hits))
    return dict(jar_sha256=t['sha256'],rows=rows,scope='Avian/mount combat/status/target callers; egg0damage route classified separately in final equipment closure.')
def save():
    with zipfile.ZipFile(targets()['iceandfire']['path']) as z:rows=[dict(id='iaf:avian-mounts:'+s,mod_key='iceandfire',entry=IAF+s+'.class',methods=sorted({m['name'] for m in ClassFile(z.read(IAF+s+'.class')).methods})) for s in CLASSES]
    s=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,scope='Avian and combat-special mounts; ordinary utility excluded.',evidence_specifications=rows)
    write_json(OUT/'native-specifications/iceandfire-avian-mounts.json',s);write_json(OUT/'native-evidence/iceandfire-avian-mounts.json',collect(s));write_json(OUT/'iceandfire-avian-mounts-census.json',census())
    print('Avian/mount witnesses saved')
if __name__=='__main__':save()
